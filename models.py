from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    category = Column(String)
    amount = Column(Float)
    description = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)