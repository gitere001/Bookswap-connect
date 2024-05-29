from os import getenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base
from models.user import User
from models.book import Book
from models.swap_request import SwapRequest

classes = {
    "User": User,
    "Book": Book,
    "SwapRequest": SwapRequest,
}


class DBStorage:
    __engine = None
    __session = None

    def __init__(self):
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
        new_dict = {}
        for clss in classes:
            if cls is None or cls in classes[clss] or cls is clss:
                objs = self.__session.query(classes[clss].all())
                for obj in objs:
                    key = obj.__class__.__name__ + '.' + obj.id
                    new_dict[key] = obj
        return (new_dict)

    def new(self, obj):
        self.__session.add(obj)

    def find(self, cls, *args, **kwargs):
        return self.__session.query(cls).filter(*args, **kwargs).all()

    def save(self):
        self.__session.commit()

    def delete(self, obj=None):
        if obj:
            self.__session.delete(obj)

    def reload(self):
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
        self.__session.remove()

    def rollback(self):
        self.__session.rollback()

    def get(self, cls, id):
        if cls not in classes.values():
            return None
        return self.__session.query(cls).filter_by(id=id).first()

    def count(self, cls=None):
        all_class = classes.values()
        if not cls:
            count = 0
            for clas in all_class:
                count += len(self.all(clas).values())
        else:
            count = len(self.all(cls).values())
        return count
