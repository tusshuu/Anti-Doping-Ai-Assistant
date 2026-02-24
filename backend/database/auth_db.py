from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True, nullable=True)
    sport = Column(String, nullable=True)
    password = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)

def get_user_by_email(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()

        if not user:
            return None

        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "sport": user.sport,
            "gender": getattr(user, "gender", "Not Provided"),
            "subscription": getattr(user, "subscription", "Not Active"),
        }

    finally:
        db.close()

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    searched_text = Column(String)
    result_summary = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")