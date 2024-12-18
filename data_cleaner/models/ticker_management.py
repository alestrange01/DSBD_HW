from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String
from db.db import DB 

class TickerManagement(DB.Base): #TODO La classe DB va cosi o con DB().Base? Ovunque
    __tablename__ = 'ticker_management'  

    id = Column(Integer, primary_key=True)
    share_cod = Column(String, nullable=False, unique=True) 
    counter = Column(Integer, nullable=False)
    
    def __repr__(self):
        return f"TickerManagement(id={self.id}, share_cod='{self.share_cod}', counter='{self.counter}')"