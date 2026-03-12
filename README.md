# 🤖 AI Chatbot Portfolio — RAG-Powered Demo

A full-stack web application showcasing three AI-powered chatbots (Law Firm, Real Estate, Dental Clinic) built with **FastAPI**, **LangChain**, **Google Gemini 2.5 Flash**, and **FAISS** vector search.

---

## 🚀 Quick Start

### 1. Clone the project

```bash
git clone https://github.com/siddcxdes/smart-AI-chatbot.git
cd smart-AI-chatbot
```

### 2. Set up the backend

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Add your Gemini API key

Open `backend/.env` and replace the placeholder:

```
GEMINI_API_KEY=your_actual_gemini_api_key
```

> Get a free API key from [Google AI Studio](https://aistudio.google.com/apikey)

### 4. (Optional) Add documents

Drop PDF files into the relevant folders:

- `backend/docs/lawfirm/`
- `backend/docs/realestate/`
- `backend/docs/dental/`

If no PDFs are present, the chatbots will use built-in sample content.

### 5. Run the backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`

### 6. Open the frontend

Open `frontend/index.html` directly in your browser, or use **Live Server** in VS Code.

---

## 📁 Project Structure

```
smart-AI-chatbot/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt        # Python dependencies
│   ├── .env                    # API key config
│   ├── docs/
│   │   ├── lawfirm/            # Law firm PDFs
│   │   ├── realestate/         # Real estate PDFs
│   │   └── dental/             # Dental clinic PDFs
│   └── rag/
│       ├── __init__.py
│       ├── loader.py           # Document loading & chunking
│       ├── vectorstore.py      # FAISS vector store
│       ├── chain.py            # LangChain RAG chain
│       └── prompts.py          # Domain system prompts
├── frontend/
│   └── index.html              # Full frontend (single file)
└── README.md
```

## 🔌 API Endpoints

| Method | Path      | Description                |
| ------ | --------- | -------------------------- |
| POST   | `/chat`   | Send a message to a chatbot |
| GET    | `/health` | Health check               |

### POST `/chat`

```json
{
  "domain": "lawfirm",
  "message": "What services do you offer?",
  "history": []
}
```

---

## 🛠 Tech Stack

- **Backend:** FastAPI, LangChain, Google Gemini 2.5 Flash, FAISS, PyPDF
- **Frontend:** Vanilla HTML/CSS/JS (single file, no frameworks)
- **Embeddings:** Google embedding-001
- **Vector Store:** FAISS (in-memory)

---

## 📝 License

MIT — feel free to use this as a starting point for your own chatbot projects.
