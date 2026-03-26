from Queries import Queries
import processor

index = processor.InvertedIndex()
index.documentProcessing()

qp = Queries(index)

while True:
    q = input("Enter Query: ")
    if q == "exit":
        break

    result = qp.queryInput(q)
    print("total documents found:", len(result))
    print("Result:", result)
    print()