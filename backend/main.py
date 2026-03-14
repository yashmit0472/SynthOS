from fastapi import FastAPI
from contextlib import asynccontextmanager
from backend.orchestrator import handle_query
from backend.background import start_scheduler

scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global scheduler
    scheduler = start_scheduler()
    yield
    # Shutdown
    if scheduler:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def root():
    return {"message": "AI OS Running"}

@app.post("/query")
def process_query(data: dict):
    return handle_query(data["question"])