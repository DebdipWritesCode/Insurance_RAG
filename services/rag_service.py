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
    raw_text = "\n".join(raw_text_output) if isinstance(raw_text_output, list) else raw_text_output
    print(f"📄 Extracted {len(raw_text)} characters from PDF")

    # Step 2: Split text
    chunks = split_text(raw_text)
    print(f"🧾 Extracted {len(chunks)} chunks from PDF")
    usable_chunks = [c for c in chunks if len(c.strip()) > 50]
    print(f"✅ Usable chunks (>50 chars): {len(usable_chunks)}")

    # Step 3: Embed into vector DB
    agent_id = str(uuid.uuid4())
    await embed_and_upsert(usable_chunks, agent_id)

    # Step 4: Parallel processing of retrieval + GPT
    semaphore = asyncio.Semaphore(10)  # Limit concurrency (adjust based on LLM rate limits)

    async def process_question(index: int, question: str) -> tuple[int, str, str]:
        async with semaphore:
            for attempt in range(3):
                try:
                    retrieval_input = {"query": question, "agent_id": agent_id, "top_k": 3}  # Reduced top_k
                    retrieved = await retrieve_from_kb(retrieval_input)
                    retrieved_chunks = retrieved.get("chunks", [])
                    if not retrieved_chunks:
                        raise ValueError("No chunks retrieved")

                    max_context_chars = 3000  # Tune this (e.g., 2000–3000)
                    context = "\n".join(retrieved_chunks)[:max_context_chars]
                    if len(context) > 3000:  # Limit context length
                        context = context[:3000]
                    print(f"✏️ Q{index}: Context preview: {context[:100]}...")
                    answer = await ask_gpt(context, question)
                    return (index, question, answer)
                except Exception as e:
                    print(f"⚠️ Q{index}: Attempt {attempt + 1} failed with error: {e}")
                    await asyncio.sleep(1)
            return (index, question, "Sorry, I couldn't find relevant information.")

    print(f"🧠 Parallel processing {len(questions)} questions...")
    tasks = [asyncio.create_task(process_question(i, q)) for i, q in enumerate(questions)]
    responses = await asyncio.gather(*tasks)

    # Step 5: Preserve question order
    results = {q: ans for _, q, ans in sorted(responses)}
    return results
