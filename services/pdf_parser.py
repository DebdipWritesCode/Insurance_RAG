import pdfplumber
import httpx
import tempfile
from asyncio import Semaphore
import asyncio

MAX_CONCURRENT_TASKS = 30
BATCH_SIZE = 20

async def download_pdf(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_file.write(response.content)
            print(f"✅ Downloaded PDF to: {temp_file.name}")
            return temp_file.name

def extract_text_from_pdf(pdf_path: str) -> list[str]:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text += text + "\n"
            else:
                print(f"⚠️ No text found on page {i+1}")

    chunks = [chunk.strip() for chunk in full_text.split("\n\n") if chunk.strip()]
    
    print(f"📄 Extracted {len(chunks)} chunks from PDF using pdfplumber")
    print(f"🔍 First chunk (100 chars): {repr(chunks[0][:100]) if chunks else 'No chunks'}")
    
    return chunks

# async def extract_text_from_pdf(pdf_path: str) -> list[str]:
#     semaphore = Semaphore(MAX_CONCURRENT_TASKS)
    
#     with pdfplumber.open(pdf_path) as pdf:
#         pages = pdf.pages
        
#         async def process_page_batch(start_idx: int, end_idx: int):
#             async with semaphore:
#                 def read_batch():
#                     batch_text = ""
#                     for i in range(start_idx, end_idx):
#                         try:
#                             page = pages[i]
#                             text = page.extract_text()
#                             if text:
#                                 batch_text += text + "\n"
#                             else:
#                                 print(f"⚠️ No text found on page {i+1}")
#                         except Exception as e:
#                             print(f"❌ Error processing page {i+1}: {e}")
#                     return batch_text
#                 return await asyncio.to_thread(read_batch)
        
#         tasks = []
#         for i in range(0, len(pages), BATCH_SIZE):
#             tasks.append(
#                 process_page_batch(
#                     i, min(i + BATCH_SIZE, len(pages))
#                 )
#             )
        
#         batch_texts = await asyncio.gather(*tasks)
#         full_text = "\n".join(batch_texts)
    
#     chunked = [chunk.strip() for chunk in full_text.split("\n\n") if chunk.strip()]
#     print(f"📄 Extracted {len(chunked)} chunks from PDF using pdfplumber")
#     print(f"🔍 First chunk (100 chars): {repr(chunked[0][:100]) if chunked else 'No chunks'}")

#     return chunked