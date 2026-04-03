from backend.db.database import engine, Base
from backend.db.models import User, SupportTicket, ChatHistory, Document


def setup():
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified!")


if __name__ == "__main__":
    setup()
