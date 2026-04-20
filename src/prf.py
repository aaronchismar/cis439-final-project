import math
from collections import defaultdict
from src.preprocessing import process_query
from src.indexer import load_global_index, load_doc_lengths
from src.bm25 import BM25


class PRF:

    def __init__(self, index_dir='.', k1=1.2, b=0.75):
        self.ranker = BM25(index_dir=index_dir, k1=k1, b=b)
        self.index = self.ranker.index
        self.doc_lengths = self.ranker.doc_lengths
        self.avg_dl = self.ranker.avg_dl
        self.N = self.ranker.N

    def _get_doc_terms_batch(self, doc_ids):
        # Scans the index once to collect tf values for all feedback docs
        doc_id_set = set(doc_ids)
        result = {did: {} for did in doc_ids}

        for term, entry in self.index.items():
            for did, tf in entry["postings"]:
                if did in doc_id_set:
                    result[did][term] = tf

        return result

    def score_expansion_terms(self, query_terms, feedback_docs, top_m=10):
        # Scores candidates as: idf(t) * avg_tf_in_feedback_docs
        # Excludes original query terms
        query_term_set = set(query_terms)
        k = len(feedback_docs)
        if k == 0:
            return []

        feedback_doc_ids = [doc_id for doc_id, _ in feedback_docs]
        doc_term_maps = self._get_doc_terms_batch(feedback_doc_ids)

        term_scores = defaultdict(float)
        for doc_id in feedback_doc_ids:
            for term, tf in doc_term_maps[doc_id].items():
                if term in query_term_set:
                    continue
                term_scores[term] += tf

        scored_terms = []
        for term, tf_sum in term_scores.items():
            if term not in self.index:
                continue
            df = self.index[term]["df"]
            idf = math.log((self.N + 1) / df)
            score = idf * (tf_sum / k)
            scored_terms.append((term, score))

        scored_terms.sort(key=lambda x: -x[1])
        return scored_terms[:top_m]

    def expand_query(self, query_terms, expansion_terms):
        # Appends expansion terms to the original query
        expanded = list(query_terms)
        for term, score in expansion_terms:
            expanded.append(term)
        return expanded

    def search(self, query_text, top_k_docs=10, top_m_terms=10, final_top_k=10):
        # 1. Initial BM25  2. Score expansion terms  3. Expand query  4. Re-rank
        query_terms = process_query(query_text)
        initial_results = self.ranker.search_with_terms(query_terms, top_k=top_k_docs)

        if not initial_results:
            return {
                "query_terms": query_terms,
                "initial_results": [],
                "expansion_terms": [],
                "expanded_query": query_terms,
                "final_results": []
            }

        expansion_terms = self.score_expansion_terms(
            query_terms, initial_results, top_m=top_m_terms
        )

        expanded_query = self.expand_query(query_terms, expansion_terms)
        final_results = self.ranker.search_with_terms(expanded_query, top_k=final_top_k)

        return {
            "query_terms": query_terms,
            "initial_results": initial_results,
            "expansion_terms": expansion_terms,
            "expanded_query": expanded_query,
            "final_results": final_results
        }


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 -m src.prf <query> [--k <feedback_docs>] [--m <expansion_terms>]")
        print('Example: python3 -m src.prf "heart attack symptoms"')
        print('Example: python3 -m src.prf "heart attack symptoms" --k 5 --m 20')
        sys.exit(1)

    args = sys.argv[1:]
    top_k_docs = 10
    top_m_terms = 10
    query_parts = []

    i = 0
    while i < len(args):
        if args[i] == '--k' and i + 1 < len(args):
            top_k_docs = int(args[i + 1])
            i += 2
        elif args[i] == '--m' and i + 1 < len(args):
            top_m_terms = int(args[i + 1])
            i += 2
        else:
            query_parts.append(args[i])
            i += 1

    query = ' '.join(query_parts)

    prf = PRF(index_dir='.')
    result = prf.search(query, top_k_docs=top_k_docs, top_m_terms=top_m_terms)

    print(f"\nQuery: {query}")
    print(f"Stemmed query terms: {result['query_terms']}")

    print(f"\n--- Initial BM25 Results (top {top_k_docs} feedback docs) ---\n")
    print(f"{'Rank':<6} {'Doc ID':<12} {'Score':<12}")
    print("-" * 30)
    for rank, (doc_id, score) in enumerate(result['initial_results'], 1):
        print(f"{rank:<6} {doc_id:<12} {score:<12.4f}")

    print(f"\n--- Expansion Terms (top {top_m_terms}) ---\n")
    print(f"{'Rank':<6} {'Term':<25} {'Score':<12}")
    print("-" * 43)
    for rank, (term, score) in enumerate(result['expansion_terms'], 1):
        print(f"{rank:<6} {term:<25} {score:<12.4f}")

    print(f"\n--- Expanded Query ---")
    print(f"  {result['expanded_query']}")

    print(f"\n--- Final Re-ranked Results ---\n")
    print(f"{'Rank':<6} {'Doc ID':<12} {'Score':<12}")
    print("-" * 30)
    for rank, (doc_id, score) in enumerate(result['final_results'], 1):
        print(f"{rank:<6} {doc_id:<12} {score:<12.4f}")
