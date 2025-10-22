# app/agents/embeddings.py
from pathlib import Path
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

CURRENT_INDEX_DIR = Path(__file__).parent / "current_index"
CURRENT_INDEX_DIR.mkdir(exist_ok=True)

def build_index(pdf_dir: str | Path, chunk_size=1000, chunk_overlap=200):
    """Gera/atualiza o índice FAISS SEMPRE em current_index."""
    pdf_dir = Path(pdf_dir)
    docs = []
    for pdf in pdf_dir.glob("*.pdf"):
        docs.extend(PyPDFLoader(str(pdf)).load())

    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings()
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local(str(CURRENT_INDEX_DIR))
    return len(chunks)

def load_index():
    """Carrega o índice de current_index."""
    embeddings = OpenAIEmbeddings()
    return FAISS.load_local(folder_path=str(CURRENT_INDEX_DIR), index_name="index", embeddings=embeddings, allow_dangerous_deserialization=True)
