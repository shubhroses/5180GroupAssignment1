import re
import os
import collections
import time
import math

class index:
    def __init__(self, path):
        self.indToDoc = {}
        self.oldPostingList = collections.defaultdict(list)
        self.curDocID = 0
        self.path = path
        self.idToTerm = {}
        self.curTermIndex = 0
        self.termToId = {}  
        self.docToVec = {}
        self.newPostingList = collections.defaultdict(list)

        self.createNewPostringList()


    def tokenize(self, f, newPath):
        #Returns [(term, pos), (term, pos) ...]
        terms = []
        with open(newPath + "/" + f) as file:
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

    def createOldPostingList(self):
        stopList = set()
        stopTuples = self.tokenize("stop-list.txt", ".")
        for t, p in stopTuples:
            stopList.add(t)

        for f in os.listdir(self.path):
            self.indToDoc[self.curDocID] = f

            # Returns [(word, pos), (word, pos) ...]
            terms = self.tokenize(f, self.path)

            # create map {word:[pos1, pos2, pos3]}
            wordToPos = collections.defaultdict(list)
            for word, pos in terms:
                if word in stopList: #Remove all stop words
                    continue
                wordToPos[word].append(pos)

            # append to posting list {term : [(docID1, [pos1, pos2, pos3, pos4])]}
            for term, arr in wordToPos.items():
                self.oldPostingList[term].append((self.curDocID, wordToPos[term]))

            # For every file update id 
            self.curDocID += 1

    def convertDocumentsToVector(self):
        for k in self.indToDoc.keys():
            self.docToVec[k] = len(self.idToTerm)*[float(0)]

        for k, v in self.newPostingList.items():
            idf = v[0]
            for i in range(1, len(v)):
                t = v[i]
                doc, w = t[0], t[1]
                self.docToVec[doc][k] = idf*w

    def createNewPostringList(self):
        startTime = time.time()
        self.createOldPostingList()
        for k,v in self.oldPostingList.items():
            # if k in stopList:
            #     continue
            self.idToTerm[self.curTermIndex] = k
            self.newPostingList[self.curTermIndex].append(math.log10(len(self.indToDoc)/len(v)))
            
            for docId, posList in v:
                self.newPostingList[self.curTermIndex].append((docId, 1 + math.log10(len(posList)), posList))
            self.curTermIndex += 1
        for id, term in self.idToTerm.items():
            self.termToId[term] = id
        endTime = time.time()
        print(f"Index built in {endTime - startTime} seconds.")

        self.convertDocumentsToVector()

    def cosine_similarity(self, v1,v2):
        "compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)"
        sumxx, sumxy, sumyy = 0, 0, 0
        for i in range(len(v1)):
            x = v1[i]; y = v2[i]
            sumxx += x*x
            sumyy += y*y
            sumxy += x*y
        if sumxx == 0 or sumyy == 0:
            return 0
        return sumxy/math.sqrt(sumxx*sumyy)

    def get_query_vector(self, query_terms):
        query_terms = [word.lower() for word in query_terms]
        termToFreq = {}
        for t in query_terms:
            termToFreq[t] = termToFreq.get(t, 0) + 1

        queryVector = len(self.idToTerm)*[float(0)]
        for term, freq in termToFreq.items():
            if term in self.termToId:
                w = 1 + math.log10(freq)
                idf = self.newPostingList[self.termToId[term]][0]
                queryVector[self.termToId[term]] = w*idf
        return queryVector

    def exact_query(self, query_terms, k):
        startTime = time.time()
        query_terms = [word.lower() for word in query_terms]

        queryVector = self.get_query_vector(query_terms)

        docToSimilarity = []
        for doc, vec in self.docToVec.items(): # for champions list only look at 
            docToSimilarity.append((doc, self.cosine_similarity(queryVector, vec)))
        # for d, s in docToSimilarity:
        #     print(f"doc: {self.indToDoc[d]}, similarity: {s}")
        docToSimilarity.sort(key = lambda x:x[1], reverse=True)
        endTime = time.time()
        print(f"Query executed in {endTime - startTime} seconds.")
        return [self.indToDoc[t[0]] for t in docToSimilarity[:k]]


    def inexact_query_champion(self, query_terms, k):
        queryVector = self.get_query_vector(query_terms)

a = index("collection")
query_terms = ["a", "cat", "jumped"]

print(a.exact_query(query_terms, 2))
