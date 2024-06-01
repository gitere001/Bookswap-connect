from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Enum, Boolean


class SwapRequest(BaseModel, Base):
    __tablename__ = 'swap_requests'
    recipient_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    requester_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    requested_book_id = Column(String(120), ForeignKey('books.id'),
                               nullable=False)
    offered_book_id = Column(String(120), ForeignKey('books.id'),
                             nullable=False)
    status = Column(Enum('pending', 'accepted', 'declined',
                         name='request_status'), default='pending')
    swapped = Column(Boolean, default=False)

    def __init__(self, requester_id, requested_book_id, offered_book_id,
                 recipient_id, swapped, status):
        super().__init__()
        self.requester_id = requester_id
        self.recipient_id = recipient_id
        self.requested_book_id = requested_book_id
        self.offered_book_id = offered_book_id
        self.status = status
        self.swapped = swapped
