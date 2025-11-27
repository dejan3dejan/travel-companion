from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AI Travel Companion API", version="0.1.0")

class HealthCheck(BaseModel):
    status: str = "ok"

@app.get("/")
async def root():
    return {"message": "Travel Companion API is running"}

@app.get("/health", response_model=HealthCheck)
async def health_check():
    return HealthCheck(status="healthy")

