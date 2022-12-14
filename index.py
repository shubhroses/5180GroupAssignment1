#Python 2.7.3
import re
import os
import collections
import time

o = open("output.txt", "a")
class index:
    def __init__(self,path):
        self.indToDoc = {}
        self.postingList = collections.defaultdict(list)
        self.curDocId = 0
        self.path = path
        self.buildIndex()

    def tokenize(self, f):
        #Returns [(term, pos), (term, pos) ...]
        terms = []
        with open(self.path + "/" + f) as file:
            line = file.readline()
            i = 0
            while line:
                # Regex to match only strings and spaces 
                line = re.sub(r'[^A-Za-z\s]+', '', line)
                for word in line.split():
                    terms.append((word.lower(), i))
                    i += 1
                line = file.readline() 
        return terms

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
        startTime = time.time()
        for f in os.listdir(self.path):
            # Assign each document a unique document ID
            self.indToDoc[self.curDocId] = f

            # Returns [(word, pos), (word, pos) ...]
            terms = self.tokenize(f)

            # create map {word:[pos1, pos2, pos3]}
            wordToPos = collections.defaultdict(list)
            for word, pos in terms:
                wordToPos[word].append(pos)

            # append to posting list {term : [(docID1, [pos1, pos2, pos3, pos4])]}
            for term, arr in wordToPos.items():
                self.postingList[term].append((self.curDocId, wordToPos[term]))

            # For every file update id 
            self.curDocId += 1
        
        endTime = time.time()
        print(f"Index built in {endTime - startTime} seconds.", file=o)

    def merge_two(self, A, B):
        # Pointer for each posting list
        a = b = 0
        res = []
        while a < len(A) and b < len(B):
            # If documents not equal, increment pointer to lower documnet
            if A[a][0] > B[b][0]:
                b += 1
            elif A[a][0] < B[b][0]:
                a += 1
            # If documents equal, add to result
            else:
                res.append((A[a][0], []))
                a += 1
                b += 1
        return res

    def and_query(self, query_terms):
	    #function for identifying relevant docs using the index
        queryTimeStart = time.time()

        # List of postringlists for each query term 
        pl = [self.postingList[q] for q in query_terms]

        # Keep combining until one query list left 
        while len(pl) > 1:
            temp = []

            # Iterate through pl with increments of 2 to pair up postringLists
            for i in range(0, len(pl), 2):

                # If we are at last element, don't have another to pair with so just add it directly
                if i == len(pl) - 1:
                    temp.append(pl[i])
                # Merge the two postringlists and add to temp
                else:
                    temp.append(self.merge_two(pl[i], pl[i+1]))
            # Update postringList to be new combined lists
            pl = temp

        # Convert each document id in posting list to actual document name
        res = []
        if pl:
            for d, a in pl[0]:
                res.append(self.indToDoc[d])
        
        queryTimeEnd = time.time()

        # Print out what is required
        andStr = " AND ".join(query_terms)
        print(f"Results for the Query: {andStr}", file=o)
        print(f"Total Docs retrieved: {len(res)}", file=o)
        for doc in res:
            print(doc, file=o)
        print(f"Retreived in {queryTimeEnd - queryTimeStart} seconds", file=o)

        return res

    def print_dict(self):
        #function to print the terms and posting list in the index
        for term, list in self.postingList.items():
            print(term, list, file=o)

    def print_doc_list(self):
	    # function to print the documents and their document id
        for doc, name in self.indToDoc.items():
            print(f"Doc ID: {doc} ==> {name}", file=o)


a = index("collection")
x = a.and_query(['with', 'without', 'yemen'])
x = a.and_query(['with', 'without', 'yemen', 'yemeni'])
x = a.and_query(['dog'])
x = a.and_query(['italian', 'restaurants'])
x = a.and_query([])
o.close()

# x = a.print_dict()
# x = a.print_doc_list()
