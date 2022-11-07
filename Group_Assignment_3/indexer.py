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
from helper import get_docs
 
if __name__ == "__main__":
    lucene.initVM()
    
    indexPath = File("index/").toPath() #from java. io import File
    indexDir = FSDirectory.open(indexPath)
    writerConfig = IndexWriterConfig(StandardAnalyzer())
    writer = IndexWriter(indexDir, writerConfig)

    docIdToText = get_docs("Group_Assignment_3/time/test.all")

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

