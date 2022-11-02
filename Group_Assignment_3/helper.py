import collections

def get_docs():
    path = "Group_Assignment_3/time/test.all"

    docNameToId = {}
    docIdToName = {}
    docIdToText = collections.defaultdict(list)

    with open(path) as file:
        line = file.readline()
        i = 0

        curDocId = 0

        while line:
            # Regex to match only strings and spaces \n",
            # line = re.sub(r'[^A-Za-z\\s]+', '', line)\n",
            words = line.split()
            if words and words[0] == "*TEXT":
                i = 0 # Have to reset count for each file
                curDocId += 1
                docNameToId[words[1]] = curDocId
                docIdToName[curDocId] = words[1]
            else:
                for word in words:   
                    # print(f\"pos: {i}, term: {word}\")\n",
                    # docIdToText[curDocId].append([word, i]) # If want to append position
                    docIdToText[curDocId].append(word)
                    i += 1
            line = file.readline()
    return docIdToText

if __name__ == "__main__":
    docIdToText = get_docs()
    for k, v in docIdToText.items():
        print(f"{k}: {v}")