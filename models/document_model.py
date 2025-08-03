from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value, info):
        if not ObjectId.is_valid(value):
            raise ValueError("Invalid ObjectId")
        return ObjectId(value)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")

class QAPair(BaseModel):
    question: str
    answer: str

class DocumentModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    document_url: HttpUrl
    questions: List[str]
    qa_pairs: List[QAPair]

    model_config = ConfigDict(
        validate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "document_url": "https://example.com/document.pdf",
                "questions": [
                    "What is the document about?",
                    "Who is the author?"
                ],
                "qa_pairs": [
                    {"question": "What is the document about?", "answer": "It's about AI in education."},
                    {"question": "Who is the author?", "answer": "John Doe"}
                ]
            }
        }
    )
