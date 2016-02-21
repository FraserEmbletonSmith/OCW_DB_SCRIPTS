#the name of the datbase
DATABASE_NAME = "OCW"

#username for db
USERNAME = "root"

#password for dv
PASSWORD = "Shirith46!"

#host for db
HOST = "localhost"

#path to xml file
PATH_TO_XML = "C:/Users/Fraser/code/ocw/xml.xml"

#path to csv file - only needed if you want to run the compare to csv funtion
PATH_TO_CSV = "C:/Users/Fraser/code/ocw/csv.csv"

#this prefix would give entry urls of the from <a href="/ocw/detail/{{entry_slug}}>{{entryname}}</a>
ENTRY_URL_PREFIX = "/ocw/detail"

#this prefix would give image urls of the from <img src="/imgages/{{name_of_image_file}}>
IMAGE_URL_PREFIX = "/images/"

#if this is set to True, the script will attempt to drop all tables in the database each time you run it
#and recreate them
DROP_ALL_TABLES = True

#if this is set to True, the script will clean the database when it is run
EMPTY_DB = True




