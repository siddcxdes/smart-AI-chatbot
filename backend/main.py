from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine, Base
from backend.routes import chat, users, tickets

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

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(users.router, prefix="/api", tags=["Users"])
app.include_router(tickets.router, prefix="/api", tags=["Tickets"])

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
