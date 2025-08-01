from sqlalchemy import Column, Integer, Text, DateTime, func, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class QuestionAnswer(Base):
    __tablename__ = "qa_logs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    document_id = Column(Integer, ForeignKey('documents.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('question', 'document_id', name='uq_question_doc'),
    )
