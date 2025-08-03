from motor.motor_asyncio import AsyncIOMotorClient
from config.settings import settings

client = AsyncIOMotorClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]

async def init_indexes():
  await db.documents.create_index("document_url", unique=True)