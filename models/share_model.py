from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func

Base = declarative_base()

class Share(Base):
    __tablename__ = 'shares' 

    id = Column(Integer, primary_key=True)
    share_name = Column(String, nullable=False)
    value = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False) 

    user = relationship("User", back_populates="shares")

    def __repr__(self):
        return f"<Share(id={self.id}, share='{self.share_name}', value={self.value}, user_id={self.user_id})>"
