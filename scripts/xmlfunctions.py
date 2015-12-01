from lxml import etree as ET
from collections import namedtuple
import pdb
from more_itertools import unique_everseen
from csvparse import get_article_names
from csvparse import strip_everything
from slugify import slugify
from xml.etree.cElementTree import ParseError
from titlecase import titlecase
from settings import *
import string


#namedtuple to hold our entry and contributor objects
Entry = namedtuple('entry', ['text', 'region', 'category', 'title', 'id', 'xrefs', 'audio', 'slug', 'contributors', 'references', 'crossref', 'abbrev'])
Contributor = namedtuple('contributor', ['forename', 'surname', 'fullname', 'initial', 'text'])
class XMLParser():
    '''
    a class to provide methods for, and hold the results of, our xml searching
    '''
    #@TODO finish entry namedtuple
    regions = ['France', 'Italy', 'Portugal', 'Germany', 'Spain', 'Latin America', 'Australia/New Zealand', 'Rest of World', 'Rest of Europe', 'North America', 'South Africa']
    categories = ['Tasting', 'Grape varieties', 'Vine-growing/Viticulture', 'History', 'Academe', 'Winemaking/Oenology', 'Wine and the consumer', 'Labelling terms', 'People / Producers / Brands', 'Packaging', 'Miscellaneous' ]



    def __init__(self, tree):
        self.found_elements = {}
        self.entries = []
        self.contributors = []
        self.found_regions = []
        self.tree = tree

        #preliminary list of entries, populated from the list of entries at the start of the book, with their region and
        #category info and a list of contributors
        self.get_relationships()

        #get the list of contributors, and populate their names, initials and the body of their descriptions
        self.get_contributors()

        #complete the list of entries, adding their text as strings of xml. Also populates their references as a list of strings,
        # their contributors as lists of slugified names, and their audio file as a filename
        self.get_entries()

        #slugify the entries' titles
        self.populate_slugs()

        #parse the text in the xml entries to html, including links and formatting, as well as populating the list of
        #xrefs for each entry
        self.parse_xml()
        self.unicodify_constants()

    def get_all(self, tree, tag):
        '''
        Takes an element and recursively searches it for a given tag, then returns a list of all the
        elements which have that tag, as an item in the instance's found_elements dict. The key will be the name of the tag.
        '''
        self.found_elements[tag] = tree.findall(".//"+tag)

    def get_relationships(self):
        '''
        populate self.entries with entry namedtuples, along with their relationships if applicable
        '''
        self.get_all(self.tree,'div2')
        region_entries = []
        category_entries = []
        divs = self.found_elements['div2']
        try:
            for div in divs:
                name = div.find('titleGroup').find('title').find('p').text
                if name in self.regions:
                    item_ones = div.find('p').find('list').find('list1')
                    for item in item_ones:
                        title = item.find('p').find('xrefGrp').find('xref').text.rstrip('.')
                        title = title.rstrip(",")
                        id = item.find('p').find('xrefGrp').find('xref').get('ref')
                        # found = False
                        # for entry in self.entries:
                        #     if entry.id == id:
                        #         new_entry = entry._replace(region = name, title=title)
                        #         self.entries.remove(entry)
                        #         self.entries.append(new_entry)
                        #         found = True
                        # if not found:
                        region_entries.append(Entry(text=None, region=name, category=None, title=title, id = id, xrefs=None, slug=None, audio=None, contributors=None, references = None, crossref=None, abbrev=None))



                elif name in self.categories:
                    item_ones = div.find('p').find('list').find('list1')
                    for item in item_ones:
                        title = item.find('p').find('xrefGrp').find('xref').text.rstrip('.')
                        title = title.rstrip(",")
                        id = item.find('p').find('xrefGrp').find('xref').get('ref')
                        # found = False
                        # for entry in self.entries:
                        #     if entry.id == id:
                        #         new_entry = entry._replace(category = name)
                        #         self.entries.remove(entry)
                        #         self.entries.append(new_entry)
                        #         found = True
                        # if not found:
                        category_entries.append(Entry(text=None, region=None, category=name, title=title, id=id, xrefs=None, slug=None, audio=None, contributors=None, references=None, crossref=None, abbrev=None))
                else:
                    self.found_regions.append(name)



        except AttributeError:
                pass
        entries = []
        for c_entry in category_entries:
            found = False
            for r_entry in region_entries:
                if c_entry.id ==r_entry.id:
                    new_entry = c_entry._replace(region=r_entry.region, id=c_entry.id, category=c_entry.category)
                    entries.append(new_entry)
                    found = True
            if found == False:
                entries.append(c_entry)
        for r_entry in region_entries:
            found = False
            for c_entry in category_entries:
                if c_entry.id ==r_entry.id:
                    new_entry = r_entry._replace(category=c_entry.category, id = r_entry.id, region=r_entry.region)
                    entries.append(new_entry)
                    found = True
            if found == False:
                entries.append(r_entry)
        self.entries = self.deduplicate(entries)

    def deduplicate(self, entries):
        deduped_entries = []
        for entry in entries:
            if entry.id not in [e.id for e in deduped_entries]:
                deduped_entries.append(entry)
        return deduped_entries





    def get_entries(self):
        '''
        populate self.entries with the body of the entries, adding entries which don't exist
        '''
        self.get_all(self.tree, 'e')
        e = self.found_elements['e']
        entries = []
        for e in e:
            contributors = self.get_contributor_list(e.findall(".//*[@role='authors']"))

            references = self.get_reference_list(e.findall(".//*[@role='bibliography']"))
            audio = self.get_audio(e)
            id = e.get('id')
            title = self.get_node_text(e.find('headwordGroup').find('headword')).rstrip('.').rstrip(",")
            crossref = e.find('section').get('role')=='crossRef'
            abbrev = e.find('headwordGroup').find('headword').get("abbrev") == 'y'
            crossref = crossref
            text = self.get_text(e)
            xrefs = None
            found = False
            #putting title=title here seems to get rid of all duplicate entries by title for some reason
            for entry in self.entries:
                if entry.id == id:
                    new_entry = entry._replace(title=title, text=text, xrefs=xrefs, references=references, contributors=contributors, audio=audio, crossref=crossref, id=id, abbrev=abbrev)
                    entries.append(new_entry)
                    found = True
            if found==False:
                    entries.append(Entry(title=title, text=text, xrefs=xrefs, region=None, category=None, id=id, slug=None, audio=audio, references=references, contributors=contributors, crossref=crossref, abbrev=abbrev))
        self.entries = entries

    def tags(self, elem):
        if elem.getchildren():
            return [elem.tag for elem in elem.getchildren()]
        else:
            return []

    def get_text(self, e):
        '''
        retrieves an entry's text as xml
        '''
        body = e.find('section').find('textMatter')
        figure =get_all(e, 'figure')
        ps = get_all(body, 'p')
        p_with_titles=[]
        try:
            for p in ps:
                if p.getparent().tag=='title':
                    p_with_titles.append(p.getparent())
                else:
                    p_with_titles.append(p)

        except AttributeError:
            pass
        ps = p_with_titles
        if len(figure)>0:
            ps.extend(figure)
        text = "<span>"+' '.join([self.get_node_xml(p) for p in ps])+"</span>"


        return text

    def check_against_article_names(self):
        '''
        checks the names of entries against the definitive csv list
        '''
        print 'Number of entries parsed from xml is {0}'.format(len(self.entries),)

        #csv article names
        article_names = get_article_names()

        #xml article names
        string_entries = [entry.title for entry in self.entries]

        #slugify the xml names and convert to unicode
        slug_entries = [slugify(convert_to_unicode(entry)) for entry in string_entries]

        #entries which match between the two lists
        entries = [entry for entry in slug_entries if entry in article_names]

        #entries which don't match between the 2 lists
        discarded_entries = [entry for entry in slug_entries if entry not in article_names]
        print 'After checking against the csv list, there are {0} entries which match'.format(len(entries),)
        return discarded_entries

    def get_node_xml(self, node):
        #return's a nodes xml as a string
        return ET.tostring(node, encoding = 'utf-8', method='xml')

    def get_node_text(self, node):
        #returns all of a node's text with no xml
        return ET.tostring(node, encoding='utf-8', method='text')

    def parse_xml(self):
        '''
        Goes through all current entries, and parses xml xrefs into html links in the text of the entries. Uses the
         acref as the destination link, needs to then be translated into the slug for the corresponding article. Also
         parses image links to html links.
        '''

        new_entries = []
        #loop through entries to get their text
        for entry in self.entries:
            #read the text as an xml element
            xmltext = ET.fromstring(entry.text)
            xrefs = self.get_xrefs(xmltext)
            xmltext = self.translate_entry_links(xmltext)
            xmltext = self.translate_media_links(xmltext)
            xmltext = self.replace_sc(xmltext)
            xmltext = self.insert_tags(xmltext)
            xmltext = self.insert_titles(xmltext)

            #we now write the entry's text as non-xml. Since our xml elements now contain their corresponding html
            #elements as text, they are written in the place of the xml elements
            new_entries.append(entry._replace(text=self.get_node_text(xmltext), xrefs=xrefs))
        self.entries = new_entries
        new_contributors = []
        for con in self.contributors:
            #read the text as an xml element
            xmltext = ET.fromstring(con.text)
            xmltext = self.translate_entry_links(xmltext)
            xmltext = self.translate_media_links(xmltext)
            xmltext = self.replace_sc(xmltext)
            xmltext = self.insert_tags(xmltext)
            xmltext = self.insert_titles(xmltext)

            #we now write the entry's text as non-xml. Since our xml elements now contain their corresponding html
            #elements as text, they are written in the place of the xml elements
            new_contributors.append(con._replace(text=self.get_node_text(xmltext)))
        self.contributors = new_contributors

    def insert_tags(self, node):
        '''
        adds html tags in the place of the xml tags to the text of the xml, meaning they are not deleted by get_node_text()
        Used for tags that we want to keep
        '''
        tags_to_keep = ['i', 'b', 'p']
        for tag in tags_to_keep:
            elems = get_all(node, tag)
            for elem in elems:
                self.wrap_element(elem, tag)
        return node

    def insert_titles(self, node):
        '''
        inserts H2 tags at titlegroups
        '''
        elems = get_all(node, 'title')
        for elem in elems:
            self.wrap_element(elem, 'title', retain=False, new_tag='h2')
        return node


    def wrap_element(self, element, tag, retain=True, new_tag=None):

        old_text =element.text or ''
        old_tail =element.tail or ''
        if retain == True:
            opening_tag = '<'+tag+'>'
            closing_tag = '</'+tag+'>'
            # if old_text and old_tail:
            element.text = convert_to_unicode(opening_tag+old_text)
            element.tail = convert_to_unicode(closing_tag+old_tail)
            # elif old_text:
            #     element.text = convert_to_unicode(opening_tag+old_text+closing_tag)
            # return element
        else:
            opening_tag = '<'+new_tag+'>'
            closing_tag = '</'+new_tag+'>'
            # if old_text and old_tail:
            element.text = convert_to_unicode(opening_tag+old_text)
            element.tail = convert_to_unicode(closing_tag+old_tail)
            # elif old_text:
            #     element.text = convert_to_unicode(opening_tag+old_text+closing_tag)


            return element


    def get_xrefs(self, node):

        grps = get_all(node, 'xrefGrp')
        xrefs = []
        for grp in grps:
            refs = get_all(grp, 'xref')
            for ref in refs:
                id = ref.get('ref')
                if id is not None:
                    if len(ref)>0:
                        text = convert_to_unicode(ref[0].text)
                    else:
                        text = convert_to_unicode(ref.text)
                    link = self.convert_link(id)
                    if text is not None and link is not None:
                        #before converting the link to html, we convert the id to be of the form "/ocw/{{slug}}"
                        link = "<a href="+link+">"+text+"</a>"
                        xrefs.append(link)
        return "; ".join(xrefs)

    def translate_entry_links(self, xmltext):
        #links are wrapped in xrefgrps, and there can be multiple xrefgrps in a text
            grps = get_all(xmltext, 'xrefGrp')

            for grp in grps:
                refs = get_all(grp, 'xref')
                #xrefs contain the actual link. Sometimes there are multiple xrefs within a single xrefgrp.
                if refs:
                    pretext = convert_to_unicode(grp.text)
                    links = ""
                    for counter, ref in enumerate(refs):

                        if len(list(ref))>0:
                            #sometimes refs contain other elements, like <sc> or <i> - we want to preserve these
                            refinnertext = convert_to_unicode(ref[0].text)
                        else:
                            refinnertext = convert_to_unicode(ref.text)
                        if counter != len(refs) - 1:
                            posttext = convert_to_unicode(ref.tail)
                        else:
                            posttext = convert_to_unicode(grp.tail)

                        #this is the id of the article being linked to
                        id = ref.get('ref')

                        #before converting the link to html, we convert the id to be of the form "/ocw/{{slug}}"
                        id = self.convert_link(id)

                        #construct the html link elements and surrounding text
                        links += u'<a href="{0}">{1}</a>{2}'.format(id, refinnertext, posttext)
                    #delete all of the attributes of the xrefgrp
                    grp.clear()
                    grp.text = pretext+links
            return xmltext

    def translate_media_links(self, node):
        media = get_all(node, 'graphic')
        if media:
            for img in media:
                id = img.get("sysId")
                link = self.convert_media_link(id)
                img.clear()
                img.text = link
        return node

    def populate_slugs(self):
        '''
        populates the slug field for each entry with the slugified title
        '''
        entries = []
        for entry in self.entries:
            if entry.abbrev:
                title = convert_to_unicode(entry.title).upper()
            else:
                title = titlecase(convert_to_unicode(entry.title))
            slug = slugify(title)
            entries.append(entry._replace(slug=slug, title=title))
        self.entries = entries

    def replace_sc(self, node):
        sc_list = get_all(node, 'sc')
        for sc in sc_list:
            text = sc.text
            if text:
                span = self.convert_sc(text)
                try:
                    sc.text = span
                except ValueError:
                    pdb.set_trace()
        return node

    def convert_sc(self, text):
        return '<span class="ocw-inline-term">'+text+'</span>'

    def convert_link(self, id):
        '''
        takes an id and converts it into a link of the form "/ocw/{{slug}}". Used for links to other articles, not media
        '''
        for entry in self.entries:
            if id == entry.id:
                slug = entry.slug
                return "/ocw/detail/"+slug

    def convert_contributor_link(self, name):
        slug = slugify(convert_to_unicode(name))
        return '<a href="'+ENTRY_URL_PREFIX+"/"+slug+'">'+convert_to_unicode(name)+'</a>'

    def convert_media_link(self, media):
        return '<img src=/ocw/images/"'+media+'">'

    def get_contributors(self):
        '''
        populates self.contributors with a list of Contributor NamedTuples
        '''
        miscMatter = get_all(self.tree, 'miscMatter')
        contriblist = []
        plist = []
        for misc in miscMatter:
            if misc.get('class') == "acknowledgements":
                if misc.find('titleGroup').find('title').find('p').text == "Contributors":
                    ps = get_all(misc.find('textMatter'), 'p')
                    plist.extend([p for p in ps if 'span' in self.tags(p)])
        self.contributors = [self.make_contributor(p) for p in plist]

    def make_contributor(self, node):
        '''
        populates and returns a contributor namedtuple for the given node
        '''
        initial = node.find('span').text
        node.remove(node.find('span'))
        nameGrp = node.find('nameGrp')
        text = "<p>"+self.get_node_xml(node)+"</p>"
        forename = nameGrp.get('foreNames')
        surname = nameGrp.get('mainName')
        fullname = forename+" "+surname
        return Contributor(initial=initial, text=text, forename=forename, surname=surname, fullname=fullname)



    def get_contributor_list(self, node):
        '''
        gets a list of contributprs' initials from a given entry node and returns the list
        '''
        contributors=[]
        for Node in node:
            authors = get_all(Node,"textMatter")
            for author in authors:
                for name in get_all(author, 'nameGrp'):
                    contributors.append(self.get_node_text(name))
        contributors = [self.remove_punctuation(c) for c in contributors]
        contributors = "; ".join([self.convert_contributor_link(con) for con in contributors])

        return contributors

    def remove_punctuation(self, text):
        exclude = set(string.punctuation)
        s = ''.join(ch for ch in text if ch not in exclude)
        return s

    def get_audio(self, node):
        '''
        gets a list of audio files for a given node and returns it as a list of file names as strings
        '''
        filerefs = get_all(node,'fileRef')
        return [info.get('fileName') for info in filerefs]


    def get_reference_list(self, node):
        '''
        Gets a list of references as strings from a given node and returns it in the form {{author}}, {{title}}
        '''
        references = []
        for Node in node:
            if Node is not None:
                bibitems = get_all(Node, 'bibItem')
                for item in bibitems:
                    author = item.get('author')
                    book = item.get('title')
                    if author and book:
                        reference = author +", "+book
                        references.append(reference)
        return references

    def unicodify_constants(self):
        self.regions = [convert_to_unicode(reg) for reg in self.regions]
        self.categories = [convert_to_unicode(cat) for cat in self.categories]


def convert_to_unicode(s):
    if not isinstance(s, unicode):
        if s is not None:
            return unicode(s, 'utf-8')
    return s or ''

def get_all(tree, tag):
    '''
    returns all of the elements with a given tag nested inside the give tree
    '''
    return tree.findall(".//"+tag)




