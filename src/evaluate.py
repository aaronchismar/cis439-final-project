import math
import sys
import os
from src.bm25 import BM25
from src.prf import PRF


# Loading queries and relevance judgments

def load_queries(path):
    # Loads queries.tsv, returns dict: {query_id: query_text}
    queries = {}
    with open(path, 'r', encoding='utf-8') as f:
        header = next(f)
        for line in f:
            line = line.rstrip('\n')
            if '\t' not in line:
                continue
            qid, text = line.split('\t', 1)
            if text.strip():
                queries[qid] = text.strip()
    return queries


def load_qrels(path):
    # Loads qrels.txt in TREC format: query_id 0 doc_id relevance
    # Returns dict: {query_id: {doc_id: relevance_grade}}
    qrels = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            qid, _, doc_id, rel = parts[0], parts[1], parts[2], int(parts[3])
            if qid not in qrels:
                qrels[qid] = {}
            qrels[qid][doc_id] = rel
    return qrels


# Metric computations

def precision_at_k(ranked_docs, relevant_docs, k):
    # P@k: fraction of top-k results that are relevant (grade > 0)
    top_k = ranked_docs[:k]
    relevant_count = sum(1 for doc_id, _ in top_k if relevant_docs.get(doc_id, 0) > 0)
    return relevant_count / k if k > 0 else 0.0


def average_precision(ranked_docs, relevant_docs):
    # AP: average of P@k at each position where a relevant doc appears
    num_relevant = sum(1 for rel in relevant_docs.values() if rel > 0)
    if num_relevant == 0:
        return 0.0

    cumulative_relevant = 0
    ap_sum = 0.0

    for rank, (doc_id, _) in enumerate(ranked_docs, 1):
        if relevant_docs.get(doc_id, 0) > 0:
            cumulative_relevant += 1
            ap_sum += cumulative_relevant / rank

    return ap_sum / num_relevant


def dcg_at_k(ranked_docs, relevant_docs, k):
    # DCG@k using graded relevance: sum of rel(i) / log2(i + 1)
    dcg = 0.0
    for i, (doc_id, _) in enumerate(ranked_docs[:k]):
        rel = relevant_docs.get(doc_id, 0)
        dcg += rel / math.log2(i + 2)
    return dcg


def ndcg_at_k(ranked_docs, relevant_docs, k):
    # nDCG@k: DCG@k normalized by ideal DCG@k
    dcg = dcg_at_k(ranked_docs, relevant_docs, k)

    # Ideal ranking: sort all judged docs by relevance descending
    ideal_rels = sorted(relevant_docs.values(), reverse=True)
    idcg = 0.0
    for i, rel in enumerate(ideal_rels[:k]):
        idcg += rel / math.log2(i + 2)

    if idcg == 0:
        return 0.0
    return dcg / idcg


# Running evaluation across all queries

def evaluate_run(ranked_results, qrels, k=10):
    # Computes P@k, AP, and nDCG@k for each query in the run.
    # ranked_results: {query_id: [(doc_id, score), ...]}
    # Returns per-query metrics and macro averages.
    per_query = {}

    for qid in sorted(ranked_results.keys()):
        if qid not in qrels:
            continue

        ranked = ranked_results[qid]
        relevant = qrels[qid]

        per_query[qid] = {
            "P@k": precision_at_k(ranked, relevant, k),
            "AP": average_precision(ranked, relevant),
            "nDCG@k": ndcg_at_k(ranked, relevant, k)
        }

    num_queries = len(per_query)
    if num_queries == 0:
        return per_query, {"MAP": 0.0, "P@k": 0.0, "nDCG@k": 0.0}

    averages = {
        "MAP": sum(m["AP"] for m in per_query.values()) / num_queries,
        "P@k": sum(m["P@k"] for m in per_query.values()) / num_queries,
        "nDCG@k": sum(m["nDCG@k"] for m in per_query.values()) / num_queries
    }

    return per_query, averages


# Generating ranked runs from BM25 and PRF

def generate_bm25_run(ranker, queries, top_k=10):
    # Runs each query through BM25, returns {qid: [(doc_id, score), ...]}
    results = {}
    for qid, text in queries.items():
        results[qid] = ranker.search(text, top_k=top_k)
    return results


def generate_prf_run(prf_ranker, queries, top_k_docs=10, top_m_terms=10, final_top_k=10):
    # Runs each query through PRF, returns {qid: [(doc_id, score), ...]}
    results = {}
    for qid, text in queries.items():
        prf_result = prf_ranker.search(text, top_k_docs=top_k_docs,
                                       top_m_terms=top_m_terms,
                                       final_top_k=final_top_k)
        results[qid] = prf_result["final_results"]
    return results


# Writing results in TREC run format

def write_run(results, path, run_name="run"):
    # Writes ranked results in TREC format:
    # query_id Q0 doc_id rank score run_name
    with open(path, 'w', encoding='utf-8') as f:
        for qid in sorted(results.keys()):
            for rank, (doc_id, score) in enumerate(results[qid], 1):
                f.write(f"{qid} Q0 {doc_id} {rank} {score:.4f} {run_name}\n")


