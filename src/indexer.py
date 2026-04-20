import os
import sys
import json
from collections import defaultdict
from src.preprocessing import process_wiki_line

# Number of chunks in the wiki2022 dataset
NUM_CHUNKS = 32


def get_chunk_filename(chunk_index):
    return f"wiki2022_small.{chunk_index:06d}"


def get_index_filename(chunk_index):
    return f"index{chunk_index:06d}.txt"


# Pass 1: Collect global vocabulary

def collect_vocabulary(data_dir):
    # Scans all chunks to build a sorted global vocabulary.
    # Returns a sorted list of unique stemmed words.
    print("Pass 1: Collecting global vocabulary...")
    vocab = set()

    for chunk_idx in range(NUM_CHUNKS):
        filename = get_chunk_filename(chunk_idx)
        filepath = os.path.join(data_dir, filename)
        print(f"  Reading {filename}...")

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                _, tokens = process_wiki_line(line)
                if tokens:
                    vocab.update(tokens)

    sorted_vocab = sorted(vocab)
    print(f"  Total unique words (excluding stop words): {len(sorted_vocab)}")
    return sorted_vocab


def write_dictionary(sorted_vocab, output_dir):
    # Writes dictionary.txt with one word per line, alphabetically sorted.
    # Line number (0-indexed) is the word-code.
    dict_path = os.path.join(output_dir, 'dictionary.txt')
    print(f"Writing {dict_path}...")
    with open(dict_path, 'w', encoding='utf-8') as f:
        for word in sorted_vocab:
            f.write(word + '\n')
    print(f"  Written {len(sorted_vocab)} words")


def load_dictionary(output_dir):
    # Loads dictionary.txt and returns a word -> code mapping.
    dict_path = os.path.join(output_dir, 'dictionary.txt')
    word_to_code = {}
    with open(dict_path, 'r', encoding='utf-8') as f:
        for code, line in enumerate(f):
            word_to_code[line.strip()] = code
    return word_to_code


# Pass 2: Build per-chunk inverted indexes + document lengths

def build_chunk_indexes(data_dir, output_dir, word_to_code):
    # Reads each chunk, builds a local inverted index per chunk, and
    # collects document lengths (total non-stopword tokens per doc).
    # Returns doc_lengths dict: {doc_id: length}.
    print("Pass 2: Building inverted indexes and computing document lengths...")
    doc_lengths = {}

    for chunk_idx in range(NUM_CHUNKS):
        filename = get_chunk_filename(chunk_idx)
        filepath = os.path.join(data_dir, filename)
        index_filename = get_index_filename(chunk_idx)
        index_path = os.path.join(output_dir, index_filename)
        print(f"  Processing {filename} -> {index_filename}...")

        # inverted_index: word -> { doc_id -> term_frequency }
        inverted_index = defaultdict(lambda: defaultdict(int))

        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                doc_id, tokens = process_wiki_line(line)
                if doc_id is None or tokens is None:
                    continue

                # Document length = total stemmed non-stopword tokens
                doc_lengths[doc_id] = len(tokens)

                for token in tokens:
                    inverted_index[token][doc_id] += 1

        # Write the index file sorted by word-code
        with open(index_path, 'w', encoding='utf-8') as f:
            words_in_chunk = sorted(
                inverted_index.keys(),
                key=lambda w: word_to_code[w]
            )

            for word in words_in_chunk:
                code = word_to_code[word]
                postings = inverted_index[word]
                doc_freq = len(postings)

                postings_str = ' '.join(
                    f"({did}, {tf})"
                    for did, tf in sorted(postings.items(), key=lambda x: int(x[0]))
                )

                f.write(f"{code} {word} {doc_freq} {postings_str}\n")

        print(f"    Words indexed: {len(inverted_index)}")

    return doc_lengths


def write_doc_lengths(doc_lengths, output_dir):
    # Writes document length statistics to doc_lengths.json.
    # Format: {"lengths": {doc_id: length}, "avg_dl": float, "N": int}
    lengths = doc_lengths
    N = len(lengths)
    avg_dl = sum(lengths.values()) / N if N > 0 else 0.0

    stats = {
        "N": N,
        "avg_dl": avg_dl,
        "lengths": lengths
    }

    path = os.path.join(output_dir, 'doc_lengths.json')
    print(f"Writing {path}...")
    print(f"  Total documents: {N}")
    print(f"  Average document length: {avg_dl:.2f}")

    with open(path, 'w', encoding='utf-8') as f:
        json.dump(stats, f)


