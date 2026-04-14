# Design Notes and TODOs

Living document for design decisions, open questions, and task tracking.
Both Aaron and Shannon should edit this freely.

## Open Design Questions

- **Index format:** keep 32 per-chunk index files from Checkpoint 2 and query
  across them, or merge into a single global index? Leaning toward merge for
  simplicity. Decision needed before BM25 implementation.
- **Document length storage:** separate `doc_lengths.txt` file, or fold into
  the main index? Separate file is cleaner; the index stays pure postings.
- **Stopword list:** Checkpoint 2 used NLTK's English stopwords. Stick with
  that for consistency.
- **BM25 parameters:** start with standard defaults (k1=1.2, b=0.75), then
  tune as part of the parameter sweep.
- **PRF term scoring:** Rocchio-style, RSV, or KL-divergence? Start with
  Rocchio (simplest), add RSV as a comparison if time permits.
- **PRF parameters:** how many feedback docs (k) and how many expansion
  terms (m)? Sweep across {5, 10, 20} x {5, 10, 20, 50}.

## Task List

### Phase 1: Infrastructure
- [x] Set up repo structure
- [ ] Port Checkpoint 1 preprocessing code into `src/preprocessing.py`
- [ ] Port Checkpoint 2 indexer code into `src/indexer.py`
- [ ] Write `scripts/merge_indexes.py` to combine 32 chunk indexes
- [ ] Write `scripts/compute_doc_lengths.py` for length statistics
- [ ] Extend index to support BM25 lookups (term -> postings, doc -> length)

### Phase 2: Ranking
- [ ] Implement BM25 in `src/bm25.py`
- [ ] Implement `src/search.py` CLI for ad-hoc queries
- [ ] Sanity-check: do obvious queries return obviously relevant documents?

### Phase 3: Evaluation Set
- [ ] Brainstorm 20+ information needs (together, in one sitting)
- [ ] Convert to query strings, fill in `data/queries.tsv`
- [ ] Fill in `data/information_needs.md` with needs + categories
- [ ] Freeze the query set (commit, do not modify after)

### Phase 4: PRF
- [ ] Implement term scoring (Rocchio or RSV) in `src/prf.py`
- [ ] Implement query expansion + second-pass retrieval
- [ ] Integrate with `src/search.py` as a `--prf` flag

### Phase 5: Evaluation
- [ ] Pool results from BM25 and BM25+PRF for each query (top-10)
- [ ] Judge pooled documents blind (split between Aaron and Shannon)
- [ ] Report Cohen's kappa on overlapping judgments
- [ ] Save judgments as `data/qrels.txt` in TREC format
- [ ] Implement P@k, MAP, nDCG in `src/evaluate.py`
- [ ] Parameter sweep over k and m; produce comparison tables

### Phase 6: Writeup
- [ ] Draft final report
- [ ] Produce result plots (MAP/nDCG vs. parameters)
- [ ] Prepare presentation slides

## Meeting Notes

### YYYY-MM-DD
- Attendees:
- Decisions:
- Next steps:
