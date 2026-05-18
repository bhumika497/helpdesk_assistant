MOCK_KNOWLEDGE_BASE = [
    {"text": "To deploy the backend service, run 'git push origin main' and monitor the AWS pipeline.", "category": "runbook"},
    {"text": "The VPN access reset process requires raising a ticket in Jira under the IT Helpdesk category.", "category": "HR/IT"},
    {"text": "Company onboarding requires filling out the direct deposit form on day 1.", "category": "HR"}
]

def retrieve(query: str) -> str:
    """
    Scans internal document entries for matching words and compiles relevant paragraphs.
    """
    query_lower = query.lower()
    matched_chunks = []

    for doc in MOCK_KNOWLEDGE_BASE:
        words = query_lower.replace("?", "").split()
        if any(word in doc["text"].lower() for word in words if len(word) > 3):
            matched_chunks.append(doc["text"])

    if matched_chunks:
        context = " ".join(matched_chunks)
        return f"Retrieved Context: {context}"
    
    return "Retrieved Context: No specific documentation found for this query."