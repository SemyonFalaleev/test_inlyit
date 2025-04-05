from src.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, func
from sqlalchemy.orm import relationship

class Advertisement(Base):
    __tablename__ = "advertisements"
    id = Column(Integer, primary_key=True)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    name = Column(String(length=150), nullable=False)
    descriptions = Column(String(length=1000), nullable=False)
    price = Column(Integer, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        server_onupdate=func.now())
    
     

    categories = relationship("Category", back_populates="advertisements")
    user = relationship("User", back_populates="advertisements")


