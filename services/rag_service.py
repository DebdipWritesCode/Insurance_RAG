from services.vector_store import embed_and_upsert, retrieve_from_kb, split_text
from services.pdf_parser import extract_text_from_pdf
from services.gpt_client import ask_gpt
import uuid
import tempfile
import aiohttp
import asyncio

async def download_pdf_to_temp_file(pdf_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(pdf_url) as response:
            if response.status != 200:
                raise Exception(f"Failed to download PDF. Status: {response.status}")
            content = await response.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(content)
                return tmp.name

async def process_documents_and_questions(pdf_url: str, questions: list[str]) -> dict:
    print(f"Processing documents from URL: {pdf_url}")
    
    # Step 1: Download PDF and extract text
    local_pdf_path = await download_pdf_to_temp_file(pdf_url)
    raw_text_output = extract_text_from_pdf(local_pdf_path)

    # Normalize: ensure we get a single string
    raw_text = "\n".join(raw_text_output) if isinstance(raw_text_output, list) else raw_text_output
    print(f"📄 Extracted {len(raw_text)} characters from PDF")

    # Step 2: Split text into chunks
    chunks = split_text(raw_text)
    print(f"🧾 Extracted {len(chunks)} chunks from PDF")
    if chunks:
        print(f"🔹 First chunk (length={len(chunks[0])}): {repr(chunks[0][:100])}...")
    usable_chunks = [c for c in chunks if len(c.strip()) > 50]
    print(f"✅ Usable chunks (>50 chars): {len(usable_chunks)}")

    # Step 3: Generate a unique agent/namespace
    agent_id = str(uuid.uuid4())

    # Step 4: Store chunks in Pinecone under this agent_id
    embed_and_upsert(usable_chunks, agent_id)

    # Step 5: Run questions through retrieval + GPT
    results = {}
    print(f"🧠 Processing {len(questions)} questions...")

    for question in questions:
        retrieval_input = {
            "query": question,
            "agent_id": agent_id,
            "top_k": 5
        }
        print(f"🔍 Retrieving context for question: {question}")
        retrieved = await retrieve_from_kb(retrieval_input)
        retrieved_chunks = retrieved.get("chunks", [])
        print(f"📚 Retrieved {len(retrieved_chunks)} chunks for question: {question}")
        context = "\n".join(retrieved_chunks)

        if not context.strip():
            results[question] = "Sorry, I couldn't find relevant information."
            continue
        
        print(f"✏️ Context preview: {context[:100]}...")
        answer = ask_gpt(context, question)
        results[question] = answer

    return results
