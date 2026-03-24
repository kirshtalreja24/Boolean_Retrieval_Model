import DocumentExtraction
from processor import InvertedIndex
from processor import InvertedIndex

d1 = DocumentExtraction.Extractedfiles()

d1.readData()
files = d1.getfiles()



index = InvertedIndex()
index.readStopWords()

doc1 = "I can't eat apples. Apples are tasty and healthy!"
doc2 = "He is eating an apple, and he likes that apple."

index.tokenizeSentences(doc1, 1)
index.tokenizeSentences(doc2, 2)

index.displayInvertedIndex()