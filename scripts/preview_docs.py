import sys
import os
import re

# Extracts a preview of each document from the wiki2022 corpus
# Usage: python3 scripts/preview_docs.py <wiki2022_dir> <doc_id1> <doc_id2> ...

def extract_doc_id(url):
    match = re.search(r'curid=(\d+)', url)
    return match.group(1) if match else None

def preview_docs(data_dir, target_ids):
    target_set = set(target_ids)
    found = {}

    for chunk_idx in range(32):
        filename = f"wiki2022_small.{chunk_idx:06d}"
        filepath = os.path.join(data_dir, filename)

        if not os.path.isfile(filepath):
            continue

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(None, 1)
                if len(parts) < 2:
                    continue

                doc_id = extract_doc_id(parts[0])
                if doc_id in target_set:
                    # Clean up the text preview
                    text = parts[1][:300]
                    text = re.sub(r'<[^>]+/?>', ' ', text)
                    text = re.sub(r'https?://\S+', '', text)
                    text = ' '.join(text.split())
                    found[doc_id] = text

                    if len(found) == len(target_set):
                        return found

    return found


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 scripts/preview_docs.py <wiki2022_dir> <doc_id> [doc_id ...]")
        sys.exit(1)

    data_dir = sys.argv[1]
    doc_ids = sys.argv[2:]

    previews = preview_docs(data_dir, doc_ids)

    for doc_id in doc_ids:
        if doc_id in previews:
            print(f"\n[{doc_id}] {previews[doc_id][:200]}...")
        else:
            print(f"\n[{doc_id}] NOT FOUND in corpus")
