import time
import io
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from pypdf import PdfReader

from db.session import init_db, SessionLocal, QueryLogModel, DocumentModel
from core.agent.router import route_query

app = FastAPI(title="Internal IT Helpdesk Assistant")
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class QueryInput(BaseModel):
    query: str

class EvalInput(BaseModel):
    queries: List[str]

@app.post("/ingest")
async def ingest_document(
    metadata_info: str = Form("General Docs"),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Ingests documentation via raw text or by uploading a document (PDF or TXT).
    """
    extracted_text = ""

    if file:
        filename = file.filename.lower()
        file_bytes = await file.read()
        
        if filename.endswith(".pdf"):
            try:
                pdf_stream = io.BytesIO(file_bytes)
                reader = PdfReader(pdf_stream)
                pages_text = []
                
                for page in reader.pages:
                    page_content = page.extract_text()
                    if page_content:
                        pages_text.append(page_content.strip())
                
                extracted_text = "\n".join(pages_text)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")
                
        elif filename.endswith(".txt"):
            try:
                extracted_text = file_bytes.decode("utf-8")
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to decode text file: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Please upload a .pdf or .txt file.")

    elif content:
        extracted_text = content
        
    else:
        raise HTTPException(
            status_code=400, 
            detail="You must provide either a 'content' text string or upload a 'file'."
        )

    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="Extracted document content is empty.")

    new_doc = DocumentModel(content=extracted_text, metadata_info=metadata_info)
    db.add(new_doc)
    db.commit()

    return {
        "status": "Success", 
        "message": "Document ingested into database successfully.",
        "character_count": len(extracted_text)
    }


@app.post("/query")
def process_query(user_input: QueryInput, db: Session = Depends(get_db)):
    start_time = time.time()

    agent_result = route_query(user_input.query)

    latency_ms = int((time.time() - start_time) * 1000)

    log_entry = QueryLogModel(
        input_query=user_input.query,
        output_response=agent_result["response"],
        tools_used=agent_result["tools_used"],
        routing_decision=agent_result["route"],
        latency_ms=latency_ms
    )
    db.add(log_entry)
    db.commit()

    return {
        "final_answer": agent_result["response"],
        "routing_decision": agent_result["route"],
        "tools_used": agent_result["tools_used"],
        "latency_ms": latency_ms
    }

@app.post("/eval")
def evaluate_dataset(dataset: EvalInput, db: Session = Depends(get_db)):
    evaluation_results = []

    for individual_query in dataset.queries:
        start_time = time.time()
        agent_result = route_query(individual_query)
        latency_ms = int((time.time() - start_time) * 1000)

        log_entry = QueryLogModel(
            input_query=individual_query,
            output_response=agent_result["response"],
            tools_used=agent_result["tools_used"],
            routing_decision=agent_result["route"],
            latency_ms=latency_ms
        )
        db.add(log_entry)
        
        evaluation_results.append({
            "query": individual_query,
            "final_answer": agent_result["response"],
            "routing_decision": agent_result["route"],
            "tools_used": agent_result["tools_used"],
            "latency": f"{latency_ms}ms"
        })
        
    db.commit()
    return {"evaluation_report": evaluation_results}