# Boolean Information Retrieval System

A Boolean Information Retrieval system built in Python with a Streamlit web interface. It indexes a corpus of 56 Trump speech documents using a **positional inverted index** and supports Boolean, phrase, and proximity queries.

## Features

- **Positional Inverted Index** — tracks every term's position in every document for phrase and proximity lookups
- **Boolean Queries** — `AND`, `OR`, `NOT` with full operator precedence and parentheses grouping
- **Phrase Queries** — exact multi-word phrase matching (e.g. `"Hillary Clinton"`)
- **Proximity Queries** — positional distance search (e.g. `keep out /2`)
- **Text Preprocessing** — lowercasing, contraction expansion, Unicode normalization, stemming (Porter), and stopword filtering
- **Streamlit UI** — dark-themed web interface with a query guide sidebar and result metrics

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
pip install streamlit nltk contractions unidecode
```

### Run the App

```bash
streamlit run app.py
```

Opens in your browser at `http://localhost:8501`. The index is built automatically on first launch.

## Query Syntax

| Type | Example |
|------|---------|
| Boolean AND | `actions AND wanted` |
| Boolean OR | `united OR plane` |
| Boolean NOT | `NOT hammer` |
| Grouped | `biggest AND (near OR box)` |
| Phrase | `"air crash landing"` |
| Proximity | `crash land /2` — t1 before t2 within 2 words |
| Combined | `"air crash" AND NOT boeing` |

## Project Structure

```
.
├── app.py                  # Streamlit web interface
├── processor.py            # Inverted index builder & text preprocessing
├── Queries.py              # Query parser and evaluator (Boolean/phrase/proximity)
├── DocumentExtraction.py   # Loads the speech corpus from disk
├── inverted_index.txt      # Pre-built index (auto-generated)
├── Stopword-List.txt       # Stopwords used during preprocessing
├── Querry List.txt         # Sample queries for testing
└── Trump Speechs/          # Corpus — 56 speech documents (speech_0 to speech_55)
```

## How It Works

1. **Indexing** — `DocumentExtraction` reads all 56 speeches. `InvertedIndex` preprocesses each document (normalize → tokenize → stem → filter) and records each term's positions per document.
2. **Query Parsing** — `Queries` tokenizes the raw query, detects operators and query types, and converts it to postfix notation via the Shunting-Yard algorithm.
3. **Evaluation** — The postfix expression is evaluated using posting list operations (`AND`/`OR`/`NOT` set operations, phrase position matching, proximity window checks).
