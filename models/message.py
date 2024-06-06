from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Text, ForeignKey, Boolean


class Message(BaseModel, Base):
    """
    Message class for representing messages in the Book Swap Connect project.

    Inherits from BaseModel and Base.
    """
    __tablename__ = 'messages'
    sender_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    recipient_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)

    def __init__(self, sender_id, recipient_id, content):
        """
        Initializes a new Message instance.

        Parameters:
            sender_id (str): The ID of the user sending the message.
            recipient_id (str): The ID of the user receiving the message.
            content (str): The content of the message.
        """
        super().__init__()
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.content = content
