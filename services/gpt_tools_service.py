import aiohttp
from services.search_api import serper_search

async def search_tool(query: str) -> str:
  """Uses Serper API to search the Web"""
  return serper_search(query)

async def request_fetch_tool(url: str) -> str:
  """Fetch the raw content of given url via GET request"""
  async with aiohttp.ClientSession() as session:
    async with session.get(url) as response:
      return await response.text()
    
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Search the web using Serper API",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query text"}
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "request_fetch",
            "description": "Fetch the content of a given URL",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch via GET"}
                },
                "required": ["url"],
            },
        },
    },
]