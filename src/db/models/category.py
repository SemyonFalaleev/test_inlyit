from src.db.base import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=100), nullable=False, unique=True)

    advertisements = relationship("Advertisement", back_populates="categories")