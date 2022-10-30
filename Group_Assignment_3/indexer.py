import sys
import lucene
 
from java.io import File
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene import document
from org.apache.lucene.document import Document, Field
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.util import Version
 
if __name__ == "__main__":
    lucene.initVM()
    indexPath = File("index/").toPath() #from java. io import File
    indexDir = FSDirectory.open(indexPath)
    writerConfig = IndexWriterConfig(StandardAnalyzer())
    writer = IndexWriter(indexDir, writerConfig)

    print ("%d docs in index" % writer.numRamDocs())
    print ("Reading lines from sys.stdin...")
    for n, l in enumerate(sys.stdin):
        doc = Document()
        doc.add(Field("text", l, document.TextField.TYPE_STORED))
        writer.addDocument(doc)
        print(doc)
    print ("Indexed %d lines from stdin (%d docs in index)" % (n, writer.numRamDocs()))
    print ("Closing index of %d docs..." % writer.numRamDocs())
    writer.close()

