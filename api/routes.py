
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, HttpUrl
from typing import List
from services.rag_service import process_documents_and_questions

router = APIRouter()

class HackRxRequest(BaseModel):
    documents: HttpUrl
    questions: List[str]

class HackRxResponse(BaseModel):
    answers: List[str]

@router.post("/hackrx/run", response_model=HackRxResponse)
async def run_rag_endpoint(payload: HackRxRequest):
    try:
        # Log the incoming request details
        print("Received RAG request:")
        print(f"Document URL: {payload.documents}")
        print(f"Questions: {payload.questions}")

        # --- Commenting out the RAG logic for testing purposes ---
        # print(f"Processing documents from URL: {payload.documents}")
        # results = await process_documents_and_questions(
        #     pdf_url=str(payload.documents),
        #     questions=payload.questions
        # )
        # return {"answers": list(results.values())}

        # Dummy response for testing
        return {"answers": []}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
