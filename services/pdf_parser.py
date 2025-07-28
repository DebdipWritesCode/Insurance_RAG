import fitz
import httpx
import tempfile

async def download_pdf(url: str) -> str:
    async with httpx.AsyncClient() as client:
      response = await client.get(url)
      response.raise_for_status()
      
      with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(response.content)
        return temp_file.name
      
def extract_text_from_pdf(pdf_path: str) -> str:
  text = ""
  with fitz.open(pdf_path) as doc:
    for page in doc:
      text += page.get_text()
  return text