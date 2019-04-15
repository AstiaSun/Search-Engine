# Search engine


This project is a realisation of tasks for a university course 
'Information search methods'. The course covers different algorithms and 
methods of search in large amount of data.

## 1. Language dictionary

**_Task_**: 

Write a program that builds a dictionary of terms according to a 
given collection of text files.

- Text files are submitted to the input in any format.
- The size of text files is not less than 150 K.
- The number of text files is at least 10.
- Glossary of terms saved to disk.
- Evaluate the size of the collection, the total number of words in the collection, and the size of the dictionary.
- Substantiate the structure of data
- Make an estimation of the complexity of the algorithm
- Try several formats for saving the dictionary (serialization of the dictionary, saving to a text file, etc.) and compare the results.

**_Solution_**:

I have used a paradigm of parallel programming 'producers and consumers', 
as well as 'map and reduce' method in order to speed the performance of the task.

1) 1 producer reads the documents and put the data into the queue.

2) N token-consumers reads the data and split it into the tokens. 
Tokenizing is done with the help of nltp library. Meanwhile token-consumers are 
also mappers, who put processed tokens with their positions in text
into the queue to later reducing work.
Tokenizing algorithm:
    1) Split data into words
    2) Remove accented chars
    3) Expand contractions
    4) Remove stopwords
    5) Remove special characters
    5) Do stemming
3) M reducers reduce token position by tokens and form dictionaries for every document.
5) Writer process save dictionaries to memory as a file with as name which corresponds 
the id of a file. File ids are saved in a separate document.

*Supported languages*: English

*Supported extensions*: txt, docx

*Test results*: processed required volume of documents in ~8-12 seconds (Intel core i7, 8 cores)


## 2. Bool search

**_Task_**:

According to the given collection (10 documents for 150K) of documents to build:

- incidence matrix "document term"
- inverted index

Justify the selected data storage structures in terms of their effectiveness when increasing data volumes.

Compare the size of the structures that came out.

Make a Boolean search for these structures (both).

Operators: AND, OR, NOT. Format on request at your own discretion

**_Solution_**:

See boolean_search folder for detailed information


## 3. Two-word index and coordinate inverted index


**_Task_**:

Construct a two-word index and coordinate inverted index in a collection of documents.

Realize phrase search and search based on distance for each one.



## 4. Suffix tree. Permutation index. 3-gram index


**_Task_**:

Construct a suffix tree of vocabulary terms, a permutation index for the 
dictionary and a 3-gram index for the dictionary. Implement a support for 
queries with jokers.


## 5. Index construction


**_Task_**:

Choose one of the methods for building an index:

- BSBI
- SPIMI
- MapReduce
- Dynamic construction

Using the chosen method build a large collection index.


## 6. Compressed dictionary and compressed inverted index

**_Task_**:


Choose one of these methods and compress the dictionary and inverted collection index:

- Dictionary: Dictionary as a strip
- Dictionary: Block compression
- Inverted file: Gamma codes

**_Solution_**:

I have chosen method of block compression for a dictionary and grey codes for inverted index.

## 7. Ranking

**_Task_**: Implement a search by query request in collection of documents using zoned ranking.
