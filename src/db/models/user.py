from src.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    name = Column(String(length=100), nullable=False)
    surname = Column(String(length=100), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False) 
    is_banned = Column(Boolean, default=False, nullable=False)


