import ast


class Queries:
    def __init__(self, processor_obj, filepath="inverted_index.txt"):
        self.index = self.load_index(filepath)
        self.processor = processor_obj
        self.resultSet = []
        self.all_docs = self.getAllDocs()

    # 🔹 Load inverted index from file
    def load_index(self, filepath):
        index = {}
        with open(filepath, "r") as f:
            for line in f:
                if "->" not in line:
                    continue
                word, postings = line.split("->")
                word = word.strip()
                postings = ast.literal_eval(postings.strip())
                index[word] = postings
        return index

    # 🔹 Get all document IDs
    def getAllDocs(self):
        docs = set()
        for postings in self.index.values():
            docs.update(postings.keys())
        return docs

    # 🔹 Get posting list
    def get_posting(self, term):
        if term in self.index:
            return sorted(list(self.index[term].keys()))
        return []

    # 🔹 Boolean operations
    def AND(self, p1, p2):
        return sorted(list(set(p1) & set(p2)))

    def OR(self, p1, p2):
        return sorted(list(set(p1) | set(p2)))

    def NOT(self, p):
        return sorted(list(self.all_docs - set(p)))

    # 🔹 Proximity Query (t1 t2 / k)
    def proximityQuery(self, term1, term2, k):
        result = []

        if term1 not in self.index or term2 not in self.index:
            return result

        postings1 = self.index[term1]
        postings2 = self.index[term2]

        common_docs = set(postings1.keys()) & set(postings2.keys())

        for doc in common_docs:
            pos1 = postings1[doc]
            pos2 = postings2[doc]

            i, j = 0, 0
            while i < len(pos1) and j < len(pos2):
                # ✅ correct positional condition
                if abs(pos1[i] - pos2[j]) <= k + 1:
                    result.append(doc)
                    break
                elif pos1[i] < pos2[j]:
                    i += 1
                else:
                    j += 1

        return sorted(result)

    # 🔥 MAIN QUERY PROCESSOR
    def queryProcessing(self, query):
        query = query.lower().strip()

        # 🔹 Positional Query: t1 t2 / k
        if '/' in query:
            parts = query.split('/')
            k = int(parts[1].strip())

            terms = parts[0].strip().split()

            if len(terms) < 2:
                return []

            t1_list = self.processor.processQuery(terms[0])
            t2_list = self.processor.processQuery(terms[1])

            if not t1_list or not t2_list:
                return []

            t1 = t1_list[0]
            t2 = t2_list[0]

            return self.proximityQuery(t1, t2, k)

        tokens = query.split()

        terms = []
        operators = []

        for token in tokens:
            if token.upper() in ["AND", "OR", "NOT"]:
                operators.append(token.upper())
            else:
                processed = self.processor.processQuery(token)
                if processed:
                    terms.append(processed[0])

        # 🔹 Single term
        if len(terms) == 1 and not operators:
            return self.get_posting(terms[0])

        # 🔹 NOT X
        if len(operators) == 1 and operators[0] == "NOT":
            p = self.get_posting(terms[0])
            return self.NOT(p)

        # 🔹 X AND Y / X OR Y
        if len(terms) == 2 and len(operators) == 1:
            p1 = self.get_posting(terms[0])
            p2 = self.get_posting(terms[1])

            if operators[0] == "AND":
                return self.AND(p1, p2)
            elif operators[0] == "OR":
                return self.OR(p1, p2)

        # 🔹 X AND Y AND Z (or OR mix)
        if len(terms) == 3 and len(operators) == 2:
            p1 = self.get_posting(terms[0])
            p2 = self.get_posting(terms[1])
            p3 = self.get_posting(terms[2])

            temp = self.AND(p1, p2) if operators[0] == "AND" else self.OR(p1, p2)
            return self.AND(temp, p3) if operators[1] == "AND" else self.OR(temp, p3)

        return []

    # 🔹 Input wrapper
    def queryInput(self, query):
        return self.queryProcessing(query)

    # 🔹 Print result
    def generateResultSet(self, result):
        print("Result-Set:", result)

    # 🔹 Debug: print index
    def printPositionalIndex(self):
        for word, postings in self.index.items():
            print(word, postings)