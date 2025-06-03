import os
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with open(pdf_path, "rb") as file:
            reader = PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading {pdf_path}: {e}")
    return text

def load_policy_texts(company_dir=None, team_dir=None):
    """
    Loads and concatenates text from all PDFs in the specified company_dir and/or team_dir.
    Returns a list of text chunks (one string per PDF).
    """
    texts = []

    # Helper function to load all PDFs in a directory
    def load_texts_from_directory(directory):
        collected_texts = []
        if not os.path.exists(directory):
            print(f"Directory does not exist: {directory}")
            return collected_texts

        for filename in os.listdir(directory):
            if filename.lower().endswith(".pdf"):
                file_path = os.path.join(directory, filename)
                text = extract_text_from_pdf(file_path)
                if text.strip():
                    collected_texts.append(text)
        return collected_texts

    # Load company policies if provided
    if company_dir is not None and os.path.exists(company_dir):
        company_texts = load_texts_from_directory(company_dir)
        texts.extend(company_texts)

    # Load team policies if provided
    if team_dir is not None and os.path.exists(team_dir):
        team_texts = load_texts_from_directory(team_dir)
        texts.extend(team_texts)

    return texts