def load_doc_lengths(output_dir):
    # Loads doc_lengths.json. Returns (lengths_dict, avg_dl, N).
    path = os.path.join(output_dir, 'doc_lengths.json')
    with open(path, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    return stats["lengths"], stats["avg_dl"], stats["N"]


# Merge: Combine per-chunk indexes into a single global index

def merge_indexes(output_dir, word_to_code):
    # Merges the 32 per-chunk index files into a single global_index.txt.
    # Each line: <word-code> <word> <global-df> (<doc-id>, <tf>) ...
    # Postings are sorted by doc-id across all chunks.
    print("Merging 32 chunk indexes into global_index.txt...")

    # global_postings: word -> [(doc_id, tf), ...]
    global_postings = defaultdict(list)

    for chunk_idx in range(NUM_CHUNKS):
        index_filename = get_index_filename(chunk_idx)
        index_path = os.path.join(output_dir, index_filename)

        with open(index_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                # Parse: <code> <word> <df> (<did>, <tf>) (<did>, <tf>) ...
                parts = line.split()
                word = parts[1]

                # Extract all (doc_id, tf) pairs
                postings_raw = line.split('(')[1:]
                for p in postings_raw:
                    p = p.rstrip(') ')
                    did, tf = p.split(',')
                    global_postings[word].append((did.strip(), int(tf.strip())))

    # Write the merged index
    code_to_word = {code: word for word, code in word_to_code.items()}
    global_path = os.path.join(output_dir, 'global_index.txt')

    with open(global_path, 'w', encoding='utf-8') as f:
        for code in sorted(code_to_word.keys()):
            word = code_to_word[code]
            if word not in global_postings:
                continue

            postings = sorted(global_postings[word], key=lambda x: int(x[0]))
            df = len(postings)

            postings_str = ' '.join(f"({did}, {tf})" for did, tf in postings)
            f.write(f"{code} {word} {df} {postings_str}\n")

    print(f"  Written global_index.txt with {len(global_postings)} terms")


# Loading the global index for retrieval

def load_global_index(output_dir):
    # Loads global_index.txt into memory for retrieval.
    # Returns a dict: word -> {"df": int, "postings": [(doc_id, tf), ...]}
    path = os.path.join(output_dir, 'global_index.txt')
    index = {}

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            word = parts[1]
            df = int(parts[2])

            postings = []
            postings_raw = line.split('(')[1:]
            for p in postings_raw:
                p = p.rstrip(') ')
                did, tf = p.split(',')
                postings.append((did.strip(), int(tf.strip())))

            index[word] = {"df": df, "postings": postings}

    return index


# Full indexing pipeline

def build_full_index(data_dir, output_dir='.'):
    # Runs the complete indexing pipeline:
    # 1. Collect vocabulary across all chunks
    # 2. Write dictionary.txt
    # 3. Build per-chunk indexes + compute doc lengths
    # 4. Write doc_lengths.json
    # 5. Merge into global_index.txt

    sorted_vocab = collect_vocabulary(data_dir)
    word_to_code = {word: code for code, word in enumerate(sorted_vocab)}

    write_dictionary(sorted_vocab, output_dir)
    doc_lengths = build_chunk_indexes(data_dir, output_dir, word_to_code)
    write_doc_lengths(doc_lengths, output_dir)
    merge_indexes(output_dir, word_to_code)

    print("\nIndexing complete!")
    print(f"  dictionary.txt: {len(sorted_vocab)} words")
    print(f"  doc_lengths.json: {len(doc_lengths)} documents")
    print(f"  global_index.txt: merged from {NUM_CHUNKS} chunks")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 -m src.indexer <path_to_wiki2022_folder>")
        print("Example: python3 -m src.indexer ./wiki2022_small")
        sys.exit(1)

    data_dir = sys.argv[1]

    if not os.path.isdir(data_dir):
        print(f"Error: Directory not found: {data_dir}")
        sys.exit(1)

    build_full_index(data_dir)
