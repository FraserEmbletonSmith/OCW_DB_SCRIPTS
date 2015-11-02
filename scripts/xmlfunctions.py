import xml.etree.cElementTree as ET
from collections import namedtuple
class XMLParser():
    '''
    a class to provide methods for, and hold the results of, our xml searching
    '''

    regions = []
    categories = []
    #namedtuple to hold our entry objects
    entry = namedtuple('entry', ['body', 'region', 'category'])

    def __init__(self, tree):
        self.found_elements = {}
        self.entries = []
        self.get__relationships()
        self.get_entries()

    def get_all(self, tree, tag):
        '''
        Takes an element and recursively searches it for a given tag, then returns a list of all the
        elements which have that tag, as an item in the instance's found_elements dict. The key will be the name of the tag.
        '''
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
        populates self.entries_regions and self.entries_categories, which are each a list of namedtuples
        '''
        pass

    def get_entries(self):
        '''
        populate self.entries with the body of the entries:
        '''
        pass