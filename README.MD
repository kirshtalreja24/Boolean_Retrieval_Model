# Implementation of Boolean Retrieval Model

-> Two basic elements which we need are the 
    # Dictionary & Posting List

-> Dictionary contains all the terms extracted from the corpus which are sorted in lexicographical order
-> Posting list consists of all the document IDs (document numbers) for each term respectively


# Step1
Created a DocumentExtraction.py which will extract the files from the "Trump Speeches Dataset" 

# Step2
created a main.py for testing 

# Step3
created preprocessor.py which will create dictionary.txt and posting_list.txt from the extracted documents by doing tokenization, normalization etc 