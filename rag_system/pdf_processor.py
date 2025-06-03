from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

def extract_text_from_pdfs(pdf_files):
    """
    Accepts list of open file-like PDF objects and extracts full text.
    """
    full_text = ""
    for pdf_file in pdf_files:
        reader = PdfReader(pdf_file)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text += text
    return full_text

def split_text_chunks(text, chunk_size=1000, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    return splitter.split_text(text)

def load_policy_texts(company_dir="policies/company", team_dir=None):
    """
    Loads, extracts, and chunks text from company and optionally team policy PDF files.
    Returns a list of text chunks.
    """
    all_chunks = []

    # Load company policy PDFs
    if os.path.exists(company_dir):
        for fname in os.listdir(company_dir):
            path = os.path.join(company_dir, fname)
            with open(path, "rb") as f:
                text = extract_text_from_pdfs([f])
                chunks = split_text_chunks(text)
                all_chunks.extend(chunks)

    # Load team policy PDFs if team_dir provided
    if team_dir and os.path.exists(team_dir):
        for fname in os.listdir(team_dir):
            path = os.path.join(team_dir, fname)
            with open(path, "rb") as f:
                text = extract_text_from_pdfs([f])
                chunks = split_text_chunks(text)
                all_chunks.extend(chunks)

    return all_chunks
