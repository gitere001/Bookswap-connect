from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Text, ForeignKey, Boolean


class Message(BaseModel, Base):
    __tablename__ = 'messages'
    sender_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    recipient_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)

    def __init__(self, sender_id, recipient_id, content):
        super().__init__()
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.content = content
