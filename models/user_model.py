from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'  

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True) 
    password = Column(String, nullable=False)
    share_int = Column(Integer, nullable=False) 
    
    shares = relationship("Share", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"