import sys
import lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene import document
from org.apache.lucene.document import Document, Field
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search import similarities

from org.apache.lucene.search.similarities import TFIDFSimilarity
from org.apache.lucene.search.similarities import BM25Similarity
from org.apache.lucene.search.similarities import BooleanSimilarity
from org.apache.lucene.search.similarities import ClassicSimilarity

from org.apache.lucene.index import IndexReader, DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.util import Version

if __name__ == "__main__":
    lucene.initVM()
    analyzer = StandardAnalyzer()
    indexPath = File("index/").toPath() #from java. io import File
    indexDir = FSDirectory.open(indexPath)
    reader = DirectoryReader.open(indexDir)

    # similarities.BooleanSimilarity()
    # similarities.BM25Similarity()
    # similarities.TFIDFSimilarity()
    
    searcher = IndexSearcher(reader)
    searcher.similarity = ClassicSimilarity()
    # searcher.setSimilarity(BM25Similarity())
    # searcher.setSimilarity(TFIDFSimilarity())


    
    indexReader = searcher.getIndexReader()

    # print(searcher.getSimilarity())


    

    # print(f"Number of docs {indexReader.numDocs()}")
    
    query = QueryParser("text", analyzer).parse("A cat jumped")
    MAX = 1000
    hits = searcher.search(query, MAX)

    print(searcher.explain(query, 1))

    # print ("Found %d document(s) that matched query '%s':" % (hits.totalHits.value, query))
    for hit in hits.scoreDocs:
        # print(hit)
        #print(hit.score, hit.doc, hit.toString())
        doc = searcher.doc(hit.doc)
        #print(doc.get("text").encode("utf-8"))