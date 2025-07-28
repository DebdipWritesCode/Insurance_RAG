from fastapi import FastAPI
from api.routes import router as hackrx

app = FastAPI()

app.include_router(hackrx)

print("✅ Loaded hackrx routes")

@app.get("/")
def health_check():
    return {"status": "ok"}
