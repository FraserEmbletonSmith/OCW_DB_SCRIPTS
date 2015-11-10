from slugify import slugify
import unicodedata
import sys
import csv,codecs
from settings import PATH_TO_CSV

tbl = dict.fromkeys(i for i in xrange(sys.maxunicode)
                      if unicodedata.category(unichr(i)).startswith('P'))
def remove_punctuation(text):
    return text.translate(tbl)

def strip_accents(input_str):
    if not isinstance(input_str, unicode):
        input_str = unicode(input_str, "utf-8")
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

def strip_everything(s):
    s = strip_accents(s)
    s = s.replace(u"\u2018", "'").replace(u"\u2019", "'")
    s = s.replace(" ", "").replace("-", "").replace(",", "").replace(".", "")
    s = remove_punctuation(s)
    if not isinstance(s, unicode):
        s = unicode(s, "utf-8")
    return s

class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
    def next(self):
        '''next() -> unicode
        This function reads and returns the next line as a Unicode string.
        '''
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self

def get_article_names():
    file = PATH_TO_CSV

    reader = UnicodeReader(open(file), delimiter = ',')
    reader.next()

    article_names = [x[0] for x in reader if x[1] != 'DELETE']

    article_names = [slugify(x) for x in article_names]


    return article_names

get_article_names()



