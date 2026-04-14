# CIS 439 Final Project: Query Expansion with Pseudo-Relevance Feedback

A BM25 retrieval system over the wiki2022 corpus, extended with pseudo-relevance
feedback (PRF) for automatic query expansion. Built for CIS 439/536 at the
University of Michigan - Dearborn.

**Team:** Aaron Chismar, Shannon A. Mendonca

## Overview

This project implements a full information retrieval pipeline and measures
whether PRF meaningfully improves retrieval quality over a BM25 baseline.
It builds directly on the preprocessing pipeline from Checkpoint #1 (tokenizer,
Porter stemmer) and the inverted index from Checkpoint #2.

## Project Structure

```
cis439-final-project/
├── src/            # Core source code (preprocessing, indexing, ranking, PRF, eval)
├── scripts/        # One-off utilities (index merging, doc length computation)
├── data/           # Query set, information needs, relevance judgments (qrels)
├── results/        # Ranked run outputs in TREC format
├── docs/           # Proposal, design notes, meeting notes
└── requirements.txt
```

The wiki2022 corpus itself is NOT tracked in git (too large). Place the
unzipped corpus in a `wiki2022/` folder at the repo root; it will be gitignored.

## Setup

Requires Python 3.9+ on macOS or Linux.

```bash
# Clone the repo
git clone <repo-url>
cd cis439-final-project

# Install dependencies
pip3 install -r requirements.txt

# Place the wiki2022 dataset at ./wiki2022/ (not included in repo)
```

## Usage

TBD as components come online. Rough plan:

```bash
# Build the inverted index with document length stats
python3 -m src.indexer ./wiki2022

# Run a BM25 query
python3 -m src.search "heart attack symptoms"

# Run full evaluation over the query set
python3 -m src.evaluate --method bm25
python3 -m src.evaluate --method bm25_prf
```

## Components

| File | Purpose |
|------|---------|
| `src/preprocessing.py` | Tokenization, stopword removal, Porter stemming (from Ckpt 1) |
| `src/indexer.py` | Inverted index with document length stats (extends Ckpt 2) |
| `src/bm25.py` | BM25 ranking function with tunable k1 and b |
| `src/prf.py` | Pseudo-relevance feedback: term scoring and query expansion |
| `src/evaluate.py` | Precision@k, MAP, nDCG computation |
| `src/search.py` | Main query interface |

## Evaluation

We author our own query set and relevance judgments since Wikipedia does not
come with pre-built qrels. See `data/information_needs.md` for methodology.

- `data/queries.tsv` - 20 queries in TSV format
- `data/information_needs.md` - human-readable need descriptions
- `data/qrels.txt` - relevance judgments in TREC qrels format

## Development Conventions

- Python 3, hash-style comments, empty lines as separators (no `# ---` dividers)
- Pre-approved libraries only: `nltk`, `numpy`, `pandas`
- BM25 scoring, index logic, and PRF implemented from scratch
- Commits should be small and focused; one logical change per commit
- Branch off `main` for non-trivial work, open a PR for review before merging

## References

- Proposal: `docs/proposal.pdf`
- Design notes and TODOs: `docs/notes.md`
