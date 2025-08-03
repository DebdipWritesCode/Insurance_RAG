
from fastapi import APIRouter, HTTPException, Header, status
from pydantic import BaseModel, HttpUrl
from typing import List

from sqlalchemy.orm import Session
from services.rag_service import process_documents_and_questions
from .deps import get_db

router = APIRouter()

class HackRxRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]
    
EXPECTED_TOKEN = "caef429214c660d704b2a640f23e760a77434c1e93eb914f19f08e00228d239d"

@router.post("/hackrx/run", response_model=HackRxResponse)
async def run_rag_endpoint(
    payload: HackRxRequest,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid authorization header")

    token = authorization.split(" ")[1]
    if token != EXPECTED_TOKEN:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    try:
        results = await process_documents_and_questions(
            pdf_url=str(payload.documents),
            questions=payload.questions,
        )
        return {"answers": list(results.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))