from typing import List
from pinecone import Pinecone
from sqlalchemy.orm import Session
from services.vector_store import embed_and_upsert, retrieve_from_kb, split_text, embed_text_batch
from services.parser.pdf_parser import extract_text_from_pdf
from services.parser.word_parser import extract_text_from_docx
from services.parser.ppt_parser import extract_text_from_pptx
from services.parser.excel_parser import extract_text_from_xlsx
from services.parser.image_parser import extract_text_from_image
from services.parser.txt_parser import extract_text_from_txt
from services.gpt_client import ask_gpt
import re
import tempfile
import aiohttp
import asyncio
from config.settings import settings
from config.mime_types import MIME_EXTENSION_MAP
# from logs.logs import add_logs
import hashlib
from services.document_db_service import (
    find_answers_in_db,
    append_qa_pairs,
    QAPair,
    create_document,
    get_document_by_url,
    update_document,
    get_all_documents,
)

pc = Pinecone(
  api_key=settings.PINECONE_API_KEY
)
pinecone_index = pc.Index(settings.PINECONE_INDEX_NAME)

def generate_namespace_from_url(url: str) -> str:
    return re.sub(r'\W+', '_', url).strip('_').lower()

async def download_file_to_temp(file_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download file. Status: {response.status}")
            content = await response.read()
            
            content_type = response.headers.get("Content-Type", "")
            ext = MIME_EXTENSION_MAP.get(content_type)
            
            if not ext:
                raise Exception(f"Unsupported or unknown Content-Type: {content_type}")

            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(content)
                return tmp.name, content_type

def parse_document_by_type(file_path: str, mime_type: str) -> str:
    if mime_type == "application/pdf":
        return extract_text_from_pdf(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_text_from_docx(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation":
        return extract_text_from_pptx(file_path)
    elif mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        return extract_text_from_xlsx(file_path)
    elif mime_type in ["image/jpeg", "image/png"]:
        return extract_text_from_image(file_path)
    elif mime_type == "text/plain":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {mime_type}")

async def process_documents_and_questions(document_url: str, questions: List[str]) -> dict:
    print(f"Processing documents from URL: {document_url}")
    print(f"Received questions: {questions}")

    existing_doc = await get_document_by_url(document_url)
    if not existing_doc:
        print(f"🆕 Creating document record in MongoDB for URL: {document_url}")
        await create_document({
            "document_url": document_url,
            "questions": [],
            "qa_pairs": []
        })
    else:
        print(f"📄 Document already exists in MongoDB")

    agent_id = generate_namespace_from_url(document_url)
    existing_namespaces = pinecone_index.describe_index_stats().namespaces.keys()

    if agent_id not in existing_namespaces:
        print(f"🆕 Namespace '{agent_id}' not found. Proceeding with download and embedding...")

        local_file_path, content_type = await download_file_to_temp(document_url)
        raw_text_output = parse_document_by_type(local_file_path, content_type)
        raw_text = "\n".join(raw_text_output) if isinstance(raw_text_output, list) else raw_text_output
        print(f"📄 Extracted {len(raw_text)} characters from document")

        chunks = split_text(raw_text)
        print(f"🧾 Extracted {len(chunks)} chunks from PDF")
        usable_chunks = [c for c in chunks if len(c.strip()) > 50]
        print(f"✅ Usable chunks (> 50 chars): {len(usable_chunks)}")

        await embed_and_upsert(usable_chunks, agent_id)
    else:
        print(f"📂 Namespace '{agent_id}' already exists. Skipping download and embedding.")

    # Step 1: Check existing answers in MongoDB
    existing_answers = await find_answers_in_db(document_url, questions)
    unanswered_questions = [q for q in questions if q not in existing_answers]

    print(f"Found {len(existing_answers)} answers in DB")
    print(f"{len(unanswered_questions)} questions to process further")

    semaphore = asyncio.Semaphore(15)

    async def process_question(index: int, question: str) -> tuple[int, str, str]:
        async with semaphore:
            for attempt in range(3):
                try:
                    question_cached_namespace = f"question_cached_{agent_id}"
                    
                    question_vector = await embed_text_batch([question])
                    if not question_vector or not question_vector[0]:
                        raise ValueError("Failed to embed question")

                    # Step 2: Check Pinecone
                    cache_result = pinecone_index.query(
                        vector=question_vector[0],
                        namespace=question_cached_namespace,
                        top_k=1,
                        include_metadata=True
                    )

                    if cache_result.matches and cache_result.matches[0].score > 0.9:
                        cached_answer = cache_result.matches[0].metadata.get("answer", "")
                        print(f"✅ Q{index}: Semantic cache hit")
                        
                        # Save to MongoDB
                        await append_qa_pairs(document_url, [QAPair(question=question, answer=cached_answer)])

                        return (index, question, cached_answer)

                    # Step 3: Retrieve context and ask GPT
                    print(f"Q{index}: No semantic match found, querying GPT")
                    retrieved = await retrieve_from_kb({"query": question, "agent_id": agent_id, "top_k": 3})
                    retrieved_chunks = retrieved.get("chunks", [])

                    if not retrieved_chunks:
                        raise ValueError("No chunks retrieved")

                    max_context_chars = 3000
                    context = "\n".join(retrieved_chunks)[:max_context_chars]

                    answer = await ask_gpt(context, question)

                    # Cache in Pinecone
                    hash_digest = hashlib.sha256(question.encode()).hexdigest()[:12]
                    vector_id = f"q_{hash_digest}_{agent_id}"
                    pinecone_index.upsert(
                        vectors=[{
                            "id": vector_id,
                            "values": question_vector[0],
                            "metadata": {"question": question, "answer": answer}
                        }],
                        namespace=question_cached_namespace
                    )

                    # Save in MongoDB
                    await append_qa_pairs(document_url, [QAPair(question=question, answer=answer)])

                    return (index, question, answer)

                except Exception as e:
                    print(f"⚠️ Q{index}: Attempt {attempt + 1} failed with error: {e}")

            return (index, question, "Sorry, I couldn't find relevant information.")

    print(f"🧠 Processing {len(unanswered_questions)} unanswered questions...")
    tasks = [asyncio.create_task(process_question(i, q)) for i, q in enumerate(unanswered_questions)]
    responses = await asyncio.gather(*tasks)

    new_answers = {q: ans for _, q, ans in sorted(responses)}
    all_answers = existing_answers | new_answers

    # Optionally log: add_logs(pdf_url, all_answers)

    return all_answers

async def clear_qa_caches():
    print("🧹 Starting cache cleanup process...")

    all_documents = await get_all_documents()
    if not all_documents:
        print("❌ No documents found in DB.")
        return

    for doc in all_documents:
        pdf_url = doc.document_url
        if not pdf_url:
            continue

        print(f"\n🧾 Processing document: {pdf_url}")
        agent_id = generate_namespace_from_url(str(pdf_url))
        question_namespace = f"question_cached_{agent_id}"

        print("🗑️ Clearing QA pairs from MongoDB...")
        await update_document(str(pdf_url), {
            "qa_pairs": [],
            "questions": []
        })

        try:
            print(f"🗑️ Deleting namespace '{question_namespace}' from Pinecone...")
            pinecone_index.delete(delete_all=True, namespace=question_namespace)
        except Exception as e:
            print(f"⚠️ Failed to delete Pinecone namespace {question_namespace}: {e}")

    print("\n✅ Finished clearing all QA caches.")
