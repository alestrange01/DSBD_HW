from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Numeric
from sqlalchemy.sql import func
from db.db import DB 

class Share(DB.Base):
    __tablename__ = 'shares' 

    id = Column(Integer, primary_key=True)
    share_name = Column(String, nullable=False)
    value = Column(Numeric(precision=10, scale=3), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    def __repr__(self):
        return f"<Share(id={self.id}, share='{self.share_name}', value={self.value}, timestamp={self.timestamp})>"
