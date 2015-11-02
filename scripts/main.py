import xml.etree.cElementTree as ET

from dbfunctions import DBManager
from xmlfunctions import XMLParser

##set up some global variables

#set up a db connection with sqlalchemy
engine='mysql://root:Shirith46!@localhost/OCW'

#generate models for the given db
database = DBManager(engine)
session = database.Session()
Model = database.create_bindings()

#bind each table's generated class to some names so that we can use them
Region = Model.classes.ocwregions
Category = Model.classes.ocwcategories
Entry = Model.classes.ocwentries

#make sure that the database is empty before we start
database.empty_db()

#the path to our xml
xml_path = '/home/fraser/Code/ocw/xml.xml'

#get a handle to the data using ET
tree = ET.parse(xml_path)
root = tree.getroot()
parser = XMLParser(root)
parser.get_all(tree=root, tag='e')
print len(parser.found_elements['e'])
