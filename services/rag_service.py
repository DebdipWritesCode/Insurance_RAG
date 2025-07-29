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

    # Step 4: Store chunks in vector DB
    await embed_and_upsert(usable_chunks, agent_id)

    # Step 4.5: Give the index some time to become searchable
    await asyncio.sleep(2)

    # Step 5: Retry logic while preserving order
    print(f"🧠 Processing {len(questions)} questions with retry logic...")
    max_retries = 3
    queue = [(i, q, 0) for i, q in enumerate(questions)]  # (original_index, question, attempt_count)
    results = [None] * len(questions)

    while queue:
        i, question, attempt = queue.pop(0)
        print(f"🔍 Attempting question [{i}]: {question} (Attempt {attempt + 1})")

        retrieval_input = {
            "query": question,
            "agent_id": agent_id,
            "top_k": 5
        }
        retrieved = await retrieve_from_kb(retrieval_input)
        retrieved_chunks = retrieved.get("chunks", [])
        print(f"📚 Retrieved {len(retrieved_chunks)} chunks for question [{i}]")

        if not retrieved_chunks:
            if attempt < max_retries - 1:
                print(f"🔁 Requeuing question [{i}] due to 0 chunks...")
                queue.append((i, question, attempt + 1))
                await asyncio.sleep(1)  # small delay before retry
            else:
                print(f"❌ Max retries reached for question [{i}]")
                results[i] = "Sorry, I couldn't find relevant information."
            continue

        context = "\n".join(retrieved_chunks)
        print(f"✏️ Context preview for question [{i}]: {context[:100]}...")
        answer = ask_gpt(context, question)
        results[i] = answer

    return {questions[i]: results[i] for i in range(len(questions))}
