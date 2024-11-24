from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db.db import Base 

class Share(Base):
    __tablename__ = 'shares' 

    id = Column(Integer, primary_key=True)
    share_name = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Share(id={self.id}, share='{self.share_name}', value={self.value}, timestamp={self.timestamp})>"
