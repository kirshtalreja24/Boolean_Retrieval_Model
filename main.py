import DocumentExtraction


d1 = DocumentExtraction.Extractedfiles()

d1.readData()
files = d1.getfiles()

print(len(files))
print(files[2])