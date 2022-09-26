README file --- Briefly describing your merge algorithm and any other comments

Merge algorithm

Requirements:
· Implement an efficient algorithm to merge (AND operation) posting lists of multiple query terms.
· The algorithm should take a list of query terms (can be more than 2 terms) as input.
· In class, we looked at an algorithm for merging posting lists of two query terms by moving a pointer over all the relevant posting lists simultaneously. 
Generalize this for n terms. Note that an efficient algorithm looks at each item in the posting lists of the query term only once.

Implementation:
1. Write the merge algorithm discussed in class to merge the posting lists of two words. 
    i. Works by having pointer i and j, one for each posting list. 
    ii. Incrementing pointer of posting list with lower number current document. 
        If PostingListI[i] < PostringListJ[j]: Increment i
        Otherwise increment j
    iii. If the current document in both posting lists is the same, add document to combined posting list
        PostingListI[i] == PostringListJ[j]: Combined.add(PostingListI[i])
    Run time: O(len(PostingListI) + len(PostringListJ))
2. Merge N posting lists
    i. Combine posting lists two at a time using algorithm above until only one posting list left
    Run time: O((len(PostingListI) + len(PostringListJ)) * log(number of query terms))
