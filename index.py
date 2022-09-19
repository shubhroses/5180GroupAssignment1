#Python 2.7.3
import re
import os
import collections
import time

class index:
    def __init__(self,path):
        pass

    def buildIndex(self):
        #function to read documents from collection, tokenize and build the index with tokens
        #index should also contain positional information of the terms in the document --- term: [(ID1,[pos1,pos2,..]), (ID2, [pos1,pos2,…]),….]
        #use unique document IDs

        """
        1. Tokenize
            a. For each document in collection
                - Open the document
                - Get each token and its position, ignoring punctuation and numerals
                - Make token lowercase
                - map[term].append((ID1, [pos1, pos2, pos3]))
        """
        pass

    def and_query(self, query_terms):
	    #function for identifying relevant docs using the index
        pass

    def print_dict(self):
        #function to print the terms and posting list in the index
        pass

    def print_doc_list(self):
	    # function to print the documents and their document id
        pass