from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Form
from sqlalchemy.orm import Session
import os
import shutil
from typing import List

from backend.database import get_db
from backend.schemas import ChatRequest, ChatResponse
from backend.models import ChatHistory, SupportTicket, User
from backend.ai_engine import get_ai_answer
from backend.auth import get_admin_user, get_current_user
from backend.document_loader import load_documents

router = APIRouter()

# ----- ADMIN ONLY: Upload Documents endpoint -----
@router.post("/admin/upload-docs")
async def upload_documents(
    files: List[UploadFile] = File(...), 
    wipe_existing: str = Form("false"),
    admin: User = Depends(get_admin_user)
):
    """
    Allow an admin to upload up to 10 company documents (.txt, .md, .pdf)
    and optionally wipe all existing documents before saving.
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="You can only upload up to 10 documents at a time.")
    
    # If the user chose to wipe existing files, delete the folder beforehand
    if wipe_existing.lower() == "true":
        if os.path.exists("company_docs"):
            shutil.rmtree("company_docs")

    # Ensure the company_docs folder exists (whether we just deleted it or it didn't exist)
    os.makedirs("company_docs", exist_ok=True)

    saved_files = []
    for file in files:
        if not file.filename.endswith((".txt", ".md", ".pdf")):
            continue
            
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join("company_docs", safe_filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        saved_files.append(safe_filename)
        
    return {"status": "success", "message": f"Successfully uploaded {len(saved_files)} documents.", "files": saved_files}

# ----- ADMIN ONLY: The "Retrain Button" Endpoint -----
@router.post("/admin/retrain")
def retrain_chatbot(admin: User = Depends(get_admin_user)):
    """
    An admin clicks "Retrain". This route deletes the old AI memory
    and completely re-reads the txt files in `company_docs/`.
    """
    db = load_documents()
    if db is None:
        return {"status": "failed", "message": "No documents found in company_docs folder!"}
    
    return {"status": "success", "message": "Chatbot memory wiped and successfully retrained with new documents!"}


@router.post("/chat", response_model=ChatResponse)
# Notice we added `current_user: User = Depends(get_current_user)`.
# Now you ONLY can chat if you are logged in!
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
    # You can't spy on other people's chats unless you're an Admin!
    if current_user.email != email and current_user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="You can only view your own chat history.")

    chats = db.query(ChatHistory).filter(
        ChatHistory.user_email == email
    ).order_by(ChatHistory.created_at.desc()).all()

    return chats
