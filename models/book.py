from models.base_model import BaseModel, Base
from sqlalchemy import Column, String, Text, ForeignKey


class Book(BaseModel, Base):
    __tablename__ = 'books'
    title = Column(String(128), nullable=False)
    author = Column(String(128), nullable=False)
    genre = Column(String(64), nullable=True)
    condition = Column(String(64), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(String(120), ForeignKey('users.id'), nullable=False)

    def __init__(self, title, author, genre, condition, description, user_id):
        super().__init__()
        self.title = title
        self.author = author
        self.genre = genre
        self.condition = condition
        self.description = description
        self.user_id = user_id
