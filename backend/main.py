from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import uvicorn
import uuid

from utils.pdf_loader import get_pdf_text, get_text_chunks, build_vector_store
from utils.qa_chain import ask_question
from utils.summarizer import summarize_document
from utils.quiz_generator import generate_quiz
from utils.llm_loader import load_llm

app = FastAPI(title="INFOMINE API")

# Enable CORS for the vanilla JS frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for simplicity (like Streamlit session state)
# In a real app, you'd use a database and distributed cache
sessions = {}

class ChatRequest(BaseModel):
    session_id: str
    query: str
    history: List[dict] = []

@app.on_event("startup")
async def startup_event():
    # Pre-load the LLM pipeline
    print("Loading LLM model...")
    load_llm()
    print("LLM loaded.")

@app.post("/upload")
async def upload_pdf(files: List[UploadFile] = File(...)):
    try:
        pdf_bytes = [await file.read() for file in files]
        raw_text = get_pdf_text(pdf_bytes)
        
        if not raw_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the provided PDFs.")
            
        text_chunks = get_text_chunks(raw_text)
        vectorstore = build_vector_store(text_chunks)
        
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            "vectorstore": vectorstore,
            "raw_text": raw_text,
            "text_chunks": text_chunks
        }
        
        return {"session_id": session_id, "message": "Documents processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    session = sessions.get(request.session_id)
    if not session or "vectorstore" not in session:
        raise HTTPException(status_code=400, detail="Please upload a document first.")
        
    answer = ask_question(request.query, session["vectorstore"], request.history)
    return {"answer": answer}

@app.get("/summarize/{session_id}")
async def summarize(session_id: str):
    session = sessions.get(session_id)
    if not session or "text_chunks" not in session:
        raise HTTPException(status_code=400, detail="Please upload a document first.")
        
    summary = summarize_document(session["text_chunks"])
    return {"summary": summary}

@app.get("/quiz/{session_id}")
async def quiz(session_id: str):
    session = sessions.get(session_id)
    if not session or "text_chunks" not in session:
        raise HTTPException(status_code=400, detail="Please upload a document first.")
        
    quiz_data = generate_quiz(session["text_chunks"])
    return {"quiz": quiz_data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
