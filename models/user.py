from models.base_model import BaseModel, Base
from sqlalchemy import Column, String


class User(BaseModel, Base):
    """
    User class for representing user entities in the Book Swap Connect project.

    Inherits from BaseModel and Base.
    """
    __tablename__ = 'users'
    email = Column(String(128), nullable=False, unique=True)
    password = Column(String(256), nullable=False)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)

    def __init__(self, email, password, first_name, last_name):
        """
        Initializes a new User instance.

        Parameters:
            email (str): The email address of the user.
            password (str): The password of the user.
            first_name (str): The first name of the user.
            last_name (str): The last name of the user.
        """
        super().__init__()
        self.email = email
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
