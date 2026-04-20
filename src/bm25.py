import math
from src.preprocessing import process_query
from src.indexer import load_global_index, load_doc_lengths


class BM25:
    # BM25 ranker over a pre-built global inverted index.
    #
    # Usage:
    #   ranker = BM25(index_dir='.')
    #   results = ranker.search("heart attack symptoms", top_k=10)

    def __init__(self, index_dir='.', k1=1.2, b=0.75):
        # k1: term frequency saturation parameter (higher = more weight to tf)
        # b: length normalization parameter (0 = no normalization, 1 = full)
        self.k1 = k1
        self.b = b

        # Load the inverted index and document length stats
        print("Loading global index...")
        self.index = load_global_index(index_dir)

        print("Loading document lengths...")
        self.doc_lengths, self.avg_dl, self.N = load_doc_lengths(index_dir)

        print(f"BM25 ready: {len(self.index)} terms, {self.N} documents")
        print(f"  avg_dl = {self.avg_dl:.2f}, k1 = {self.k1}, b = {self.b}")

    def _idf(self, df):
        # Inverse document frequency: log((N + 1) / df)
        # Using the variant from the CIS 439 course material.
        return math.log((self.N + 1) / df)

    def _tf_component(self, tf, doc_len):
        # BM25 term frequency component with length normalization.
        # tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avg_dl))
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_dl))
        return numerator / denominator

    def score_document(self, query_terms, doc_id, doc_tf_map):
        # Computes the BM25 score for a single document given query terms.
        # query_terms: list of stemmed query tokens
        # doc_id: the document id string
        # doc_tf_map: dict mapping query_term -> tf in this document
        doc_len = float(self.doc_lengths.get(doc_id, self.avg_dl))
        score = 0.0

        for term in query_terms:
            if term not in doc_tf_map:
                continue
            if term not in self.index:
                continue

            tf = doc_tf_map[term]
            df = self.index[term]["df"]

            idf = self._idf(df)
            tf_comp = self._tf_component(tf, doc_len)
            score += idf * tf_comp

        return score

    def search(self, query_text, top_k=10):
        # Searches the index for documents matching the query.
        # Returns a list of (doc_id, score) tuples, sorted by descending score.
        query_terms = process_query(query_text)

        if not query_terms:
            return []

        # Deduplicate query terms but track frequency for potential weighting
        unique_terms = list(set(query_terms))

        # Collect candidate documents: any doc containing at least one query term
        # Build a per-document tf map for the query terms
        doc_scores = {}

        for term in unique_terms:
            if term not in self.index:
                continue

            entry = self.index[term]
            idf = self._idf(entry["df"])

            for doc_id, tf in entry["postings"]:
                doc_len = float(self.doc_lengths.get(doc_id, self.avg_dl))
                tf_comp = self._tf_component(tf, doc_len)
                term_score = idf * tf_comp

                if doc_id in doc_scores:
                    doc_scores[doc_id] += term_score
                else:
                    doc_scores[doc_id] = term_score

        # Sort by score descending, then by doc_id ascending for ties
        ranked = sorted(doc_scores.items(), key=lambda x: (-x[1], int(x[0])))

        return ranked[:top_k]

    def search_with_terms(self, query_terms, top_k=10):
        # Like search(), but takes pre-processed (stemmed) query terms directly.
        # Useful for PRF where the expanded query is already tokenized.
        if not query_terms:
            return []

        unique_terms = list(set(query_terms))
        doc_scores = {}

        for term in unique_terms:
            if term not in self.index:
                continue

            entry = self.index[term]
            idf = self._idf(entry["df"])

            for doc_id, tf in entry["postings"]:
                doc_len = float(self.doc_lengths.get(doc_id, self.avg_dl))
                tf_comp = self._tf_component(tf, doc_len)
                term_score = idf * tf_comp

                if doc_id in doc_scores:
                    doc_scores[doc_id] += term_score
                else:
                    doc_scores[doc_id] = term_score

        ranked = sorted(doc_scores.items(), key=lambda x: (-x[1], int(x[0])))

        return ranked[:top_k]


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 -m src.bm25 <query>")
        print("  Run from the directory containing global_index.txt and doc_lengths.json")
        print('Example: python3 -m src.bm25 "heart attack symptoms"')
        sys.exit(1)

    query = ' '.join(sys.argv[1:])
    ranker = BM25(index_dir='.')
    results = ranker.search(query, top_k=10)

    print(f"\nQuery: {query}")
    print(f"Results ({len(results)} documents):\n")
    print(f"{'Rank':<6} {'Doc ID':<12} {'Score':<12}")
    print("-" * 30)
    for rank, (doc_id, score) in enumerate(results, 1):
        print(f"{rank:<6} {doc_id:<12} {score:<12.4f}")
