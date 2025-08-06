import requests
from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, HttpUrl
from typing import List

from services.rag_service import process_documents_and_questions, clear_qa_caches

from config.settings import settings

router = APIRouter()

class HackRxRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

@router.post("/hackrx/run", response_model=HackRxResponse)
async def run_rag_endpoint(
    payload: HackRxRequest,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")

    token = authorization.split(" ")[1]
    if token != settings.EXPECTED_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        try:
            head_response = requests.head(str(payload.documents), allow_redirects=True, timeout=5)
            content_type = head_response.headers.get("Content-Type", "")
            print(f"Content-Type of the document: {content_type}")
        except Exception as head_err:
            return {"answers": ["Sorry, I cannot access this type of document."]}
        
        if content_type == "application/zip":
            return {"answers": ["Sorry, this zip file contains files that I cannot process."]}

        results = await process_documents_and_questions(
            document_url=str(payload.documents),
            questions=payload.questions,
        )
        return {"answers": list(results.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/hackrx/clear-cache")
async def clear_cache_endpoint(
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")

    token = authorization.split(" ")[1]
    if token != settings.EXPECTED_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        await clear_qa_caches()
        return {"message": "QA cache cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear QA caches: {e}")