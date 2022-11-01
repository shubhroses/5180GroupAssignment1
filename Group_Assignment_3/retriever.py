import sys
import lucene

from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene import document
from org.apache.lucene.document import Document, Field
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.search.similarities import TFIDFSimilarity
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

   
    
    searcher = IndexSearcher(reader)
    indexReader = searcher.getIndexReader()

    print(indexReader.numDocs())
    
    query = QueryParser("text", analyzer).parse("Dog in house")
    MAX = 1000
    hits = searcher.search(query, MAX)

    print ("Found %d document(s) that matched query '%s':" % (hits.totalHits.value, query))
    for hit in hits.scoreDocs:
        print(hit)
        #print(hit.score, hit.doc, hit.toString())
        doc = searcher.doc(hit.doc)
        #print(doc.get("text").encode("utf-8"))