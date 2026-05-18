import re

def calculate(expression: str) -> str:
    """
    Cleans up a text math equation and securely computes the arithmetic answer.
    """
    clean_expression = expression.replace("?", "").strip()
    
    clean_expression = re.sub(r'[^0-9+\-*/().\s]', '', clean_expression)
    
    if not any(char.isdigit() for char in clean_expression):
        return "Could not compute equation: No valid numbers found."
    
    try:
        result = eval(clean_expression)
        return f"Calculation Result: {result}"
    except Exception as e:
        return f"Could not compute equation: {str(e)}"