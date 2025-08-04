from serpapi import GoogleSearch
from config.settings import settings

def serper_search(query: str) -> str:
    params = {
        "q": query,
        "hl": "en",
        "gl": "in",
        "google_domain": "google.com",
        "api_key": settings.SERPAPI_API_KEY,
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    try:
        snippet = results["organic_results"][0]["snippet"]
        return snippet
    except (KeyError, IndexError):
        return "No relevant results found."
