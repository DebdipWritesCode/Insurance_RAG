from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
    PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
    PINECONE_HOST_NAME = os.getenv("PINECONE_HOST_NAME")
    DATABASE_URL = os.getenv("DATABASE_URL")
    EXPECTED_TOKEN = os.getenv("EXPECTED_TOKEN")

settings = Settings()