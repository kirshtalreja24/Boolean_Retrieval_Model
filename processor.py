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

    # Loads stopwords from a file into a set for fast lookup.
    def readStopWords(self, filepath='Stopword-List.txt'):
        with open(filepath) as file:
            self.stopwords = set(line.strip() for line in file)

    # Collapses multiple consecutive spaces into a single space.
    def removeWhiteSpaces(self, text):
        return re.sub(' +', ' ', text)

    # Converts all characters in the text to lowercase.
    def lowerText(self, text):
        return text.lower()

    # Converts accented or special Unicode characters to their ASCII equivalents.
    def normalizeText(self, text):
        return unidecode.unidecode(text)

    # Expands contractions in a list of words (e.g. "don't" -> "do not").
    def removeContractions(self, words):
        fixed = []
        for word in words:
            expanded = contractions.fix(word)
            fixed.extend(expanded.split())
        return fixed

    # Cleans and normalizes a list of words by expanding contractions,
    # splitting hyphenated words, removing punctuation, stemming,
    # and filtering out stopwords and very short tokens.
    def processWords(self, words):
        words = self.removeContractions(words)

        fixed_words = []
        for w in words:
            w = w.replace('-', ' ')
            fixed_words.extend(w.split())

        words = [w.translate(self.punctuation_table) for w in fixed_words]
        words = [w for w in words if w]
        words = [self.stemmer.stem(w) for w in words]
        words = [w for w in words if len(w) > 2 and w not in self.stopwords]

        return words

    # Splits text into sentences, tokenizes each sentence, processes the words,
    # and records each word's position in the index under the given document ID.
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

    # Reads all documents, preprocesses each one, and builds the inverted index.
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

    # Writes the inverted index to a text file in the format: word -> {postings}
    def writeToFile(self, filename="inverted_index.txt"):
        with open(filename, "w") as f:
            for word, postings in sorted(self.words.items()):
                f.write(f"{word} -> {postings}\n")

    # Returns the sorted list of document IDs that contain the given word.
    def getspecificPostingList(self, word):
        if word in self.words:
            return sorted(list(self.words[word].keys()))
        return []

    # Takes a raw query string, applies the same preprocessing as the index
    # (lowercasing, normalization, punctuation removal, stemming, stopword filtering),
    # and returns a list of processed terms ready for lookup.
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