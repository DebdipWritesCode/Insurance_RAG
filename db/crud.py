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

def get_or_create_document(db: Session, url: str):
    doc = db.query(models.Document).filter_by(url=url).first()
    if doc:
        return doc
    return create_document(db, url)

def create_question_entry(db: Session, question: str, document_id: int):
    existing = db.query(models.QuestionAnswer).filter_by(question=question, document_id=document_id).first()
    if existing:
        return existing
    qa = models.QuestionAnswer(question=question, answer=None, document_id=document_id)
    db.add(qa)
    db.commit()
    db.refresh(qa)
    return qa

def update_answer(db: Session, question: str, document_id: int, answer: str):
    qa = db.query(models.QuestionAnswer).filter_by(question=question, document_id=document_id).first()
    if qa:
        qa.answer = answer
        db.commit()
        db.refresh(qa)
        return qa
    return None