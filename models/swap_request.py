from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, ForeignKey, Enum, Boolean


class SwapRequest(BaseModel, Base):
    """
    SwapRequest class for representing swap requests in the Book Swap Connect
    project.

    Inherits from BaseModel and Base.
    """
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
    viewed = Column(Boolean, default=False)

    def __init__(self, requester_id, requested_book_id, offered_book_id,
                 recipient_id, swapped=False, viewed=False, status='pending'):
        """
        Initializes a new SwapRequest instance.

        Parameters:
            requester_id (str): The ID of the user making the swap request.
            requested_book_id (str): The ID of the book being requested.
            offered_book_id (str): The ID of the book being offered in
            exchange.
            recipient_id (str): The ID of the user receiving the swap request.
            swapped (bool): Indicates if the swap has been completed
            (default is False).
            viewed (bool): Indicates if the swap request has been viewed by
            the recipient (default is False).
            status (str): The status of the swap request, can be 'pending',
            'accepted', or 'declined' (default is 'pending').
        """
        super().__init__()
        self.requester_id = requester_id
        self.recipient_id = recipient_id
        self.requested_book_id = requested_book_id
        self.offered_book_id = offered_book_id
        self.status = status
        self.swapped = swapped
        self.viewed = viewed
