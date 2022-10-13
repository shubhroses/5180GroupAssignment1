import re
import os
import collections
import time
import math
import random

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

        self.championList = collections.defaultdict(list)
        self.r = 2
        self.docToVecChamp = {}
        self.champDocs = set()
        self.leadersArr = []
        self.leadersSet = set()
        self.docToNearestLeader = {}
        self.leaderAndFollowers = collections.defaultdict(list)

        self.createNewPostringList()
        self.createChampionList()
        self.setLeaders()



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
        startTime = time.time()

        for k in self.indToDoc.keys():
            self.docToVec[k] = len(self.idToTerm)*[float(0)]

        for k, v in self.newPostingList.items():
            idf = v[0]
            for i in range(1, len(v)):
                t = v[i]
                doc, w = t[0], t[1]
                self.docToVec[doc][k] = idf*w

        endTime = time.time()
        print(f'Converting Collection of Documents to Vectors finished in {endTime-startTime} seconds')

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

        for id, similarity in docToSimilarity:
            print(self.indToDoc[id], similarity)
        return [self.indToDoc[t[0]] for t in docToSimilarity[:k]]

    def createChampionList(self):
        startTime = time.time()
        for k, v in self.newPostingList.items():
            docs = v[1:]
            docs.sort(key = lambda x: x[1], reverse = True)
            topR = docs[:self.r]
            self.championList[k].append(math.log10(len(self.indToDoc)/len(topR)))
            self.championList[k].extend(topR)
        
        for k, v in self.championList.items():
            docs = v[1:]
            justDocs = [d[0] for d in docs]
            self.champDocs = self.champDocs.union(set(justDocs))
        endTime = time.time()
        print(f"Finished building champion's list in {endTime - startTime} seconds")

    def get_query_vector_champ(self, query_terms):
        query_terms = [word.lower() for word in query_terms]
        termToFreq = {}
        for t in query_terms:
            termToFreq[t] = termToFreq.get(t, 0) + 1

        queryVector = len(self.idToTerm)*[float(0)]
        for term, freq in termToFreq.items():
            if term in self.termToId:
                w = 1 + math.log10(freq)
                idf = self.championList[self.termToId[term]][0]
                queryVector[self.termToId[term]] = w*idf
        return queryVector

    def inexact_query_champion(self, query_terms, x):
        startTime = time.time()
        
        for k in self.champDocs:
            self.docToVecChamp[k] = len(self.idToTerm)*[float(0)]

        for k, v in self.championList.items():
            idf = v[0]
            for i in range(1, len(v)):
                t = v[i]
                doc, w = t[0], t[1]
                self.docToVecChamp[doc][k] = idf*w

        queryVector = self.get_query_vector_champ(query_terms)
        docToSimilarity = []
        for doc, vec in self.docToVecChamp.items(): # for champions list only look at 
            docToSimilarity.append((doc, self.cosine_similarity(queryVector, vec)))
        # for d, s in docToSimilarity:
        #     print(f"doc: {self.indToDoc[d]}, similarity: {s}")
        docToSimilarity.sort(key = lambda x:x[1], reverse=True)

        endTime = time.time()
        print(f"Query executed in {endTime - startTime} seconds.")
        return [self.indToDoc[t[0]] for t in docToSimilarity[:x]]

    def get_query_vector_elimination(self, query_terms):
        query_terms = [word.lower() for word in query_terms]

        termToIDF = []
        for term in query_terms:
            if term in self.termToId:
                termToIDF.append((term, self.newPostingList[self.termToId[term]][0]))

        termToIDF.sort(key=lambda x:x[1], reverse=True)
        query_terms = [tuple[0] for tuple in termToIDF[:len(termToIDF)//2]] 

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

    def inexact_query_index_elimination(self, query_terms, k):
        startTime = time.time()
        query_terms = [word.lower() for word in query_terms]

        queryVector = self.get_query_vector_elimination(query_terms)

        docToSimilarity = []
        for doc, vec in self.docToVec.items(): 
            docToSimilarity.append((doc, self.cosine_similarity(queryVector, vec)))
        docToSimilarity.sort(key = lambda x:x[1], reverse=True)
        for d, s in docToSimilarity:
            print(f"doc: {self.indToDoc[d]}, similarity: {s}")
        endTime = time.time()
        print(f"Index Elimination Query executed in {endTime - startTime} seconds.")
        return [self.indToDoc[t[0]] for t in docToSimilarity[:k]]

    def setLeaders(self):
        startTime = time.time()
        self.leadersArr = random.sample(range(0, len(self.indToDoc)), int(math.sqrt(len(self.indToDoc))))
        self.leadersSet = set(self.leadersArr)

        for doc in range(len(self.indToDoc)):
            if doc not in self.leadersSet:
                docVec = self.docToVec[doc]
                distNearest = float("-inf")
                nearest = None
                for l in self.leadersArr:
                    newDist = self.cosine_similarity(docVec, self.docToVec[l])
                    if newDist >= distNearest:
                        distNearest = newDist
                        nearest = l
                self.docToNearestLeader[doc] = nearest
            else:
                self.docToNearestLeader[doc] = doc

        for k, v in self.docToNearestLeader.items():
            self.leaderAndFollowers[v].append(k)
        endTime = time.time()
        print(f"Finished setting leaders in {endTime - startTime} seconds")

    def inexact_query_cluster_pruning(self, query_terms, k):
        startTime = time.time()
        queryVector = self.get_query_vector(query_terms)

        leadersAndDist = []
        for l in self.leadersArr:
            v = self.docToVec[l]
            distToQuery = self.cosine_similarity(v, queryVector)
            leadersAndDist.append((l, distToQuery))
        leadersAndDist.sort(key=lambda x:x[1])

        res = []
        for l, dist in leadersAndDist:
            cluster = self.leaderAndFollowers[l]
            # Sort each element in cluster by distance to query vector
            clusterDistToQuery = []
            for n in cluster:
                dist = self.cosine_similarity(self.docToVec[n], queryVector)
                clusterDistToQuery.append((n, dist))
            clusterDistToQuery.sort(key=lambda x:x[1])
            res.extend([x[0] for x in clusterDistToQuery])
            if len(res) >= k:
                break
        result = res[:k]

        endTime = time.time()
        print(f"Query executed in {endTime - startTime} seconds.")

        return [self.indToDoc[r] for r in result]

    def print_dict(self):
        #function to print the terms and posting list in the index
        for k, v in self.newPostingList.items:
            print(f"{k} : {v}")


    def print_doc_list(self):
	    # function to print the documents and their document id
        for k, v in self.indToDoc.items:
            print(f"ID:{k}, Doc:{v}")
    



a = index("collection")
query_terms1 = ["American", "Party", "Election", "Republican", "Democrat", "interference", "War", "Crime", "Russian", "Spy", "Rigging"]
query_terms2 = ["Young", "Girl", "Family", "Captured", "Miracle", "War", "economy", "human", "nature", "violence", "soldier"]
query_terms3 = ["German", "Manufactured", "Automobile", "Car", "tires", "armored", "safe", "expensive", "money", "tax", "mileage"]
query_terms4 = ["Bad", "Police", "Officer", "Captured", "wrong", "person", "imprisoned", "mistake", "jailed", "unpunished", "criminal"]
query_terms5 = ["Soviet", "Communist", "Russian", "Party", "War", "chaotic", "regime", "battlefield", "negotiation", "native", "guerillas"]


print(a.inexact_query_index_elimination(query_terms3, 10))

#print(a.exact_query(query_terms, 2))

# print(a.inexact_query_champion(query_terms, 2))
# print(a.inexact_query_index_elimination(query_terms, 2))
# print(a.inexact_query_cluster_pruning(query_terms, 2))