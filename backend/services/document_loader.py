"""
Document loader - Extracts text from files, stores in DB, builds in-memory vector store.

Key changes for deployment:
- PDFs are now supported via pypdf
- Document text is stored in PostgreSQL (not local filesystem)
- ChromaDB runs in-memory (no local chroma_storage/ folder needed)
- Vector store is rebuilt from DB on startup and on retrain
"""
import io
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from pypdf import PdfReader

# Global in-memory vector store
_vector_store = None


def get_embeddings():
    """Free, fast local embedding model"""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract text content from uploaded files (PDF, TXT, MD)."""
    if filename.lower().endswith(".pdf"):
        try:
            reader = PdfReader(io.BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            return text.strip()
        except Exception as e:
            print(f"Error reading PDF {filename}: {e}")
            return ""
    else:
        # TXT and MD files
        return file_bytes.decode("utf-8", errors="ignore").strip()


def build_vector_store(documents_text: list):
    """Build in-memory ChromaDB from a list of document text strings."""
    global _vector_store

    if not documents_text:
        _vector_store = None
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.create_documents(documents_text)
    print(f"Total chunks created: {len(chunks)}")

    embeddings = get_embeddings()
    _vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings
        # No persist_directory = purely in-memory!
    )

    print("Vector store built in memory successfully!")
    return _vector_store


def get_vector_store():
    """Return the current in-memory vector store (or None if not loaded)."""
    return _vector_store


def load_from_database(db_session):
    """Load all documents from PostgreSQL and build the in-memory vector store."""
    from backend.db.models import Document

    docs = db_session.query(Document).all()
    if not docs:
        print("No documents found in database.")
        return None

    texts = [doc.content for doc in docs]
    print(f"Loading {len(docs)} document(s) from database...")
    return build_vector_store(texts)
