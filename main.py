import processor

index = processor.InvertedIndex()
index.documentProcessing()
# index.writeToFile()


# ✅ process query properly
query_terms = index.processQuery("running")

ar1 = []
for term in query_terms:
    ar1.extend(index.getspecificPostingList(term))

ar1 = sorted(set(ar1))

print("Your Output:", ar1)
print()

arr = ['0', '1', '10', '11', '12', '16', '17', '18', '19', '2', '20', '21',
       '22', '24', '25', '26', '27', '28', '3', '30', '32', '33', '34',
       '35', '36', '37', '39', '4', '40', '41', '44', '45', '46', '47',
       '5', '50', '51', '52', '53', '6', '8', '9']

arr = sorted([int(x) for x in arr])

print("Expected:", arr)
print()

if ar1 == arr:
    print("✅ True")
else:
    print("❌ False")