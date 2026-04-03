import os
import shutil
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from backend.config import CHROMA_DB_PATH, DOCUMENTS_FOLDER

def get_embeddings():
    """We use this free, fast local model to turn words into numbers"""
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_documents():
    # If the database exists, delete it so we start completely fresh!
    if os.path.exists(CHROMA_DB_PATH):
        # Do not use rmtree, it corrupts the running sqlite db connection!
        try:
            db = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=get_embeddings())
            db.delete_collection()
            print("Cleared old memory database via delete_collection.")
        except Exception as e:
            print("Could not clear collection:", e)

    if not os.path.exists(DOCUMENTS_FOLDER):
        os.makedirs(DOCUMENTS_FOLDER)
        print("Created company_docs folder - put your txt files in there!")
        return None

    all_text = []
    for filename in os.listdir(DOCUMENTS_FOLDER):
        if filename.endswith(".txt"):
            path = os.path.join(DOCUMENTS_FOLDER, filename)
            with open(path, "r") as file:
                text = file.read()
                all_text.append(text)
                print("Loaded:", filename)

    if len(all_text) == 0:
        print("No txt files found!")
        return None

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.create_documents(all_text)
    print("Total chunks created:", len(chunks))

    embeddings = get_embeddings()
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )

    print("Done! Documents are now in Chroma.")
    return db

def get_vector_store():
    # Only get the database if it actually exists, don't auto-load yet
    if os.path.exists(CHROMA_DB_PATH) and len(os.listdir(CHROMA_DB_PATH)) > 0:
        embeddings = get_embeddings()
        db = Chroma(
            persist_directory=CHROMA_DB_PATH,
            embedding_function=embeddings
        )
        return db

    return None

if __name__ == "__main__":
    load_documents()
