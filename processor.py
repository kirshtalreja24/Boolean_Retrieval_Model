import DocumentExtraction
import re
import unidecode
import string
from nltk.tokenize import word_tokenize   #splits sentences into words
from nltk.tokenize import sent_tokenize   #splits text into sentences
from nltk.stem import WordNetLemmatizer   # a lemmatizer
import contractions    

class InvertedIndex:    
    def __init__(self):
        self.words = {}
        self.stopwords = set()
        self.lemmatizer = WordNetLemmatizer()
        self.punctuation_table = str.maketrans('', '', r'!"#$%&()*+,-./:;<=>?@[\]^_`{|}~') #remove punctuation from text
        
    
    def readStopWords(self):
        with open('Stopword-List.txt') as file:
            lines = file.readlines()
            for line in lines:
                self.stopwords.add(line.strip())

    def removeStopWords(self, words):
        self.readStopWords()
        flt = [word for word in words if word not in self.stopwords]
        return flt
    
    def removeWhiteSpaces(self, text):
        return re.sub(' +', ' ', text)
    
    def lowerText(self, text):
        return text.lower()
    
    #convert "can't" to "cannot"
    def removeContractions(self, words):
        contracted = []
        for word in words:
            contracted.append(contractions.fix(word))  #basically to replace contractions with their expanded forms
        return contracted
    
    def wordTokenize(self, sentence, fileNum):
        words = word_tokenize(sentence)
        words = self.removeContractions(words)
        words = self.removeStopWords(words)
        words = self.lemmatizeWords(words)  
        self.appendToInvertedIndex(words, fileNum)
    
    def lemmatizeWords(self, words):
        lemmatized = []
        for word in words:
            lemmatized.append(self.lemmatizer.lemmatize(word))
        return lemmatized
    
    # converts one whole document into sentence pieces after which further processing is done
    def tokenizeSentences(self, text, fileNum):
        sentences = sent_tokenize(text)
        for sentence in sentences:
            sentence = self.removePunctuation(sentence)
            sentence = sentence.strip()
            self.wordTokenize(sentence, fileNum)
    
    def appendToInvertedIndex(self, words, fileNum):
        for index, word in enumerate(words):
            
            #normalize words (lowercase and only letters)
            word = ''.join(c for c in word.lower() if c.isalpha())
            
            if len(word) <= 2 or word in self.stopwords:
                continue
            
            if word not in self.words:
                self.words[word] = {}
            if fileNum not in self.words[word]:
                self.words[word][fileNum] = []
            
            self.words[word][fileNum].append(index)
        
        #sort
        self.words = dict(sorted(self.words.items()))
    


'''
{
    "apple":{
        1:[0,4]
        2:[3,5]
    }
}

this is the structure of the inverted index

'''

    
    
    
    
    



ob1 = InvertedIndex()
ob1.readStopWords()
print(ob1.stopwords)
        
    
    



ob1 = InvertedIndex()
ob1.readStopWords()
print(ob1.stopwords)
        
        
