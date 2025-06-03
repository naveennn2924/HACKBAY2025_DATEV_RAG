import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
import warnings

# Ignore warnings
warnings.filterwarnings('ignore', category=UserWarning, message='.*torch.classes.*')

# Load environment variables including OPENAI_API_KEY
load_dotenv()

# Function to extract text from PDFs
def get_pdf_text(pdf_docs):
    pdf_text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                pdf_text += text
    return pdf_text

# Function to split text into chunks
def get_text_chunks(pdf_text, chunk_size=1000, chunk_overlap=100):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(pdf_text)
    return chunks

# Function to generate vector store from text chunks
def get_vectorstore(text_chunks):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    vectorstore.save_local("vector_index")
    return vectorstore

# Function to define the QA chain
def get_conversation():
    prompt_template = """
    Answer the question as detailed as possible using only the given context from the PDFs.
    Ensure your response is based strictly on the provided documents.

    Context:\n{context}\n
    Question:\n{question}\n

    Response:
    """
    llm = OpenAI(temperature=0.5, max_tokens=512)
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)
    return chain

# Function to process user question and return answer
def return_user_input(user_question):
    embeddings = OpenAIEmbeddings()
    # Allow dangerous deserialization here since loading a local pickle file
    db = FAISS.load_local("vector_index", embeddings, allow_dangerous_deserialization=True)
    docs = db.similarity_search(user_question)

    chain = get_conversation()
    response = chain({"input_documents": docs, "question": user_question}, return_only_outputs=True)

    st.markdown(f'<div class="response-box">{response["output_text"]}</div>', unsafe_allow_html=True)

# Main Streamlit app
def main():
    st.set_page_config(page_title="PDF Query", page_icon="📄", layout="wide")

    # Custom CSS
    st.markdown("""
        <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
        }
        .stTextInput input {
            border-radius: 10px;
            padding: 10px;
            border: 1px solid #ccc;
            font-size: 16px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            padding: 10px 15px;
            border-radius: 8px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .response-box {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            font-size: 16px;
            color: #333;
        }
        </style>
    """, unsafe_allow_html=True)

    st.header("📚 Ask Questions to Multiple PDFs")
    st.write("Upload PDF documents and ask questions about their content.")

    uploaded_files = st.file_uploader("Upload PDFs", accept_multiple_files=True, type=["pdf"])

    if uploaded_files:
        pdf_text = get_pdf_text(uploaded_files)
        text_chunks = get_text_chunks(pdf_text)
        get_vectorstore(text_chunks)
        st.success("PDFs processed successfully! You can now ask questions.")

    user_question = st.text_input("Enter your question about the documents:")
    if user_question:
        return_user_input(user_question)

if __name__ == "__main__":
    main()
