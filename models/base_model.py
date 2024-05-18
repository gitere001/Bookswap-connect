#!/usr/bin/python3
"""Base model for the project Book Swap Connect"""
from datetime import datetime
import uuid
import models
import sqlalchemy
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
        """initializing the base model"""
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.id = str(uuid.uuid4())

    def __str__(self):
        """string representation of a class"""
        return f"[{self.__class__.__name__}] ({self.id}) {self.__dict__}"

    def save(self):
        """updates attribute 'updated_at' with current time and date"""
        self.updated_at = datetime.now().strftime(time)

    def to_dict(self):
        new_dict = self.__dict__.copy()
        if 'created_at' in new_dict:
            new_dict['created_at'] = new_dict['created_at'].strftime(time)
        if 'updated_at' in new_dict:
            new_dict['updated_at'] = new_dict['updated_at'].strftime(time)
        new_dict['class'] = self.__class__.__name__
        if '_sa_instance_state' in new_dict:
            del new_dict['_sa_instance_state']
        return new_dict


b1 = BaseModel()
print(b1)
print(b1.to_dict())
