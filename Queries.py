import ast

class Queries:
    def __init__(self, processor_obj, filepath="inverted_index.txt"):
        self.index = self.load_index(filepath)  # positional inverted index
        self.processor = processor_obj
        self.all_docs = self.getAllDocs()  # normalized as strings

    # 🔹 Load inverted index
    def load_index(self, filepath):
        index = {}
        with open(filepath, "r") as f:
            for line in f:
                if "->" not in line:
                    continue
                word, postings = line.split("->")
                index[word.strip()] = ast.literal_eval(postings.strip())
        return index

    # 🔹 Get all docs
    def getAllDocs(self):
        docs = set()
        for postings in self.index.values():
            for doc_id in postings.keys():
                docs.add(doc_id)
        return docs

    # 🔹 Posting list (always returns list of strings)
    def get_posting(self, term):
        return sorted([str(doc) for doc in self.index.get(term, {}).keys()])

    # 🔹 Boolean operations (handle None / empty safely)
    def AND(self, a, b):
        a = a or []
        b = b or []
        return sorted(set(a) & set(b))

    def OR(self, a, b):
        a = a or []
        b = b or []
        return sorted(set(a) | set(b))

    def NOT(self, a):
        a = a or []
        if not a:
            return sorted(self.all_docs)
        return sorted(self.all_docs - set(a))

    # 🔹 Proximity Query (t1 before t2 within k)
    def proximityQuery(self, t1, t2, k):
        if t1 not in self.index or t2 not in self.index:
            return []

        result = []
        p1 = self.index[t1]
        p2 = self.index[t2]

        common_docs = set(p1.keys()) & set(p2.keys())

        for doc in common_docs:
            pos1 = p1[doc]
            pos2 = p2[doc]
            i, j = 0, 0
            while i < len(pos1) and j < len(pos2):
                diff = pos2[j] - pos1[i] - 1
                if 0 <= diff <= k:
                    result.append(doc)
                    break
                elif pos1[i] < pos2[j]:
                    i += 1
                else:
                    j += 1

        return sorted(result)

    # 🔹 Phrase Query
    def phraseQuery(self, phrase):
        words = phrase.split()
        words_proc = []
        for w in words:
            p = self.processor.processQuery(w)
            words_proc.append(p[0] if p else w)

        postings = []
        for w in words_proc:
            if w not in self.index:
                return []
            postings.append(self.index[w])

        result = []
        common_docs = set(postings[0].keys())
        for p in postings[1:]:
            common_docs &= set(p.keys())

        for doc in common_docs:
            positions = postings[0][doc]
            for i in range(1, len(postings)):
                next_pos = postings[i][doc]
                temp = []
                for pos in positions:
                    if pos + 1 in next_pos:
                        temp.append(pos + 1)
                positions = temp
                if not positions:
                    break
            if positions:
                result.append(doc)

        return sorted(result)

    # 🔹 Tokenize (handles phrases, proximity, parentheses)
    def tokenize(self, query):
        tokens = []
        i = 0
        words = query.split()
        while i < len(words):
            word = words[i]

            # Proximity query: t1 t2 /k
            if i + 2 < len(words) and words[i+2].startswith('/'):
                tokens.append((words[i], words[i+1], words[i+2]))
                i += 3
                continue

            # Phrase query
            if word.startswith('"'):
                phrase = word[1:]
                while not words[i].endswith('"'):
                    i += 1
                    phrase += ' ' + words[i].replace('"', '')
                phrase = phrase.rstrip('"')
                tokens.append(phrase)
                i += 1
                continue

            # Parentheses handling
            while word.startswith('('):
                tokens.append('(')
                word = word[1:]
            while word.endswith(')'):
                if word[:-1]:
                    word = word[:-1]
                tokens.append(')')
                word = word[:-1]

            # Boolean operators -> normalized to uppercase
            if word.lower() in ('and', 'or', 'not'):
                tokens.append(word.upper())
            elif word not in ('(', ')', ''):
                tokens.append(word)
            i += 1

        return tokens

    # 🔹 Infix → Postfix conversion
    def infix_to_postfix(self, tokens):
        precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
        output = []
        stack = []
        for token in tokens:
            token_upper = token.upper() if isinstance(token, str) else token
            if isinstance(token, tuple):
                output.append(token)
            elif token_upper not in precedence and token not in ('(', ')'):
                output.append(token)
            elif token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()
            else:
                while (stack and stack[-1] != '(' and
                       precedence.get(stack[-1].upper(), 0) >= precedence.get(token_upper, 0)):
                    output.append(stack.pop())
                stack.append(token_upper)
        while stack:
            output.append(stack.pop())
        return output

    # 🔹 Evaluate postfix
    def evaluate_postfix(self, tokens):
        stack = []
        for token in tokens:
            if isinstance(token, tuple):
                t1, t2, k = token
                k = int(k[1:])
                p1 = self.processor.processQuery(t1)
                p2 = self.processor.processQuery(t2)
                t1 = p1[0] if p1 else t1
                t2 = p2[0] if p2 else t2
                stack.append(self.proximityQuery(t1, t2, k) or [])
            elif token == 'AND':
                b = stack.pop() or []
                a = stack.pop() or []
                stack.append(self.AND(a, b))
            elif token == 'OR':
                b = stack.pop() or []
                a = stack.pop() or []
                stack.append(self.OR(a, b))
            elif token == 'NOT':
                a = stack.pop() or []
                stack.append(self.NOT(a))
            else:
                # Phrase or single term
                if ' ' in token:
                    res = self.phraseQuery(token)
                    stack.append(res if res is not None else [])
                else:
                    p = self.processor.processQuery(token)
                    term = p[0] if p else token
                    res = self.get_posting(term)
                    stack.append(res if res is not None else [])

        return stack[0] if stack else []

    # 🔹 Main query processor
    def queryProcessing(self, query):
        tokens = self.tokenize(query)
        postfix = self.infix_to_postfix(tokens)
        return self.evaluate_postfix(postfix)

    # 🔹 Wrapper
    def queryInput(self, query):
        return self.queryProcessing(query)

    # 🔹 Display results
    def generateResultSet(self, result):
        print("total documents found:", len(result))
        print("Result:", result)