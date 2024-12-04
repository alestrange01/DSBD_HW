from sqlalchemy import Column, Integer, String, Numeric
from db.db import Base 

class User(Base):
    __tablename__ = 'users'  

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True) 
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    share_cod = Column(String, nullable=False) 
    high_value = Column(Numeric(precision=10, scale=3), nullable=True)
    low_value = Column(Numeric(precision=10, scale=3), nullable=True)
    
    def __repr__(self):
        return f"User: email: {self.email}, role: {self.role}, share_cod: {self.share_cod}, high_value: {self.high_value}, low_value: {self.low_value}"
    