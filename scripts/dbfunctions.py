import contextlib

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


class DBManager():
    '''
    a class which handles database operations and stores relevant info
    '''
    def __init__(self, engine):
        self.engine = create_engine(engine, echo=True)
        self.Base = None
        self.Session = sessionmaker(bind=engine)
        self.Tables = None

    def create_bindings(self):
        #autogenerate models for a given database and set this instance's automap_base to self.Base
        self.Base = automap_base()
        self.Base.prepare(self.engine, reflect=True)
        self.Tables = self.Base.metadata.tables
        return self.Base

    def empty_db(self):
        #deletes all data from database
        meta = self.Base.metadata

        with contextlib.closing(self.engine.connect()) as con:
            #establish a connection and close it when we're done with it
            trans = con.begin()

            #reverse the order of the tables so that children are deleted before parents
            for table in reversed(meta.sorted_tables):
                con.execute(table.delete())
            trans.commit()

    def save_object(self, session, type, **kwargs):
        #a function which saves an instance of the given type with the given kwargs
        if type in self.Tables:
            session.add(type(**kwargs))
            session.commit()
            return session.query(type, **kwargs)
        else:
            raise AttributeError
