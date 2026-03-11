# AI Customer Support System

A smart chatbot that answers customer questions using company documents. Built with **FastAPI**, **LangChain**, **Ollama**, **ChromaDB**, and **PostgreSQL**.

---

## What it looks like

- **Chat Page** - Customers ask questions, AI answers instantly
- **Admin Panel** - View and manage support tickets
- **Auto Tickets** - When AI can't answer, a ticket is created automatically

---

## Tech Stack

| Technology | What it does |
|---|---|
| FastAPI | Backend API framework |
| PostgreSQL | Stores users, tickets, chat history |
| ChromaDB | Vector database for document search |
| LangChain | Connects AI model with documents (RAG) |
| Ollama | Runs AI model locally |
| HTML/CSS/JS | Simple frontend |

---

## Project Structure

```
smart-AI-chatbot/
├── main.py                  # entry point, starts the server
├── config.py                # all settings in one place
├── database.py              # database connection setup
├── models.py                # database tables (User, Ticket, Chat)
├── schemas.py               # request/response data shapes
├── ai_engine.py             # the AI brain (RAG logic)
├── document_loader.py       # loads company docs into ChromaDB
├── setup_db.py              # creates database tables
├── requirements.txt         # python packages needed
│
├── routes/
│   ├── chat.py              # chat API endpoints
│   ├── users.py             # user API endpoints
│   └── tickets.py           # ticket API endpoints
│
├── templates/
│   ├── index.html           # main chat page
│   └── admin.html           # admin dashboard
│
├── static/
│   └── style.css            # all the styling
│
└── company_docs/            # put your .txt files here
    ├── faq.txt
    ├── refund_policy.txt
    ├── shipping_info.txt
    └── account_management.txt
```

---

## How to Set Up

### Step 1: Install Prerequisites

Make sure you have these installed:
- **Python 3.10+**
- **PostgreSQL** (running on localhost:5432)
- **Ollama** (https://ollama.ai)

### Step 2: Set Up PostgreSQL Database

```bash
# open psql and create a database
psql -U postgres
CREATE DATABASE support_db;
\q
```

### Step 3: Pull the AI Model with Ollama

```bash
# download the mistral model (or any model you prefer)
ollama pull mistral

# make sure ollama is running
ollama serve
```

### Step 4: Install Python Packages

```bash
# create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate    # on mac/linux
# venv\Scripts\activate     # on windows

# install packages
pip install -r requirements.txt
```

### Step 5: Set Up Database Tables

```bash
python setup_db.py
```

### Step 6: Load Company Documents into ChromaDB

```bash
python document_loader.py
```

### Step 7: Start the Server

```bash
uvicorn main:app --reload --port 8000
```

### Step 8: Open in Browser

- **Chat Page**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Documentation**: http://localhost:8000/docs

---

## API Endpoints

### Chat
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/chat` | Send a question, get AI answer |
| GET | `/api/chat/history/{email}` | Get chat history for a user |

### Users
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/users` | Create a new user |
| GET | `/api/users` | Get all users |
| GET | `/api/users/{email}` | Get a specific user |

### Tickets
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/tickets` | Get all tickets |
| GET | `/api/tickets/{id}` | Get a specific ticket |
| PUT | `/api/tickets/{id}` | Update ticket status |
| DELETE | `/api/tickets/{id}` | Delete a ticket |

### Health
| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Check if system is running |

---

## How RAG Works (Simple Explanation)

1. **Load** - Company documents (FAQ, policies) are split into small chunks
2. **Embed** - Each chunk is converted into numbers (vectors) using AI
3. **Store** - These vectors are saved in ChromaDB
4. **Search** - When a user asks a question, we find the most similar chunks
5. **Generate** - The AI reads those chunks and writes a human-friendly answer

This is called **Retrieval Augmented Generation (RAG)** — the AI doesn't make stuff up, it answers based on real documents.

---

## Configuration

Edit `config.py` to change settings:

```python
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/support_db"
OLLAMA_MODEL = "mistral"      # change to any ollama model
CHROMA_DB_PATH = "./chroma_storage"
DOCUMENTS_FOLDER = "./company_docs"
```

---

## Adding Your Own Documents

1. Create `.txt` files with your company information
2. Put them in the `company_docs/` folder
3. Run `python document_loader.py` to load them
4. Restart the server

---

Built by a student learning AI
