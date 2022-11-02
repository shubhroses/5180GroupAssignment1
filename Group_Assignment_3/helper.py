import collections

def get_docs(path):
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

def get_queue(path):
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

def get_stopwords(path):
    stopWords = []
    with open(path) as file:
        line = file.readline()
        while line:
            for word in line.split():
                if len(word) == 1:
                    continue
                stopWords.append(word)
            line = file.readline()
    return stopWords

def get_relevance(path):
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

if __name__ == "__main__":
    print("\n TESTING GET_DOCS")
    docIdToText = get_docs("Group_Assignment_3/time/test.all")
    for k, v in docIdToText.items():
        print(f"{k}: {v}")

    print("\n TESTING GET_QUEUE")
    idToQueue = get_queue("Group_Assignment_3/time/test.que")
    for k, v in idToQueue.items():
        print(f"{k}: {v}")

    print("\n TESTING GET_STOPWORDS")
    stopWords = get_stopwords("Group_Assignment_3/time/test.stp")
    print(stopWords)

    print("\n TESTING GET_RELEVANCE")
    queryToRelatedDocs = get_relevance("Group_Assignment_3/time/test.rel")
    for k, v in queryToRelatedDocs.items():
        print(f"{k} : {v}")



    