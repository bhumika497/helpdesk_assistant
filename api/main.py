import time
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

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

class DocumentInput(BaseModel):
    content: str
    metadata_info: str = "General Docs"

class EvalInput(BaseModel):
    queries: List[str]

@app.post("/ingest")
def ingest_document(doc: DocumentInput, db: Session = Depends(get_db)):
    new_doc = DocumentModel(content=doc.content, metadata_info=doc.metadata_info)
    db.add(new_doc)
    db.commit()
    return {"status": "Success", "message": "Document ingested into database successfully."}

@app.post("/query")
def process_query(user_input: QueryInput, db: Session = Depends(get_db)):
    start_time = time.time()  # Start our latency stopwatch

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