# Pooling results for relevance judging

def pool_results(runs, top_k=10):
    # Unions the top-k results from multiple runs per query.
    # Returns {query_id: set(doc_ids)}
    pool = {}
    for run in runs:
        for qid, ranked in run.items():
            if qid not in pool:
                pool[qid] = set()
            for doc_id, _ in ranked[:top_k]:
                pool[qid].add(doc_id)
    return pool


def write_pool_for_judging(pool, path):
    # Writes a shuffled judging spreadsheet (TSV) with no method info.
    # Columns: query_id, doc_id, relevance (blank, to be filled in)
    import random
    rows = []
    for qid in sorted(pool.keys()):
        for doc_id in pool[qid]:
            rows.append((qid, doc_id))

    random.shuffle(rows)

    with open(path, 'w', encoding='utf-8') as f:
        f.write("query_id\tdoc_id\trelevance\n")
        for qid, doc_id in rows:
            f.write(f"{qid}\t{doc_id}\t\n")


# Display helpers

def print_comparison(bm25_metrics, prf_metrics, bm25_per_query, prf_per_query, k):
    print(f"\n{'='*60}")
    print(f"  Evaluation Results (k={k})")
    print(f"{'='*60}")

    print(f"\n--- Per-Query Breakdown ---\n")
    print(f"{'Query':<8} {'Metric':<10} {'BM25':<10} {'BM25+PRF':<10} {'Delta':<10}")
    print("-" * 48)

    for qid in sorted(bm25_per_query.keys()):
        for metric in ["P@k", "AP", "nDCG@k"]:
            bm25_val = bm25_per_query[qid][metric]
            prf_val = prf_per_query.get(qid, {}).get(metric, 0.0)
            delta = prf_val - bm25_val
            sign = "+" if delta >= 0 else ""
            print(f"{qid:<8} {metric:<10} {bm25_val:<10.4f} {prf_val:<10.4f} {sign}{delta:<10.4f}")
        print()

    print(f"--- Macro Averages ---\n")
    print(f"{'Metric':<10} {'BM25':<10} {'BM25+PRF':<10} {'Delta':<10}")
    print("-" * 40)
    for metric in ["P@k", "MAP", "nDCG@k"]:
        bm25_val = bm25_metrics[metric]
        prf_val = prf_metrics[metric]
        delta = prf_val - bm25_val
        sign = "+" if delta >= 0 else ""
        print(f"{metric:<10} {bm25_val:<10.4f} {prf_val:<10.4f} {sign}{delta:<10.4f}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate BM25 vs BM25+PRF")
    parser.add_argument("--queries", default="data/queries.tsv", help="Path to queries.tsv")
    parser.add_argument("--qrels", default="data/qrels.txt", help="Path to qrels.txt")
    parser.add_argument("--index-dir", default=".", help="Directory with index files")
    parser.add_argument("--k", type=int, default=10, help="k for P@k and nDCG@k")
    parser.add_argument("--prf-k", type=int, default=10, help="Number of feedback docs for PRF")
    parser.add_argument("--prf-m", type=int, default=10, help="Number of expansion terms for PRF")
    parser.add_argument("--pool-only", action="store_true",
                        help="Generate pooled judging sheet instead of evaluating")
    args = parser.parse_args()

    queries = load_queries(args.queries)
    print(f"Loaded {len(queries)} queries from {args.queries}")

    # Initialize rankers (shared index load)
    prf_ranker = PRF(index_dir=args.index_dir)
    bm25_ranker = prf_ranker.ranker

    # Generate runs
    print("\nRunning BM25...")
    bm25_run = generate_bm25_run(bm25_ranker, queries, top_k=args.k)

    print("Running BM25+PRF...")
    prf_run = generate_prf_run(prf_ranker, queries, top_k_docs=args.prf_k,
                               top_m_terms=args.prf_m, final_top_k=args.k)

    # Save runs in TREC format
    os.makedirs("results", exist_ok=True)
    write_run(bm25_run, "results/bm25_run.txt", run_name="bm25")
    write_run(prf_run, "results/prf_run.txt", run_name="bm25_prf")
    print("Saved runs to results/bm25_run.txt and results/prf_run.txt")

    if args.pool_only:
        # Generate pooled judging sheet and exit
        pool = pool_results([bm25_run, prf_run], top_k=args.k)
        total_judgments = sum(len(docs) for docs in pool.values())
        write_pool_for_judging(pool, "data/judging_pool.tsv")
        print(f"\nGenerated data/judging_pool.tsv with {total_judgments} judgments to make")
        print("Fill in the 'relevance' column (0-3) and save as data/qrels.txt")
        sys.exit(0)

    # Full evaluation
    qrels = load_qrels(args.qrels)
    print(f"Loaded qrels for {len(qrels)} queries from {args.qrels}")

    bm25_per_query, bm25_avg = evaluate_run(bm25_run, qrels, k=args.k)
    prf_per_query, prf_avg = evaluate_run(prf_run, qrels, k=args.k)

    print_comparison(bm25_avg, prf_avg, bm25_per_query, prf_per_query, args.k)
