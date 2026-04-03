from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.db.database import engine, Base, SessionLocal
from backend.routes import chat, users, tickets
from backend.services.document_loader import load_from_database

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Customer Support",
    description="Chatbot that answers questions using company documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(tickets.router, prefix="/api", tags=["Tickets"])


@app.on_event("startup")
def startup_load_vectorstore():
    """Auto-load documents from PostgreSQL into in-memory vector store on startup."""
    try:
        db = SessionLocal()
        load_from_database(db)
        db.close()
        print("Vector store loaded from database on startup.")
    except Exception as e:
        print(f"Could not load vector store on startup: {e}")


@app.get("/", response_class=HTMLResponse)
def home_page():
    return FileResponse(FRONTEND_DIR / "index.html")

@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return FileResponse(FRONTEND_DIR / "chat.html")

@app.get("/admin", response_class=HTMLResponse)
def admin_page():
    return FileResponse(FRONTEND_DIR / "admin.html")

@app.get("/api/health")
def health_check():
    return {"status": "running", "message": "Server is up!"}

# Mount static files LAST — serves CSS, JS, favicon for any unmatched path
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
