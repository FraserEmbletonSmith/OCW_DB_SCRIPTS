from lxml import etree as ET
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbfunctions import Entry, Category, Region, empty_db, create_all
from slugify import slugify
from xmlfunctions import convert_to_unicode
from settings import *


from xmlfunctions import XMLParser
from csvparse import get_article_names, UnicodeReader
import pdb

#our database details
engine=create_engine("mysql://"+USERNAME+":"+PASSWORD+"@"+HOST+"/"+DATABASE_NAME+"?charset=utf8", echo=True)
empty_db(engine)
create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

#@TODO encapsulate this stuff in the xmlparser class
#the path to our xml
xml_path = PATH_TO_XML

# #get a handle to the data using ET
tree = ET.parse(xml_path)
root = tree.getroot()

parser = XMLParser(root)

#populate our database:
for counter, region in enumerate(parser.regions):
    if session.query(Region).count()<11:
        #don't make duplicate regions if the db wasn't emptied
        new_region = Region(title=region, url_component=slugify(region), display_order=counter)
        session.add(new_region)
session.commit()

for counter, category in enumerate(parser.categories):
    if session.query(Category).count()<11:
        new_category = Category(title=category, url_component=slugify(category), display_order=counter)
        session.add(new_category)
session.commit()

for entry in parser.entries:
    if entry.region:
        region = session.query(Region).filter(Region.title==entry.region).one()
    else:
        region = None
    if entry.category:
        category = session.query(Category).filter(Category.title==entry.category).one()
    else:
        category=None


    new_entry = Entry(title = entry.title,
                      content = entry.text,
                      reference_list = "; ".join(entry.references),
                      legacy_url_component = entry.slug,
                      is_contributor = 0,
                      audio_file = ", ".join(entry.audio),
                      contributors =entry.contributors,
                      entries = entry.xrefs,
                      is_crossref = int(entry.crossref),
                      )
    if region:
        new_entry.region_id = region.id
    if category:
        new_entry.category_id = category.id
    session.add(new_entry)
session.commit()

for contrib in parser.contributors:

    new_contrib = Entry(title = contrib.fullname,
                      content = contrib.text,
                      legacy_url_component = slugify(convert_to_unicode(contrib.fullname.lower())),
                      is_contributor = 1,
                      is_crossref = 0
                      )
    session.add(new_contrib)
session.commit()
    
# for entry in parser.entries:
#     try:
#         db_entry = session.query(Entry).filter(Entry.legacy_url_component==slugify(convert_to_unicode(entry.title.lower()))).one()
#     except:
#         db_entry =None
#         pass
#     contribs = session.query(Entry).filter(Entry.legacy_url_component in entry.contributors)
#     contributors = [contrib.id for contrib in contribs]
#     validated_contributors = [contrib for contrib in contributors]
#     if db_entry is not None and validated_contributors is not []:
#         db_entry.contributors=validated_contributors
#         session.add(db_entry)
#
# session.commit()


