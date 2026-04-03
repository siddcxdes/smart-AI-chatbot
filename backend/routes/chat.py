from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
from typing import List

from backend.db.database import get_db
from backend.db.schemas import ChatRequest, ChatResponse
from backend.db.models import ChatHistory, SupportTicket, User, Document
from backend.services.ai_engine import get_ai_answer
from backend.auth import get_admin_user, get_current_user
from backend.services.document_loader import load_from_database, extract_text_from_file

router = APIRouter()


# ----- ADMIN ONLY: Upload Documents (now stores in PostgreSQL) -----
@router.post("/admin/upload-docs")
async def upload_documents(
    files: List[UploadFile] = File(...),
    wipe_existing: str = Form("false"),
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Upload company documents (.txt, .md, .pdf).
    Text is extracted and stored in PostgreSQL — no local filesystem needed.
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="You can only upload up to 10 documents at a time.")

    if wipe_existing.lower() == "true":
        db.query(Document).delete()
        db.commit()

    saved_files = []
    for file in files:
        if not file.filename.endswith((".txt", ".md", ".pdf")):
            continue

        file_bytes = await file.read()
        text_content = extract_text_from_file(file_bytes, file.filename)

        if not text_content.strip():
            continue

        # Check if document with same filename already exists, replace it
        existing = db.query(Document).filter(Document.filename == file.filename).first()
        if existing:
            existing.content = text_content
            existing.file_type = file.filename.rsplit(".", 1)[-1].lower()
        else:
            doc = Document(
                filename=file.filename,
                content=text_content,
                file_type=file.filename.rsplit(".", 1)[-1].lower()
            )
            db.add(doc)

        saved_files.append(file.filename)

    db.commit()
    return {
        "status": "success",
        "message": f"Successfully uploaded {len(saved_files)} document(s) to database.",
        "files": saved_files
    }


# ----- ADMIN ONLY: Retrain (now reads from PostgreSQL) -----
@router.post("/admin/retrain")
def retrain_chatbot(admin: User = Depends(get_admin_user), db: Session = Depends(get_db)):
    """
    Rebuild the AI vector store from all documents stored in PostgreSQL.
    """
    result = load_from_database(db)
    if result is None:
        return {"status": "failed", "message": "No documents found in database! Upload some first."}

    return {"status": "success", "message": "AI knowledge base retrained from database documents!"}


@router.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    past_chats = db.query(ChatHistory).filter(
        ChatHistory.user_email == current_user.email
    ).order_by(ChatHistory.created_at.asc()).all()

    chat_history = []
    for chat in past_chats[-5:]:
        chat_history.append({
            "question": chat.question,
            "answer": chat.answer
        })

    result = get_ai_answer(request.question, chat_history=chat_history)

    ticket_id = None

    if result["needs_ticket"]:
        full_conversation = ""
        for msg in chat_history:
            full_conversation += f"Customer: {msg['question']}\nAssistant: {msg['answer']}\n"
        full_conversation += f"Customer: {request.question}"

        ticket = SupportTicket(
            user_email=current_user.email,
            question=full_conversation.strip(),
            ai_response=result["answer"],
            status="open"
        )
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        ticket_id = ticket.id

    chat = ChatHistory(
        user_email=current_user.email,
        question=request.question,
        answer=result["answer"]
    )
    db.add(chat)
    db.commit()

    source = "ticket_created" if result["needs_ticket"] else "ai"
    return ChatResponse(answer=result["answer"], source=source, ticket_id=ticket_id)


@router.get("/chat/history/{email}")
def get_chat_history(email: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.email != email and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only view your own chat history.")

    chats = db.query(ChatHistory).filter(
        ChatHistory.user_email == email
    ).order_by(ChatHistory.created_at.desc()).all()

    return chats
