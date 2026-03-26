from Queries import Queries
import processor

index = processor.InvertedIndex()
index.documentProcessing()
# index.writeToFile()


# query_terms = index.processQuery("hammer")

# ar1 = []
# for term in query_terms:
#     t = index.getspecificPostingList(term)
#     print(t)
#     ar1.extend(t)

# ar1 = sorted(set(ar1))
# ar2 = []
# for i in range(0,56):
#     if i not in ar1:
#         ar2.append(i)


# print("Your Output:", ar1)
# print()

# arr = ['31', '28', '50', '53', '46', '37', '54', '42', '7', '10', '14', '18', '6', '49', '41', '15', '11', '45', '13', '21', '44', '16', '4', '8', '22', '40', '20', '38', '48', '47', '51', '43', '23', '39', '9', '3', '5', '12', '55']

# arr = sorted([int(x) for x in arr])
# print(len(arr))
# print("Expected:", arr)
# print()

# if ar2 == arr:
#     print("✅ True")
# else:
#     print("❌ False")
    


qp = Queries(index)

while True:
    q = input("Enter Query: ")
    if q == "exit":
        break

    result = qp.queryInput(q)
    print("total documents found:", len(result))
    print("Result:", result)
    print()
# print(qp.getAllDocs())