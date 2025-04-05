from src.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=100), nullable=False)
    surname = Column(String(length=100), nullable=False)
    email = Column(String(length=100), nullable=False, unique=True)
    hashed_password = Column(String(length=300), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False) 
    is_banned = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    advertisements = relationship("Advertisement", back_populates="user")

