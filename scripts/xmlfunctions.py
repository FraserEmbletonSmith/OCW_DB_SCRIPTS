import xml.etree.cElementTree as ET
from collections import namedtuple
Entry = namedtuple('entry', ['body', 'region', 'category', 'title'])
class XMLParser():
    '''
    a class to provide methods for, and hold the results of, our xml searching
    '''
    #@TODO Populate these by hand and finish entry namedtuple
    regions = ['France', 'Italy', 'Portugal', 'Germany', 'Spain', 'Latin America', 'Australia/New Zealand']
    categories = []
    #namedtuple to hold our entry objects


    def __init__(self, tree):
        self.found_elements = {}
        self.entries = []
        self.tree = tree
        self.get__relationships()
        self.get_entries()


    def get_all(self, tree, tag):
        '''
        Takes an element and recursively searches it for a given tag, then returns a list of all the
        elements which have that tag, as an item in the instance's found_elements dict. The key will be the name of the tag.
        '''
        #if there is no key for this tag in found elements, add it
        if tag not in self.found_elements.keys():
            self.found_elements[tag]=[]

        if len(list(tree)) == 1:
            if tree.tag == tag:
                self.found_elements[tag].append(tree)
                self.found_elements[tag] = [elem for elem in self.found_elements[tag]]
            else:
                self.found_elements[tag] = [elem for elem in self.found_elements[tag]]

        for branch in tree:
            if branch.tag == tag:
                self.found_elements[tag].append(branch)
            else:
                self.get_all(branch, tag)


    def get(self, tree, tag):
        '''
        Recursively searches a given tree for an element with the given tag, then returns it. Note that this returns the first
        element with the correct tag which it encounters.
        '''
        if tree.tag == tag:
            return tree
        else:
            for branch in tree:
                self.get(branch, tag)

    def get__relationships(self):
        '''
        populate self.entries with entry namedtuples, along with their relationships if applicable
        '''
        self.get_all(self.tree,'div2')

        divs = self.found_elements['div2']
        try:
            for div in divs:
                if div.find('titleGroup').find('title').find('p').text in self.regions:
                    region = div.find('titleGroup').find('title').find('p').text
                    item_ones = div.find('p').find('list').find('list1')
                    for item in item_ones:
                        title = item.find('p').find('xrefGrp').find('xref').text
                        found = False
                        for entry in self.entries:
                            if entry.title == title:
                                new_entry = entry._replace(region = region)
                                # self.entries.remove(entry)
                                self.entries.append(new_entry)
                                found = True
                        if not found:
                            self.entries.append(Entry(body=None, region=region, category=None, title=title))

        except AttributeError:
            pass

            # elif div.find('titleGroup').find('title').find('p') in self.categories:
            #     item_ones = div.find('p').find('list')
            #         for item in item_ones:



    def get_entries(self):
        '''
        populate self.entries with the body of the entries, adding entries which don't exist
        '''
        pass


