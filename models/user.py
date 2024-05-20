from models.base_model import BaseModel, Base
import models
from os import getenv
import sqlalchemy
from sqlalchemy import Column, String


class User(BaseModel, Base):
    """User class"""
    __tablename__ = 'users'
    email = Column(String(128), nullable=False, unique=True)
    password = Column(String(128), nullable=False)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)

    def __init__(self, email, password, first_name, last_name):
        """Initialize the user with email, password, first name, and last
        name."""
        super().__init__()
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
