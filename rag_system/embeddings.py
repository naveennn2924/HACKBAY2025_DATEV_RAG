from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import os

def create_and_save_vectorstore(text_chunks, index_dir="vector_index"):
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
    os.makedirs(index_dir, exist_ok=True)
    vectorstore.save_local(index_dir)
    return vectorstore

def load_vectorstore(index_dir="vector_index"):
    embeddings = OpenAIEmbeddings()
    if not os.path.exists(index_dir):
        raise ValueError(f"Vectorstore directory '{index_dir}' does not exist.")
    return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
