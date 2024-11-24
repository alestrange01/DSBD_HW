from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func
from db.db import Base 

class User(Base):
    __tablename__ = 'users'  

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True) 
    password = Column(String, nullable=False)
    share_cod = Column(String, nullable=False) 
    role = Column(String, nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}', share_cod='{self.share_cod}')>"
    