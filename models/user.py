#!/usr/bin/python3
"""this is the user model for the user of bookswap connect"""
from models.base_model import BaseModel


class User(BaseModel):
    """User class"""
    email = ""
    password = ""
    first_name = ""
    last_name = ""

    def __init__(self):
        super().__init__()


user1 = User()
print(user1)
