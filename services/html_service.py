import aiohttp
import asyncio
from bs4 import BeautifulSoup
from services.gpt_client import ask_gpt

async def fetch_html_content(url: str) -> str:
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      if response.status != 200:
        raise Exception(f"Failed to fetch HTML content from {url}. Status code: {response.status}")
      return await response.text()
    
def clean_html_text(html: str) -> str:
  soup = BeautifulSoup(html, 'html.parser')
  
  for tag in soup(['script', 'style', "noscript"]):
    tag.extract()
    
  text_parts = []
  for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', "li", "div"]):
    content = tag.get_text(strip=True)
    if content:
      text_parts.append(content)
      
  return "\n".join(text_parts)

async def process_html_and_questions(html_url: str, questions: list[str]) -> dict:
  print(f"🌐 Processing HTML from: {html_url}")
  html_content = await fetch_html_content(html_url)
  cleaned_text = clean_html_text(html_content)
  
  max_context_chars = 3000
  context = "Here is the cleaned text or the contents of the link, now answer the following question. You do not need to go to the link, just answer by looking at this context\n\n"
  context += cleaned_text[:max_context_chars]

  semaphore = asyncio.Semaphore(10)

  async def process_question(index: int, question: str) -> tuple[int, str, str]:
      async with semaphore:
          try:
              answer = await ask_gpt(context, question)
              return (index, question, answer)
          except Exception as e:
              print(f"⚠️ Error processing Q{index}: {e}")
              return (index, question, "Sorry, I couldn't find relevant information.")

  tasks = [asyncio.create_task(process_question(i, q)) for i, q in enumerate(questions)]
  responses = await asyncio.gather(*tasks)

  return {q: ans for _, q, ans in sorted(responses)}