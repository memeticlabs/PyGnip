# -*- coding: utf-8 -*-
import pymongo
from pygnip.config import MainConfig as settings


class MongoPool():

    """Mongo Connection Pool"""

    MONGO_DB = settings.MONGODB_DATABASE
    
    def engine(self, host, port):
        key = 'connection_%s_%s' % (host, port)
        con = getattr(self, key, None)
        if not con:
            if not host or not port or not type(port) == int:
                raise Exception(
                    "Sample arguments: Host: '127.0.0.1' Port: 27017")

            con = pymongo.Connection(host, port, safe=True)
            setattr(self, key, con)

        return con

    def get(self, name):
        if not name:
            return None

        connection = getattr(self, name, None)
        if connection:
            return connection

        if name == settings.MONGODB_DATABASE:
            return self.create(
                database=settings.MONGODB_DATABASE,
                host=settings.MONGODB_HOST,
                port=settings.MONGODB_PORT)

        else:
            # add other databases of future here
            pass

        return self.create(database=name)

    def create(self, database, host=None, port=None):
        engine = self.engine(
            host=host or settings.MONGODB_HOST,
            port=port or settings.MONGODB_PORT)

        # if not database in engine.database_names():
        #     raise Exception("Error finding the program %s" % database)

        db = getattr(engine, database, None)
        setattr(self, database, db)
        return db

    def __call__(self, name, collection=None):
        db = self.get(name)

        if not isinstance(db, pymongo.database.Database):
            raise Exception(
                "Database using a reserved name %s. Need to rename the database" % name)

        if not collection:
            return db
        else:
            return getattr(db, collection, None)

class RedisPool():
    pass


mongodbapi = MongoPool()
redisdbapi = RedisPool()
