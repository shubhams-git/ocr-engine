"""
OCR Prompt Configuration
Developers can modify this prompt as needed
"""

# Main OCR prompt - modify this as needed
OCR_PROMPT = """
Extract all text from this document with high accuracy. 
Preserve the original formatting, structure, and layout as much as possible.
Include all visible text including headers, body text, captions, labels, and any other textual content.
If there are tables, maintain the table structure.
If there are multiple columns, preserve the column layout.
Return only the extracted text without any additional commentary.
"""

def get_prompt() -> str:
    """Get the current OCR prompt"""
    return OCR_PROMPT.strip()

def set_prompt(new_prompt: str) -> None:
    """Set a new OCR prompt"""
    global OCR_PROMPT
    OCR_PROMPT = new_prompt 