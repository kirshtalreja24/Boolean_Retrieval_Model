import re
import unidecode
import string
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import contractions
import DocumentExtraction


class InvertedIndex:
    def __init__(self):
        self.words = {}
        self.stopwords = set()
        self.stemmer = PorterStemmer()
        self.punctuation_table = str.maketrans('', '', string.punctuation)

    def readStopWords(self, filepath='Stopword-List.txt'):
        with open(filepath) as file:
            self.stopwords = set(line.strip() for line in file)

    def removeWhiteSpaces(self, text):
        return re.sub(' +', ' ', text)

    def lowerText(self, text):
        return text.lower()

    def normalizeText(self, text):
        return unidecode.unidecode(text)

    def removeContractions(self, words):
        fixed = []
        for word in words:
            expanded = contractions.fix(word)
            fixed.extend(expanded.split())
        return fixed

    #process the words by removing contractions, fixing hyphenated words, removing punctuation, stemming and removing stopwords
    def processWords(self, words):
        words = self.removeContractions(words)

        # fix hyphenated words
        fixed_words = []
        for w in words:
            w = w.replace('-', ' ')
            fixed_words.extend(w.split())

        words = [w.translate(self.punctuation_table) for w in fixed_words]
        words = [w for w in words if w]

        #stemming
        words = [self.stemmer.stem(w) for w in words]

        words = [w for w in words if len(w) > 2 and w not in self.stopwords]

        return words

    def tokenizeSentences(self, text, fileNum):
        sentences = text.split('.')
        position = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            words = word_tokenize(sentence)
            words = self.processWords(words)

            for word in words:
                if word not in self.words:
                    self.words[word] = {}

                if fileNum not in self.words[word]:
                    self.words[word][fileNum] = []

                self.words[word][fileNum].append(position)
                position += 1

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

        self.words = dict(sorted(self.words.items()))

    def writeToFile(self, filename="inverted_index.txt"):
        with open(filename, "w") as f:
            for word, postings in sorted(self.words.items()):
                f.write(f"{word} -> {postings}\n")

    def getspecificPostingList(self, word):
        if word in self.words:
            return sorted(list(self.words[word].keys()))
        return []

    # to process the query and return the processed terms
    def processQuery(self, query):
        query = query.lower()
        query = unidecode.unidecode(query)

        query = query.replace('-', ' ')
        parts = query.split()

        processed = []
        for w in parts:
            w = w.translate(self.punctuation_table)
            w = self.stemmer.stem(w)

            if len(w) > 2 and w not in self.stopwords:
                processed.append(w)

        return processed 
    


    