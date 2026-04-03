import os
from dotenv import load_dotenv

# load everything from the .env file
load_dotenv()

# where we connect to our database (pulling from .env now!)
DATABASE_URL = os.getenv("DATABASE_URL")

# our new pollination API key
POLLINATIONS_API_KEY = os.getenv("POLLINATIONS_API_KEY")

CHROMA_DB_PATH = "./chroma_storage"
DOCUMENTS_FOLDER = "./company_docs"
