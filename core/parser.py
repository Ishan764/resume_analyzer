import pdfplumber

def extract_text_from_pdf(file_path):
    """
    Opens a PDF file, extracts all text, and returns it as a string.
    """
    full_text = ""
    
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            # Extract text from each page safely
            text = page.extract_text()
            if text:  
                full_text += text + "\n"
                
    return full_text.strip()