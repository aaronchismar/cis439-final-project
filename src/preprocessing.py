import re
from nltk.stem import PorterStemmer

# Regex patterns for tokenization
URL_PATTERN = re.compile(r'https?://\S+')
MARKUP_PATTERN = re.compile(r'<[^>]+/?>')
WORD_PATTERN = re.compile(r'[a-zA-Z]+')

# Initialize stemmer (module-level singleton for performance)
stemmer = PorterStemmer()

# NLTK English stop words, pre-stemmed for fast lookup
NLTK_STOP_WORDS = [
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you',
    "you're", "you've", "you'll", "you'd", 'your', 'yours', 'yourself',
    'yourselves', 'he', 'him', 'his', 'himself', 'she', "she's", 'her',
    'hers', 'herself', 'it', "it's", 'its', 'itself', 'they', 'them',
    'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom',
    'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are',
    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having',
    'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if',
    'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for',
    'with', 'about', 'against', 'between', 'through', 'during', 'before',
    'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
    'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once',
    'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both', 'each',
    'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
    'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can',
    'will', 'just', 'don', "don't", 'should', "should've", 'now', 'd',
    'll', 'm', 'o', 're', 've', 'y', 'ain', 'aren', "aren't", 'couldn',
    "couldn't", 'didn', "didn't", 'doesn', "doesn't", 'hadn', "hadn't",
    'hasn', "hasn't", 'haven', "haven't", 'isn', "isn't", 'ma', 'mightn',
    "mightn't", 'mustn', "mustn't", 'needn', "needn't", 'shan', "shan't",
    'shouldn', "shouldn't", 'wasn', "wasn't", 'weren', "weren't", 'won',
    "won't", 'wouldn', "wouldn't"
]
STOP_WORDS = set(stemmer.stem(w) for w in NLTK_STOP_WORDS)


def tokenize(text):
    # Strips URLs and markup, extracts alphabetic tokens, lowercases them.
    # Returns a list of raw (unstemmed) lowercase tokens.
    text = URL_PATTERN.sub('', text)
    text = MARKUP_PATTERN.sub(' ', text)
    return [t.lower() for t in WORD_PATTERN.findall(text)]


def stem(token):
    # Stems a single token using Porter stemmer.
    return stemmer.stem(token)


def tokenize_and_stem(text, remove_stopwords=True):
    # Full pipeline: tokenize, stem, optionally remove stop words.
    # Returns a list of stemmed tokens (with duplicates for tf counting).
    tokens = tokenize(text)
    stemmed = [stemmer.stem(t) for t in tokens]
    if remove_stopwords:
        stemmed = [s for s in stemmed if s not in STOP_WORDS]
    return stemmed


def parse_wiki_line(line):
    # Parses a single line from the wiki2022 dataset.
    # Each line is: <wikipedia_url> <page_text>
    # Returns (doc_id, raw_text) or (None, None) if invalid.
    line = line.strip()
    if not line:
        return None, None

    parts = line.split(None, 1)
    if len(parts) < 2:
        return None, None

    url = parts[0]
    text = parts[1]

    # Extract the numeric doc-id (curid) from the Wikipedia URL
    match = re.search(r'curid=(\d+)', url)
    if match:
        return match.group(1), text

    return None, None


def process_wiki_line(line, remove_stopwords=True):
    # Convenience: parses a wiki line and returns (doc_id, stemmed_tokens).
    # Returns (None, None) if the line is invalid.
    doc_id, text = parse_wiki_line(line)
    if doc_id is None:
        return None, None
    tokens = tokenize_and_stem(text, remove_stopwords=remove_stopwords)
    return doc_id, tokens


def process_query(query_text, remove_stopwords=True):
    # Processes a user query through the same pipeline as documents.
    # Returns a list of stemmed tokens.
    return tokenize_and_stem(query_text, remove_stopwords=remove_stopwords)
