import ast
import re


class Queries:
    def __init__(self, processor_obj, filepath="inverted_index.txt"):
        self.index = self.load_index(filepath)
        self.processor = processor_obj
        self.all_docs = self.getAllDocs()

    # Reads the inverted index from a text file and returns it as a dictionary.
    # Each line is expected in the format: word -> {doc_id: [positions]}
    def load_index(self, filepath):
        index = {}
        with open(filepath, "r") as f:
            for line in f:
                if "->" not in line:
                    continue
                word, postings = line.split("->", 1)
                index[word.strip()] = ast.literal_eval(postings.strip())
        return index

    # Collects and returns the set of all document IDs present in the index.
    def getAllDocs(self):
        docs = set()
        for postings in self.index.values():
            for doc_id in postings.keys():
                docs.add(str(doc_id))
        return docs

    # Returns the list of document IDs that contain the given term.
    def get_posting(self, term):
        return sorted([str(doc) for doc in self.index.get(term, {}).keys()])

    # Returns documents that appear in both lists a and b.
    def AND(self, a, b):
        a = a or []
        b = b or []
        return sorted(set(a) & set(b))

    # Returns documents that appear in either list a or b.
    def OR(self, a, b):
        a = a or []
        b = b or []
        return sorted(set(a) | set(b))

    # Returns all documents that are NOT in list a.
    def NOT(self, a):
        a = a or []
        return sorted(self.all_docs - set(a))

    # Finds documents where term t1 appears before t2 within k words of each other.
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
            i = j = 0
            found = False
            while i < len(pos1) and j < len(pos2) and not found:
                diff = pos2[j] - pos1[i] - 1
                if 0 <= diff <= k:
                    result.append(str(doc))
                    found = True
                elif pos1[i] < pos2[j]:
                    i += 1
                else:
                    j += 1

        return sorted(result)

    # Finds documents that contain the exact sequence of words in the given phrase.
    # Format for phrase queries: "word1 word2 word3" -> words should be enclosed in quotes, if they are not then they will be treated as normal terms and not as a phrase query.
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

        common_docs = set(postings[0].keys())
        for p in postings[1:]:
            common_docs &= set(p.keys())

        result = []
        for doc in common_docs:
            positions = list(postings[0][doc])
            for i in range(1, len(postings)):
                next_pos = postings[i][doc]
                temp = [pos + 1 for pos in positions if pos + 1 in next_pos]
                positions = temp
                if not positions:
                    break
            if positions:
                result.append(str(doc))

        return sorted(result)

    # Splits a raw query string into a list of tokens.
    # Handles boolean operators, parentheses, phrase queries (quoted strings),
    # and proximity queries (t1 t2 /k format).
    def tokenize(self, query):
        tokens = []
        i = 0
        words = query.split()

        while i < len(words):
            word = words[i]

            # Proximity query detected when the third word starts with /digit
            if i + 2 < len(words) and re.search(r'/\d+', words[i + 2]):
                t1    = words[i].strip('()')
                t2    = words[i + 1].strip('()')
                raw_k = words[i + 2].strip('()')
                lead  = words[i].count('(')
                trail = words[i + 2].count(')')
                for _ in range(lead):
                    tokens.append('(')
                tokens.append((t1, t2, raw_k))
                for _ in range(trail):
                    tokens.append(')')
                i += 3
                continue

            # Phrase query: collect words until the closing quote is found
            if word.startswith('"'):
                phrase = word[1:]
                while i < len(words) - 1 and not words[i].endswith('"'):
                    i += 1
                    phrase += ' ' + words[i].replace('"', '')
                phrase = phrase.rstrip('"')
                tokens.append(phrase)
                i += 1
                continue

            # Strip all leading parentheses
            leading_parens = []
            while word.startswith('('):
                leading_parens.append('(')
                word = word[1:]

            # Strip all trailing parentheses
            trailing_parens = []
            while word.endswith(')'):
                trailing_parens.append(')')
                word = word[:-1]

            tokens.extend(leading_parens)

            if word:
                if word.lower() in ('and', 'or', 'not'):
                    tokens.append(word.upper())
                else:
                    tokens.append(word)

            tokens.extend(trailing_parens)

            i += 1

        return tokens

    # Converts a list of tokens from infix order to postfix order
    # using the Shunting-Yard algorithm, respecting operator precedence:
    # NOT (highest) > AND > OR (lowest).
    def infix_to_postfix(self, tokens):
        precedence = {'NOT': 3, 'AND': 2, 'OR': 1}
        output = []
        stack  = []

        for token in tokens:
            if isinstance(token, tuple):
                output.append(token)

            elif isinstance(token, str) and token in ('AND', 'OR', 'NOT'):
                while (stack
                       and stack[-1] != '('
                       and isinstance(stack[-1], str)
                       and precedence.get(stack[-1], 0) >= precedence.get(token, 0)):
                    output.append(stack.pop())
                stack.append(token)

            elif token == '(':
                stack.append(token)

            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()

            else:
                output.append(token)

        while stack:
            top = stack.pop()
            if top != '(':
                output.append(top)

        return output

    # Evaluates a postfix token list and returns the matching document IDs.
    # Operands are pushed onto the stack; operators pop and combine them.
    def evaluate_postfix(self, tokens):
        stack = []

        for token in tokens:

            if isinstance(token, tuple):
                t1_raw, t2_raw, k_raw = token
                k_match = re.search(r'\d+', k_raw)
                if not k_match:
                    raise ValueError(f"Invalid proximity value: {k_raw!r}")
                k = int(k_match.group())
                p1 = self.processor.processQuery(t1_raw)
                p2 = self.processor.processQuery(t2_raw)
                t1 = p1[0] if p1 else t1_raw
                t2 = p2[0] if p2 else t2_raw
                stack.append(self.proximityQuery(t1, t2, k))

            elif token == 'AND':
                if len(stack) < 2:
                    raise ValueError("Invalid query: AND requires two operands")
                b = stack.pop() or []
                a = stack.pop() or []
                stack.append(self.AND(a, b))

            elif token == 'OR':
                if len(stack) < 2:
                    raise ValueError("Invalid query: OR requires two operands")
                b = stack.pop() or []
                a = stack.pop() or []
                stack.append(self.OR(a, b))

            elif token == 'NOT':
                if not stack:
                    raise ValueError("Invalid query: NOT has no operand")
                a = stack.pop() or []
                stack.append(self.NOT(a))

            else:
                if ' ' in token:
                    res = self.phraseQuery(token)
                else:
                    p = self.processor.processQuery(token)
                    term = p[0] if p else token
                    res = self.get_posting(term)
                stack.append(res if res is not None else [])

        return stack[0] if stack else []

    # Runs the full query pipeline: tokenize -> convert to postfix -> evaluate.
    def queryProcessing(self, query):
        tokens  = self.tokenize(query)
        postfix = self.infix_to_postfix(tokens)
        return self.evaluate_postfix(postfix)

    def queryInput(self, query):
        return self.queryProcessing(query)

    # Prints the total number of results and the list of matching document IDs.
    def generateResultSet(self, result):
        print("total documents found:", len(result))
        print("Result:", result)