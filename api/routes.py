
from fastapi import APIRouter, HTTPException, Depends
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

@router.post("/hackrx/run", response_model=HackRxResponse)
async def run_rag_endpoint(payload: HackRxRequest, db: Session = Depends(get_db)):
    try:
        results = await process_documents_and_questions(
            pdf_url=str(payload.documents),
            questions=payload.questions,
            db=db
        )
        return {"answers": list(results.values())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
