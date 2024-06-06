from os import getenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base
from models.user import User
from models.book import Book
from models.swap_request import SwapRequest
from models.message import Message

classes = {
    "User": User,
    "Book": Book,
    "SwapRequest": SwapRequest,
    "Message": Message,
}


class DBStorage:
    __engine = None
    __session = None

    def __init__(self):
        """
        Initializes the DBStorage instance.
        Sets up the database engine and drops all tables if the environment
        is 'test'.
        """
        BOOKSWAP_MYSQL_USER = getenv('BOOKSWAP_MYSQL_USER')
        BOOKSWAP_MYSQL_PWD = getenv('BOOKSWAP_MYSQL_PWD')
        BOOKSWAP_MYSQL_HOST = getenv('BOOKSWAP_MYSQL_HOST')
        BOOKSWAP_MYSQL_DB = getenv('BOOKSWAP_MYSQL_DB')
        BOOKSWAP_ENV = getenv('BOOKSWAP_ENV')
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.
                                      format(BOOKSWAP_MYSQL_USER,
                                             BOOKSWAP_MYSQL_PWD,
                                             BOOKSWAP_MYSQL_HOST,
                                             BOOKSWAP_MYSQL_DB))
        if BOOKSWAP_ENV == "test":
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """
        Queries and returns a dictionary of all objects of a given class, or
        all objects if no class is specified.

        Parameters:
            cls (str or None): The class name to filter objects by.

        Returns:
            dict: A dictionary of all queried objects.
        """
        new_dict = {}
        for clss in classes:
            if cls is None or cls in classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss].all())
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        return (new_dict)

    def new(self, obj):
        """
        Adds a new object to the current database session.

        Parameters:
            obj: The object to add to the session.
        """
        self.__session.add(obj)

    def find(self, cls, *args, **kwargs):
        """
        Finds and returns objects of a given class based on provided filters.

        Parameters:
            cls (class): The class to query.
            *args: Variable length argument list for filters.
            **kwargs: Arbitrary keyword arguments for filters.

        Returns:
            list: A list of objects that match the filters.
        """
        return self.__session.query(cls).filter(*args, **kwargs).all()

    def save(self):
        """
        Commits the current database session.
        """
        self.__session.commit()

    def delete(self, obj=None):
        """
        Deletes an object from the current database session.

        Parameters:
            obj: The object to delete from the session.
        """
        if obj:
            self.__session.delete(obj)

    def reload(self):
        """
        Reloads the database by creating all tables and initializing the
        session.
        """
        Base.metadata.create_all(self.__engine)
        sess_factory = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sess_factory)
        self.__session = Session

        inspector = inspect(self.__engine)
        existing_tables = inspector.get_table_names()

        for clss in classes.values():
            table_name = clss.__tablename__
            if table_name not in existing_tables:
                clss.__table__.create(self.__engine)

    def close(self):
        """
        Closes the current database session.
        """
        self.__session.remove()

    def rollback(self):
        """
        Rolls back the current database session.
        """
        self.__session.rollback()

    def get(self, cls, id):
        """
        Retrieves an object by class and ID.

        Parameters:
            cls (class): The class of the object to retrieve.
            id (int): The ID of the object to retrieve.

        Returns:
            object or None: The object if found, otherwise None.
        """
        if cls not in classes.values():
            return None
        return self.__session.query(cls).filter_by(id=id).first()

    def count(self, cls, **filters):
        """
        Counts the number of objects in a given class based on provided
        filters.

        Parameters:
            cls (class): The class to count objects in.
            **filters: Arbitrary keyword arguments for filters.

        Returns:
            int: The count of objects that match the filters.
        """
        query = self.__session.query(cls).filter_by(**filters)
        return query.count()
