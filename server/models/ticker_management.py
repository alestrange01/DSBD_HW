from sqlalchemy import Column, Integer, String
from db.db import DB 

class TickerManagement(DB.Base):
    __tablename__ = 'ticker_management'  

    id = Column(Integer, primary_key=True)
    share_cod = Column(String, nullable=False, unique=True) 
    counter = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"TickerManagement(id={self.id}, share_cod='{self.share_cod}', counter='{self.counter}')"
    
    def to_dict(self):
        return {
            "id": self.id,
            "share_cod": self.share_cod,
            "counter": self.counter
        }