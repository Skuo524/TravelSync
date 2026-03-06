from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

# Database path
SQLALCHEMY_DATABASE_URL = "sqlite:///./travelsync.db"

# Create engine (check_same_thread=False is needed for SQLite with multiple threads like Streamlit)
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database and create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
