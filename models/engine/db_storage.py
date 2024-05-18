from os import getenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models.base_model import Base
from models.user import User

classes = {
    "User": User,
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
        self.__engine = create_engine('mysql+mysqldb://{}:{}@{}/{}'.format(BOOKSWAP_MYSQL_USER, BOOKSWAP_MYSQL_PWD, BOOKSWAP_MYSQL_HOST, BOOKSWAP_MYSQL_DB))
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