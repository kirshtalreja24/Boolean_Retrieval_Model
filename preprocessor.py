import DocumentExtraction
import re
import unidecode
from nltk.tokenize import word_tokenize   #splits sentences into words
from nltk.tokenize import sent_tokenize   #splits text into sentences
from nltk.stem import WordNetLemmatizer   # a lemmatizer


class InvertedIndex:    
    def __init__(self):
        self.words = {}
        self.stopwords = []
        self.lemmatizer = WordNetLemmatizer()
        self.punctuation_table = str.maketrans('', '', r'!"#$%&()*+,-./:;<=>?@[\]^_`{|}~') #remove punctuation from text
        
    
    def readStopWords(self):
        with open('Stopword-List.txt') as file:
            lines = file.readlines()
            for line in lines:
                self.stopwords.append(line.strip())




# ob1 = InvertedIndex()
# ob1.readStopWords()
# print(ob1.stopwords)
        
        
