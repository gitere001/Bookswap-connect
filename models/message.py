from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Text, ForeignKey


class Message(BaseModel, Base):
    __tablename__ = 'messages'
    sender_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    recipient_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
