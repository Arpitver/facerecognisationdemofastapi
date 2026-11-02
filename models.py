from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class Person(Base):
    __tablename__ = "persons"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    encoding = Column(Text, nullable=False)  # 128 floats, JSON string
    image_path = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
