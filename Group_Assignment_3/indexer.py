import sys
import lucene
 
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene import document
from org.apache.lucene.document import Document, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.search.similarities import TFIDFSimilarity
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.util import Version
from helper import get_docs
 
if __name__ == "__main__":
    lucene.initVM()
    indexPath = File("index/").toPath() #from java. io import File
    indexDir = FSDirectory.open(indexPath)
    writerConfig = IndexWriterConfig(StandardAnalyzer())
    
    writer = IndexWriter(indexDir, writerConfig)

    print ("%d docs in index" % writer.numRamDocs())
    print ("Reading lines from sys.stdin...")

    docIdToText = get_docs("Group_Assignment_3/time/test.all")
    for k, v in docIdToText.items():
        doc = Document()
        ft = document.FieldType(document.TextField.TYPE_STORED)
        ft.setStoreTermVectors(True)
        doc.add(Field("text", " ".join(v), ft))
        writer.addDocument(doc) # TODO: Document id to index 
        print(doc)

    print ("Indexed %d docs in index)" % (writer.numRamDocs()))
    print ("Closing index of %d docs..." % writer.numRamDocs())

    # print ("%d docs in index" % writer.numRamDocs())
    # print ("Reading lines from sys.stdin...")
    # for n, l in enumerate(sys.stdin):
    #     doc = Document()
    #     doc.add(Field("text", l, document.TextField.TYPE_STORED))
    #     """
    #     ALong with text, add field of id.
    #     """
    #     writer.addDocument(doc)
    #     print(doc)
    # print ("Indexed %d docs in index)" % (writer.numRamDocs()))
    # print ("Closing index of %d docs..." % writer.numRamDocs())
    writer.close()

