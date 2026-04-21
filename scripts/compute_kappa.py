import sys


def load_qrels(path):
    # Loads qrels file, returns dict: {(query_id, doc_id): relevance}
    judgments = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            qid, _, doc_id, rel = parts[0], parts[1], parts[2], int(parts[3])
            judgments[(qid, doc_id)] = rel
    return judgments


def compute_kappa(judgments_a, judgments_b):
    # Finds overlapping (qid, doc_id) pairs and computes Cohen's kappa
    overlap_keys = set(judgments_a.keys()) & set(judgments_b.keys())

    if not overlap_keys:
        print("No overlapping judgments found.")
        return None

    labels_a = [judgments_a[k] for k in sorted(overlap_keys)]
    labels_b = [judgments_b[k] for k in sorted(overlap_keys)]

    # All possible categories
    categories = sorted(set(labels_a + labels_b))
    n = len(labels_a)

    # Observed agreement
    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    po = agree / n

    # Expected agreement by chance
    pe = 0.0
    for cat in categories:
        count_a = sum(1 for a in labels_a if a == cat)
        count_b = sum(1 for b in labels_b if b == cat)
        pe += (count_a / n) * (count_b / n)

    if pe == 1.0:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1 - pe)

    return kappa, po, pe, n, overlap_keys, labels_a, labels_b


def print_confusion_matrix(labels_a, labels_b, categories):
    # Prints a confusion matrix of annotator A vs annotator B
    print(f"\n{'':>8}", end='')
    for cat in categories:
        print(f"  B={cat}", end='')
    print()
    print("-" * (8 + 6 * len(categories)))

    for cat_a in categories:
        print(f"A={cat_a:>3}  ", end='')
        for cat_b in categories:
            count = sum(1 for a, b in zip(labels_a, labels_b) if a == cat_a and b == cat_b)
            print(f"  {count:>3}", end='')
        print()


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/compute_kappa.py <aaron_qrels> <shannon_qrels>")
        print("Example: python3 scripts/compute_kappa.py data/aaron_qrels.txt data/shannon_qrels.txt")
        sys.exit(1)

    path_a = sys.argv[1]
    path_b = sys.argv[2]

    judgments_a = load_qrels(path_a)
    judgments_b = load_qrels(path_b)

    print(f"Annotator A: {len(judgments_a)} judgments from {path_a}")
    print(f"Annotator B: {len(judgments_b)} judgments from {path_b}")

    result = compute_kappa(judgments_a, judgments_b)
    if result is None:
        sys.exit(1)

    kappa, po, pe, n, overlap_keys, labels_a, labels_b = result

    # Show per-query overlap counts
    overlap_queries = sorted(set(k[0] for k in overlap_keys))
    print(f"\nOverlap queries: {overlap_queries}")
    print(f"Total overlapping judgments: {n}")

    for qid in overlap_queries:
        count = sum(1 for k in overlap_keys if k[0] == qid)
        agrees = sum(1 for k in sorted(overlap_keys) if k[0] == qid
                     and judgments_a[k] == judgments_b[k])
        print(f"  {qid}: {count} docs, {agrees} agreements ({agrees/count*100:.0f}%)")

    categories = sorted(set(labels_a + labels_b))
    print_confusion_matrix(labels_a, labels_b, categories)

    print(f"\nObserved agreement (Po): {po:.4f}")
    print(f"Expected agreement (Pe): {pe:.4f}")
    print(f"Cohen's kappa (k):       {kappa:.4f}")

    if kappa < 0:
        interp = "less than chance"
    elif kappa < 0.21:
        interp = "slight"
    elif kappa < 0.41:
        interp = "fair"
    elif kappa < 0.61:
        interp = "moderate"
    elif kappa < 0.81:
        interp = "substantial"
    else:
        interp = "almost perfect"

    print(f"Interpretation: {interp} agreement")
