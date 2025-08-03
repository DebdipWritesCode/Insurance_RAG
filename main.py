from fastapi import FastAPI
from api.routes import router as hackrx
from db.client import init_indexes

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await init_indexes()

app.include_router(hackrx)

@app.get("/")
def health_check():
    return {"status": "ok"}
