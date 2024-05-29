from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Boolean, ForeignKey


class Notification(BaseModel, Base):
    __tablename__ = 'notifications'

    recipient_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    sender_id = Column(String(60), ForeignKey('users.id'), nullable=False)
    message = Column(String(250), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)

    def __init__(self, recipient_id, sender_id, message):
        super().__init__()
        self.recipient_id = recipient_id
        self.sender_id = sender_id
        self.message = message
