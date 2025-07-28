from sqlalchemy.orm import Session
from . import models

def create_document(db: Session, url: str):
    doc = models.Document(url=url)
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def log_question_answer(db: Session, question: str, answer: str, document_id: int):
    qa = models.QuestionAnswer(question=question, answer=answer, document_id=document_id)
    db.add(qa)
    db.commit()
    db.refresh(qa)
    return qa
