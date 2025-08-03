from pymongo.errors import DuplicateKeyError
from typing import List
from bson import ObjectId
from models.document_model import DocumentModel, QAPair
from db.client import db

document_collection = db["documents"]

async def create_document(document_data: dict) -> DocumentModel:
    try:
        result = await document_collection.insert_one(document_data)
        document = await document_collection.find_one({"_id": result.inserted_id})
        return DocumentModel(**document)
    except DuplicateKeyError:
        raise ValueError("Document with this URL already exists")

async def get_document_by_id(doc_id: str) -> DocumentModel:
    document = await document_collection.find_one({"_id": ObjectId(doc_id)})
    return DocumentModel(**document) if document else None

async def get_document_by_url(document_url: str) -> DocumentModel:
    document = await document_collection.find_one({"document_url": document_url})
    return DocumentModel(**document) if document else None

async def append_questions(document_url: str, new_questions: List[str]) -> DocumentModel:
    doc = await get_document_by_url(document_url)
    if not doc:
        raise ValueError("Document not found")

    existing_questions_set = {q.strip().lower() for q in doc.questions}
    filtered_questions = [q for q in new_questions if q.strip().lower() not in existing_questions_set]

    if not filtered_questions:
        return doc

    await document_collection.update_one(
        {"document_url": document_url},
        {"$push": {"questions": {"$each": filtered_questions}}}
    )

    return await get_document_by_url(document_url)

async def append_qa_pairs(document_url: str, new_pairs: List[QAPair]) -> DocumentModel:
    doc = await get_document_by_url(document_url)
    if not doc:
        raise ValueError("Document not found")

    existing_questions_set = {pair.question.strip().lower() for pair in doc.qa_pairs}
    filtered_pairs = [pair for pair in new_pairs if pair.question.strip().lower() not in existing_questions_set]

    if not filtered_pairs:
        return doc

    formatted_pairs = [pair.dict() for pair in filtered_pairs]

    await document_collection.update_one(
        {"document_url": document_url},
        {"$push": {"qa_pairs": {"$each": formatted_pairs}}}
    )

    return await get_document_by_url(document_url)

async def find_answers_in_db(document_url: str, questions: List[str]) -> dict[str, str]:
    """
    Given a document URL and a list of questions, return a dict of {question: answer}
    for any that are found in the document's qa_pairs.
    """
    doc = await get_document_by_url(document_url)
    if not doc:
        return {}

    normalized_question_map = {q.strip().lower(): q for q in questions}
    found_answers = {}

    existing_qapairs_map = {
        pair.question.strip().lower(): pair.answer
        for pair in doc.qa_pairs
    }

    for norm_q, original_q in normalized_question_map.items():
        if norm_q in existing_qapairs_map:
            found_answers[original_q] = existing_qapairs_map[norm_q]

    return found_answers
