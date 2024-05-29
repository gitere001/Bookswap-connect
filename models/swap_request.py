from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Enum, Text


class SwapRequest(BaseModel, Base):
    __tablename__ = 'swap_requests'
    requester_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    requested_book_id = Column(String(120), ForeignKey('books.id'),
                               nullable=False)
    offered_book_id = Column(String(120), ForeignKey('books.id'),
                             nullable=False)
    status = Column(Enum('pending', 'accepted', 'declined',
                         name='request_status'), default='pending')
    message = Column(Text, nullable=True)

    def __init__(self, requester_id, requested_book_id, offered_book_id,
                 status, message):
        super().__init__()
        self.requester_id = requester_id
        self.requested_book_id = requested_book_id
        self.offered_book_id = offered_book_id
        self.status = status
        self.message = message
