from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from db.db import Base 

class TickerManagement(Base):
    __tablename__ = 'ticker_management'  

    id = Column(Integer, primary_key=True)
    share_cod = Column(String, nullable=False, unique=True) 
    counter = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"TickerManagement(share_cod={self.share_cod}, counter={self.counter})"