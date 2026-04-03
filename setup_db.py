# setup_db.py - run this once to create all the tables

from database import engine, Base
from models import User, SupportTicket, ChatHistory

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done! Tables created.")

# Compatibility script - calls backend.setup_db
if __name__ == "__main__":
    # importing backend.setup_db will create tables (keeps old behaviour)
    import backend.setup_db  # noqa: F401
    print("Ran backend.setup_db")
