from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os

# We import our new optimized pipeline
# This replaces the manual loop you had before
from services.ingest import run_ingestion
from models.vector_store import reset_db, list_documents
from models.rag import ask

app = FastAPI(title="DevDocs AI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Models ----------

class IndexRequest(BaseModel):
    path: str

class Question(BaseModel):
    question: str

# ---------- Routes ----------

@app.post("/index")
async def index_docs(request: IndexRequest, background_tasks: BackgroundTasks):
    """
    Index documents from a folder path.
    Top 1% Improvement: Uses BackgroundTasks.
    Instead of making the user wait for 5 minutes, we return immediately
    and let the server process the files in the background.
    """
    if not os.path.exists(request.path):
        raise HTTPException(status_code=400, detail="Path does not exist")

    # Add the heavy function to the background queue
    background_tasks.add_task(run_ingestion, request.path)

    return {
        "message": "Indexing started in the background.", 
        "path": request.path,
        "note": "Check server logs for progress."
    }

@app.post("/ask")
async def ask_question(body: Question):
    """
    Ask a question.
    Top 1% Improvement: Async/Await allows handling multiple users at once.
    """
    # We must await the async function from rag.py
    response = await ask(body.question)
    return response

@app.post("/reset")
def reset():
    """
    Completely reset the vector database.
    """
    reset_db()
    return {"message": "Database reset successfully"}

@app.get("/documents")
def documents():
    """
    List indexed documents and chunk counts.
    """
    return list_documents()

@app.get("/health")
def health():
    """Simple health check for production monitoring."""
    return {"status": "ok"}
