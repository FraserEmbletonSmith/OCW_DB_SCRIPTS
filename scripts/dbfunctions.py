import contextlib
import pdb
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT, VARCHAR, TIMESTAMP, TINYINT
from sqlalchemy import ForeignKey, Table
from settings import DROP_ALL_TABLES, EMPTY_DB




Base = declarative_base()

def empty_db(engine):
    #deletes all data from database
    if EMPTY_DB:
        with contextlib.closing(engine.connect()) as con:
            #establish a connection and close it when we're done with it
            trans = con.begin()
            meta = Base.metadata
            #reverse the order of the tables so that children are deleted before parents
            for table in reversed(meta.sorted_tables):
                con.execute(table.delete())
            trans.commit()
    if DROP_ALL_TABLES:
        Base.metadata.drop_all(bind=engine)

    if not DROP_ALL_TABLES and not EMPTY_DB:
        pass

class Category(Base):
    __tablename__='ocwcategories'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(VARCHAR(100))
    url_component = Column(VARCHAR(200))
    display_order = Column(Integer)
    legacy_url_component = Column(VARCHAR(50))


class Region(Base):
    __tablename__='ocwregions'

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(VARCHAR(100))
    url_component = Column(VARCHAR(200))
    display_order = Column(Integer)
    legacy_url_component = Column(VARCHAR(50))



class Entry(Base):
    __tablename__='ocwentries'

    id = Column(Integer, primary_key=True, nullable=False)
    legacy_url_component = Column(VARCHAR(50))
    title = Column(VARCHAR(50, collation='utf8_bin'))
    subtitle = Column(VARCHAR(50))
    content = Column(LONGTEXT(collation='utf8_bin'))
    category_id = Column(Integer, ForeignKey('ocwcategories.id'), nullable=True)
    region_id = Column(Integer, ForeignKey('ocwregions.id'), nullable=True)
    guid = Column(VARCHAR(50))
    posted = Column(TIMESTAMP())
    modified = Column(TIMESTAMP())
    published = Column(TIMESTAMP())
    publish = Column(TINYINT(), default=1)
    contributors = Column(LONGTEXT(collation='utf8_bin'))
    reference_list = Column(LONGTEXT(collation='utf8_bin'))
    entries = Column(LONGTEXT(collation='utf8_bin'))
    is_contributor = Column(TINYINT())
    audio_file = Column(VARCHAR(30))
    is_crossref = Column(TINYINT())

    #category = relationship('Category', backref=backref('entries', order_by=id))
    #region = relationship('Region', backref=backref('entries', order_by=id))

def create_all(engine):
    Base.metadata.create_all(engine)

#  contributors = relationship("Entry",
#                         secondary=entry_to_contributor,
#                         primaryjoin=id==entry_to_contributor.c.contributor_id,
#                         secondaryjoin=id==entry_to_contributor.c.entry_id,
#                         backref="parent_entries"
#     )
#  linked_entries = relationship("Entry",
#                         secondary=entry_to_entry,
#                         primaryjoin=id==entry_to_entry.c.linked_entry_id,
#                         secondaryjoin=id==entry_to_entry.c.parent_entry_id,
#                         backref="parent_entries"
#     )
#  entry_to_contributor = Table("ocw_entry_to_contributor", Base.metadata,
#     Column("contributor_id", Integer, ForeignKey("ocwentries.id"), primary_key=True),
#     Column("entry_id", Integer, ForeignKey("ocwentries.id"), primary_key=True)
# )
#
# entry_to_entry = Table("ocw_entry_to_entry", Base.metadata,
#     Column("linked_entry_id", Integer, ForeignKey("ocwentries.id"), primary_key=True),
#     Column("parent_entry_id", Integer, ForeignKey("ocwentries.id"), primary_key=True)
# )