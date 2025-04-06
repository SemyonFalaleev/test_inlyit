from src.db.base import Base
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, func
from sqlalchemy.orm import relationship

class Review(Base):
    __tablename__ = "reviews"
    id = Column(Integer, primary_key=True)
    description = Column(String(length=1000), nullable=False)
    adv_id = Column(ForeignKey("advertisements.id"), nullable=False)
    user_id = Column(ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(),
                        onupdate=func.now())
    
    advertisement = relationship("Advertisement", back_populates="reviews")
    user = relationship("User", back_populates= "reviews")