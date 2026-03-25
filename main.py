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

# arr = ['31', '28', '37', '30', '7', '10', '14', '1', '6', '41', '15', '11',
#        '29', '26', '52', '13', '32', '44', '4', '8', '22', '38', '48', '0', 
#        '47', '2', '23', '9', '3', '5', '12', '55']

# arr = sorted([int(x) for x in arr])

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
    print("Result:", result)
    print()