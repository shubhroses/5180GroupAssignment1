import sys
import lucene
 
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene import document
from org.apache.lucene.document import Document, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.search.similarities import TFIDFSimilarity
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.util import Version


from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search import similarities

from org.apache.lucene.search.similarities import TFIDFSimilarity
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.search.similarities import BooleanSimilarity
from org.apache.lucene.search.similarities import ClassicSimilarity
from org.apache.lucene.search.similarities import Similarity


from org.apache.lucene.index import IndexReader, DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.util import Version

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
		self.reader = None

		self.createNewPostringList()
		self.convertDocumentsToVector()
		self.buildIndex()
		pass

	def get_docs_for_lucene(self, path):
		docIdToText = collections.defaultdict(list)

		with open(path) as file:
			line = file.readline()
			i = 0

			while line:
				words = line.split()
				if words and words[0] == "*TEXT":
					curDocId = int(words[1]) # Can change it back to string if necessary
				else:
					for word in words:   
						docIdToText[curDocId].append(word)
				line = file.readline()
		return docIdToText


	def buildIndex(self):
		lucene.initVM()
		indexPath = File("index/").toPath() #from java. io import File
		indexDir = FSDirectory.open(indexPath)
		writerConfig = IndexWriterConfig(StandardAnalyzer())
		writer = IndexWriter(indexDir, writerConfig)

		docIdToText = self.get_docs_for_lucene(self.path + "time/TIME.ALL")

		for k, v in docIdToText.items():
			doc = Document()
			
			fieldType = document.FieldType()
			fieldType.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS_AND_OFFSETS)
			fieldType.setStored(True)
			fieldType.setTokenized(True)
			fieldType.setOmitNorms(False)

			doc.add(Field("myID", k, fieldType))
			doc.add(Field("content", " ".join(v), fieldType))

			writer.addDocument(doc)

		print ("Indexed %d docs in index" % (writer.numRamDocs()))
		print ("Closing index of %d docs..." % writer.numRamDocs())

		writer.close()


		analyzer = StandardAnalyzer()
		indexPath = File("index").toPath() #from java. io import File
		indexDir = FSDirectory.open(indexPath)
		self.reader = DirectoryReader.open(indexDir)

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

	def get_queue(self, path):
		idToQueue = collections.defaultdict(list)

		with open(path) as file:
			line = file.readline()
			while line:
				words = line.split()
				if words and words[0] == "*STOP":
					break
				if words and words[0] == "*FIND":
					query_id = int(words[1])
				else:
					for word in words:   
						idToQueue[query_id].append(word)
				line = file.readline()
		
		return idToQueue

	def get_relevance(self, path):
		queryToRelatedDocs = collections.defaultdict(list)

		with open(path) as file:
			line = file.readline()
			while line:
				docs = line.split()
				if docs:
					cur_doc = int(docs[0])
					for doc in docs[1:]:
						queryToRelatedDocs[cur_doc].append(int(doc))
				line = file.readline()

		return queryToRelatedDocs

	def get_stats(self, qId, k):
		idToQueue = self.get_queue(self.path + "time/TIME.QUE")
		queryToRelatedDocs = self.get_relevance(self.path + "time/TIME.REL")
		
		all_documents = set(self.indToDoc.keys())
		p = []
		r = []
		mp = []

		qText = idToQueue[qId]
		qVec = np.array(self.get_query_vector(qText))

		print(f"Query ID: {qId}, Query text: {qText}")
		for i in range(6):
			queryResultArr = self.exact_query_using_vector(qVec, k)
			queryResults = set(queryResultArr)

			relatedDocs = set(queryToRelatedDocs[qId])

			pos_feedback = list(queryResults.intersection(relatedDocs))
			neg_feedback = list(queryResults.difference(relatedDocs))

			print(f"Iterations: {i}")
			print(f"Positive Feedback: {pos_feedback}")
			print(f"Negative Feedback: {neg_feedback}")
			relevant = relatedDocs
			non_relevant = all_documents.difference(relevant)

			retrieved = queryResults
			not_retrieved = all_documents.difference(retrieved)

			tp = relevant.intersection(retrieved)
			fp = non_relevant.intersection(retrieved)
			fn = relevant.intersection(not_retrieved)

			precision = len(tp)/(len(tp) + len(fp))
			recall = len(tp)/(len(tp) + len(fn))

			rCount = 0
			curMap = 0
			for ind, res in enumerate(queryResultArr, 1):
				if res in relevant:
					rCount += 1
					curMap += float(rCount)/float(ind)
			if rCount > 0:
				curMap = curMap/float(rCount)

			print(f"Precision: {precision}, Recall: {recall}, MAP: {curMap}")

			p.append([i, precision])
			r.append([i, recall])
			mp.append([i, curMap])

			qVec = self.rocchio(qText, pos_feedback, neg_feedback, alpha=1.0, beta=0.75, gamma=0.15, q=qVec)
			print(f"New Query Vector: {qVec}")

		return [p, r, mp]

	def get_stats_pseudo(self, qId, k):
		idToQueue = self.get_queue(self.path + "time/TIME.QUE")
		queryToRelatedDocs = self.get_relevance(self.path + "time/TIME.REL")
		
		all_documents = set(self.indToDoc.keys())
		p = []
		r = []
		mp = []

		qText = idToQueue[qId]
		qVec = np.array(self.get_query_vector(qText))

		# relatedDocs = None

		print(f"Query ID: {qId}, Query text: {qText}")
		for i in range(6):
			queryResultArr = self.exact_query_using_vector(qVec, k)
			queryResults = set(queryResultArr)

			# if not relatedDocs:
			# 	relatedDocs = set(queryResultArr[:3])
			relatedDocs = set(queryToRelatedDocs[qId])

			pos_feedback = list(queryResults.intersection(set(queryResultArr[:3])))
			neg_feedback = list(queryResults.difference(set(queryResultArr[:3])))

			print(f"Iterations: {i}")
			print(f"Positive Feedback: {pos_feedback}")
			print(f"Negative Feedback: {neg_feedback}")
			relevant = relatedDocs
			non_relevant = all_documents.difference(relevant)

			retrieved = queryResults
			not_retrieved = all_documents.difference(retrieved)

			tp = relevant.intersection(retrieved)
			fp = non_relevant.intersection(retrieved)
			fn = relevant.intersection(not_retrieved)

			precision = len(tp)/(len(tp) + len(fp))
			recall = len(tp)/(len(tp) + len(fn))

			rCount = 0
			curMap = 0
			for ind, res in enumerate(queryResultArr, 1):
				if res in relevant:
					rCount += 1
					curMap += float(rCount)/float(ind)
			if rCount > 0:
				curMap = curMap/float(rCount)

			print(f"Precision: {precision}, Recall: {recall}, MAP: {curMap}")

			p.append([i, precision])
			r.append([i, recall])
			mp.append([i, curMap])

			qVec = self.rocchio(qText, pos_feedback, neg_feedback, alpha=1.0, beta=0.75, gamma=0.15, q=qVec)
			print(f"New Query Vector: {qVec}")

		return [p, r, mp]
	

if __name__ == "__main__":
	a = index("Group_Assignment_3/")

	a.get_stats(qId = 6, k=9)

	# a.get_stats(qId = 9, k=50)

	# a.get_stats(qId = 12, k=50)

	# a.get_stats_pseudo(qId = 6, k=50)

	# a.get_stats_pseudo(qId = 9, k=50)

	# a.get_stats_pseudo(qId = 12, k=50)

