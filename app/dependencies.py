from app.database import SessionLocal, SessionManager


def get_db():
    db = SessionLocal()
    with SessionManager(db) as session:
        yield session
