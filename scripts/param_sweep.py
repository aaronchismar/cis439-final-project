import sys
import os
from src.bm25 import BM25
from src.prf import PRF
from src.evaluate import (load_queries, load_qrels, generate_bm25_run,
                          generate_prf_run, evaluate_run)


def run_sweep(queries_path, qrels_path, index_dir='.', eval_k=10):
    queries = load_queries(queries_path)
    qrels = load_qrels(qrels_path)

    print(f"Loaded {len(queries)} queries, qrels for {len(qrels)} queries")

    # Initialize rankers (shared index load)
    prf_ranker = PRF(index_dir=index_dir)
    bm25_ranker = prf_ranker.ranker

    # BM25 baseline
    print("\nRunning BM25 baseline...")
    bm25_run = generate_bm25_run(bm25_ranker, queries, top_k=eval_k)
    _, bm25_avg = evaluate_run(bm25_run, qrels, k=eval_k)

    print(f"\nBM25 Baseline:  P@{eval_k}={bm25_avg['P@k']:.4f}  "
          f"MAP={bm25_avg['MAP']:.4f}  nDCG@{eval_k}={bm25_avg['nDCG@k']:.4f}")

    # PRF parameter grid
    k_values = [3, 5, 10, 15, 20]
    m_values = [5, 10, 15, 20, 50]

    print(f"\n{'k':<6} {'m':<6} {'P@10':<10} {'MAP':<10} {'nDCG@10':<10} {'MAP Delta':<10}")
    print("-" * 52)

    best_map = 0
    best_params = None

    for k in k_values:
        for m in m_values:
            prf_run = generate_prf_run(prf_ranker, queries,
                                       top_k_docs=k, top_m_terms=m,
                                       final_top_k=eval_k)
            _, prf_avg = evaluate_run(prf_run, qrels, k=eval_k)

            delta = prf_avg['MAP'] - bm25_avg['MAP']
            sign = "+" if delta >= 0 else ""

            print(f"{k:<6} {m:<6} {prf_avg['P@k']:<10.4f} {prf_avg['MAP']:<10.4f} "
                  f"{prf_avg['nDCG@k']:<10.4f} {sign}{delta:<10.4f}")

            if prf_avg['MAP'] > best_map:
                best_map = prf_avg['MAP']
                best_params = (k, m)

    print(f"\nBest PRF config: k={best_params[0]}, m={best_params[1]} (MAP={best_map:.4f})")
    print(f"BM25 baseline MAP: {bm25_avg['MAP']:.4f}")
    delta = best_map - bm25_avg['MAP']
    sign = "+" if delta >= 0 else ""
    print(f"Best improvement: {sign}{delta:.4f}")


if __name__ == '__main__':
    queries_path = sys.argv[1] if len(sys.argv) > 1 else "data/queries.tsv"
    qrels_path = sys.argv[2] if len(sys.argv) > 2 else "data/qrels.txt"

    run_sweep(queries_path, qrels_path)
