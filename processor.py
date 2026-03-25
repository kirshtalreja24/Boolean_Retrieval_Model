import re
import unidecode
import string
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import contractions
import DocumentExtraction  # your module containing Extractedfiles


class InvertedIndex:
    def __init__(self):
        self.words = {}  # main inverted index
        self.stopwords = set()
        self.lemmatizer = WordNetLemmatizer()
        self.punctuation_table = str.maketrans('', '', string.punctuation)

    # Load stopwords once
    def readStopWords(self, filepath='Stopword-List.txt'):
        with open(filepath) as file:
            self.stopwords = set(line.strip() for line in file)

    # Remove extra whitespaces
    def removeWhiteSpaces(self, text):
        return re.sub(' +', ' ', text)

    # Lowercase text
    def lowerText(self, text):
        return text.lower()

    # Remove accents / diacritics
    def normalizeText(self, text):
        return unidecode.unidecode(text)

    # Expand contractions like "can't" -> "cannot"
    def removeContractions(self, words):
        return [contractions.fix(word) for word in words]

    # Lemmatize words
    def lemmatizeWords(self, words):
        return [self.lemmatizer.lemmatize(word) for word in words]

    # Tokenize sentences, remove punctuation, lemmatize, and build the inverted index
    def tokenizeSentences(self, text, fileNum):
        sentences = text.split('.')  
        position = 0  
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            words = word_tokenize(sentence)
            words = self.removeContractions(words)
            words = [w.translate(self.punctuation_table) for w in words]  # remove punctuation
            words = [self.lemmatizer.lemmatize(w.lower()) for w in words]  # lowercase + lemmatize
            words = [w for w in words if len(w) > 2 and w not in self.stopwords]  # remove short words & stopwords

            for word in words:
                
                if word not in self.words:
                    self.words[word] = {}
                    
                if fileNum not in self.words[word]:
                    self.words[word][fileNum] = []
                    
                self.words[word][fileNum].append(position)
                position += 1  

    # helper function to display the inverted index
    def displayInvertedIndex(self):
        for word, postings in sorted(self.words.items()):
            print(f"{word} -> {postings}")

    #controller function to process documents and build the inverted index
    def documentProcessing(self):
        fobj = DocumentExtraction.Extractedfiles()
        fobj.readData()
        files = fobj.getfiles()

        self.readStopWords()  
        for cnt, doc in enumerate(files, start=0):
            text = self.removeWhiteSpaces(doc)
            text = self.lowerText(text)
            text = self.normalizeText(text)
            self.tokenizeSentences(text, cnt)

        self.words = dict(sorted(self.words.items(), key=lambda term: term[0]))

    def writeToFile(self, filename="inverted_index.txt"):
        with open(filename, "w") as f:
            for word, postings in sorted(self.words.items()):
                f.write(f"{word} -> {postings}\n")

    def printPostingList(self):
        for word, postings in sorted(self.words.items()):
            print(word, postings)

    #helper function
    def printSpecificPostingList(self, word):
        if word in self.words:
            print(f"{word} -> {self.words[word]}")
        else:
            print(f"{word} not found in index.")