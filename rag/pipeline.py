from pypdf import PdfReader

MOCK_KNOWLEDGE_BASE = [
    {"text": "To deploy the backend service, run 'git push origin main' and monitor the AWS pipeline.", "category": "runbook"},
    {"text": "The VPN access reset process requires raising a ticket in Jira under the IT Helpdesk category.", "category": "HR/IT"},
    {"text": "Company onboarding requires filling out the direct deposit form on day 1.", "category": "HR"}
]

def ingest_pdf(file_path: str, category: str):
    """
    Reads a PDF file, extracts its text page by page, 
    and adds it to the MOCK_KNOWLEDGE_BASE.
    """
    try:
        reader = PdfReader(file_path)
        extracted_text = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:  # Ensure the page has readable text
                extracted_text.append(text.strip())
        
        full_text = " ".join(extracted_text)
        
        if full_text.strip():
            MOCK_KNOWLEDGE_BASE.append({
                "text": full_text,
                "category": category
            })
            print(f"Successfully ingested: {file_path} into category '{category}'")
        else:
            print(f"Warning: No text could be extracted from {file_path}")
            
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")

from db.session import SessionLocal, DocumentModel
from sqlalchemy import or_

def retrieve(query: str) -> str:
    """
    Scans SQLAlchemy DocumentModel table for matching words 
    and compiles relevant document paragraphs.
    """
    query_lower = query.lower()
    
    clean_query = query_lower.replace("?", "").replace(".", "").replace(",", "")
    words = [word for word in clean_query.split() if len(word) > 3]

    if not words:
        return "No specific documentation found for this query."

    db = SessionLocal()
    try:
        conditions = [DocumentModel.content.ilike(f"%{word}%") for word in words]
        
        matched_docs = db.query(DocumentModel).filter(or_(*conditions)).all()
        
        if matched_docs:
            context = " ".join([doc.content for doc in matched_docs])
            return context
            
        return "No specific documentation found for this query."
        
    except Exception as e:
        return f"Error retrieving from database: {str(e)}"
        
    finally:
        db.close()