import re
from tools.calculator import calculate
from rag.pipeline import retrieve

def get_active_users():
    """Simulates querying internal tables for active user metrics."""
    return "Database Result: There are currently 1,245 active users in the system."

def route_query(query: str) -> dict:
    """
    Analyzes the incoming user query and manually routes it to the 
    appropriate module (Database, Calculator, or RAG).
    """
    query_lower = query.lower()

    if "active users" in query_lower or "paid accounts" in query_lower:
        data = get_active_users()
        return {
            "route": "DATABASE",
            "response": data,
            "tools_used": "db_query"
        }
        
    elif any(char.isdigit() for char in query) and any(op in query for op in ["+", "-", "*", "/"]):
        clean_math = query_lower
        for word in ["what is", "calculate", "compute", "equal", "?", "usd", "npr", "total"]:
            clean_math = clean_math.replace(word, "")
        
        clean_math = clean_math.strip()
        
        result = calculate(clean_math)
        return {
            "route": "TOOL",
            "response": result,
            "tools_used": "calculator"
        }
        
    else:
        docs = retrieve(query)
        return {
            "route": "RAG",
            "response": f"Based on our documents: {docs}",
            "tools_used": "rag_retrieval"
        }