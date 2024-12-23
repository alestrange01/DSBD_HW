from sqlalchemy import Column, Integer, String, Numeric
from db.db import DB 

class User(DB.Base):
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
    
    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "share_cod": self.share_cod,
            "high_value": float(self.high_value) if self.high_value is not None else None,
            "low_value": float(self.low_value) if self.low_value is not None else None
        }