from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Text, ForeignKey, Boolean


class Book(BaseModel, Base):
    __tablename__ = 'books'
    title = Column(String(128), nullable=False)
    author = Column(String(128), nullable=False)
    genre = Column(String(64), nullable=True)
    condition = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String(120), ForeignKey('users.id'), nullable=False)
    cover = Column(String(256), nullable=True)
    location = Column(String(128), nullable=False)
    swap_request_swapped = Column(Boolean, default=False)

    def __init__(self, title, author, genre, condition, description, user_id,
                 cover, swapped, location):
        super().__init__()
        self.title = title
        self.author = author
        self.genre = genre
        self.condition = condition
        self.description = description
        self.user_id = user_id
        self.cover = cover
        self.location = location
        self.swap_request_swapped = swapped
