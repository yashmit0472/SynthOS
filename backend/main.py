from fastapi import FastAPI
from backend.orchestrator import handle_query

app = FastAPI()

@app.get("/")
def root():
    return {"message": "AI OS Running"}

@app.post("/query")
def process_query(data: dict):
    return handle_query(data["question"])