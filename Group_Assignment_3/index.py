#Python 3.0
import re
import os
import collections
import time
import math
import random
import numpy as np
#import other modules as needed

class index:
	def __init__(self, path):
		self.path = path
		self.idToTerm = {}
		self.termToId = {}
		self.curTermIndex = 0
		self.indToDoc = {}
		self.docToVec = {}
		self.newPostingList = collections.defaultdict(list)

		self.createNewPostringList()
		self.convertDocumentsToVector()
		pass

	def buildIndex(self):
		#function to read documents from collection, tokenize and build the index with tokens
		# implement additional functionality to support relevance feedback
		#use unique document integer IDs
		pass

	def rocchio(self, query_terms, pos_feedback, neg_feedback, alpha, beta, gamma, q):
		relevant_doc_vecs = [np.array(self.docToVec[i]) for i in pos_feedback]
		non_relevant_doc_vecs = [np.array(self.docToVec[i]) for i in neg_feedback]

		if len(relevant_doc_vecs) == 0 and len(non_relevant_doc_vecs) == 0:
			new_query = alpha*q
		elif len(relevant_doc_vecs) == 0:
			new_query = alpha*q - gamma*(1/len(non_relevant_doc_vecs))*(sum(non_relevant_doc_vecs))
		elif len(non_relevant_doc_vecs) == 0:
			new_query = alpha*q + beta*(1/len(relevant_doc_vecs))*(sum(relevant_doc_vecs)) 
		else:
			new_query = alpha*q + beta*(1/len(relevant_doc_vecs))*(sum(relevant_doc_vecs)) - gamma*(1/len(non_relevant_doc_vecs))*(sum(non_relevant_doc_vecs))
		return new_query
	
	def query(self, query_terms, k):
	#function for exact top K retrieval using cosine similarity
	#Returns at the minimum the document names of the top K documents ordered in decreasing order of similarity score
		pass
	
	def print_dict(self):
    #function to print the terms and posting list in the index
		for k, v in self.newPostingList.items():
			print(k, v)

	def print_doc_list(self):
	# function to print the documents and their document id
		for id, doc in self.indToDoc.items():
			print(id)

	def get_docs(self, path):
		docIdToText = collections.defaultdict(list)
		with open(path) as file:
			line = file.readline()
			i = 0

			while line:
				words = line.split()
				if words and words[0] == "*TEXT":
					curDocId = int(words[1]) # Can change it back to string if necessary
					self.indToDoc[curDocId] = curDocId
					i = 0
				else:
					for word in words:   
						docIdToText[curDocId].append((word.lower(), i))
						i += 1
				line = file.readline()
		return docIdToText
	
	def get_stopwords(self, path):
		stopWords = set()
		with open(path) as file:
			line = file.readline()
			while line:
				for word in line.split():
					if len(word) == 1:
						continue
					stopWords.add(word.lower())
				line = file.readline()
		return stopWords
	
	def buildOldIndex(self):
		docIdToText = self.get_docs(self.path + "time/TIME.ALL")
		stopWords = self.get_stopwords(self.path + "time/TIME.STP")
		oldPostingList = collections.defaultdict(list)

		for doc, termPos in docIdToText.items():
			wordToPos = collections.defaultdict(list)
			for word, pos in termPos:
				if word in stopWords:
					continue
				wordToPos[word].append(pos)
			for term, arr in wordToPos.items():
				oldPostingList[term].append((doc, arr))
		
		return oldPostingList

	def createNewPostringList(self):
		startTime = time.time()
		oldPostingList = self.buildOldIndex()
		
		for k,v in oldPostingList.items():
			# if k in stopList:
			#     continue
			self.idToTerm[self.curTermIndex] = k
			self.termToId[k] = self.curTermIndex
			self.newPostingList[self.curTermIndex].append(math.log10(len(self.indToDoc)/len(v)))
			
			for docId, posList in v:
				self.newPostingList[self.curTermIndex].append((docId, 1 + math.log10(len(posList)), posList))
			self.curTermIndex += 1
		for id, term in self.idToTerm.items():
			self.termToId[term] = id
		endTime = time.time()
		print(f"Index built in {endTime - startTime} seconds.")
	
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

		# for id, similarity in docToSimilarity:
		#     print(self.indToDoc[id], similarity)
		return [self.indToDoc[t[0]] for t in docToSimilarity[:k]]

	def exact_query_using_vector(self, queryVector, k):
		startTime = time.time()
		queryVector.tolist()
		docToSimilarity = []
		for doc, vec in self.docToVec.items(): # for champions list only look at 
			docToSimilarity.append((doc, self.cosine_similarity(queryVector, vec)))
		# for d, s in docToSimilarity:
		#     print(f"doc: {self.indToDoc[d]}, similarity: {s}")
		docToSimilarity.sort(key = lambda x:x[1], reverse=True)
		endTime = time.time()
		print(f"Query executed in {endTime - startTime} seconds.")

		# for id, similarity in docToSimilarity:
		#     print(self.indToDoc[id], similarity)
		return [self.indToDoc[t[0]] for t in docToSimilarity[:k]]
	

if __name__ == "__main__":
	a = index("Group_Assignment_3/")

	query_terms1 = ["a", "cat", "jumped"]

	print(a.exact_query(query_terms1, 3))