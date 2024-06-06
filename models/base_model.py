#!/usr/bin/python3
"""Base model for the project Book Swap Connect"""
from datetime import datetime
import uuid
import models
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

time = "%A, %d %B %Y %I:%M%p"

Base = declarative_base()


class BaseModel:
    """This is the base class where other classes will inherit from"""
    id = Column(String(60), primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    def __init__(self):
        """Initializes the base model.

        Attributes:
            id (str): Unique identifier for each object, generated using UUID.
            created_at (datetime): Timestamp when the object is created.
            updated_at (datetime): Timestamp when the object is last updated.
        """
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.id = str(uuid.uuid4())

    def __str__(self):
        """Returns a string representation of the object.

        Returns:
            str: A string that represents the object instance.
        """
        return f"[{self.__class__.__name__}] ({self.id}) {self.__dict__}"

    def save(self):
        """Updates the 'updated_at' attribute with the current time and date,
        and saves the object to the storage.
        """
        self.updated_at = datetime.now().strftime(time)
        models.storage.new(self)
        models.storage.save()

    def to_dict(self):
        """Converts the object to a dictionary format.

        Returns:
            dict: A dictionary containing all key/value pairs of the instance.
        """
        new_dict = self.__dict__.copy()
        if 'created_at' in new_dict:
            new_dict['created_at'] = new_dict['created_at'].strftime(time)
        if 'updated_at' in new_dict:
            new_dict['updated_at'] = new_dict['updated_at'].strftime(time)
        new_dict['class'] = self.__class__.__name__
        if '_sa_instance_state' in new_dict:
            del new_dict['_sa_instance_state']
        return new_dict

    def delete(self):
        """Deletes the object from the storage."""
        models.storage.delete(self)
