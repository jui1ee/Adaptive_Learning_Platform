import re
import json
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from typing import List
from pathlib import Path

# -----------------------------
# NLTK SETUP
# -----------------------------
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

STOPWORDS = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# -----------------------------
# CLEAN TEXT
# -----------------------------
def clean_text(text: str) -> str:
    text = text.lower()

    # Remove URLs & emails
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)

    # Remove lecture artifacts (IMPORTANT)
    text = re.sub(r'refer slide time', '', text)
    text = re.sub(r'lecture \d+|chapter \d+', '', text)

    # Remove timestamps and standalone numbers
    text = re.sub(r'\b\d{1,4}\b', '', text)

    # Remove single-letter noise like "a.", "b."
    text = re.sub(r'\b[a-z]\.\b', '', text)

    # Keep useful punctuation
    text = re.sub(r'[^\w\s\.\?\!\-]', '', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# -----------------------------
# LEMMATIZATION
# -----------------------------
def lemmatize_sentence(sentence: str) -> str:
    tokens = word_tokenize(sentence)
    lemmas = [lemmatizer.lemmatize(w) for w in tokens]
    return ' '.join(lemmas)

# -----------------------------
# SENTENCE TOKENIZATION + FILTERING
# -----------------------------
def tokenize_sentences(text: str) -> List[str]:
    sentences = sent_tokenize(text)
    clean_sentences = []

    for s in sentences:
        s = s.strip()

        # Skip very short sentences
        if len(s.split()) < 6:
            continue

        # Skip too long sentences (often noisy)
        if len(s.split()) > 40:
            continue

        # Remove numeric-heavy sentences
        digit_ratio = sum(c.isdigit() for c in s) / max(len(s), 1)
        if digit_ratio > 0.3:
            continue

        # Remove low alphabetic content
        alpha_ratio = len(re.findall(r'[a-zA-Z]', s)) / max(len(s), 1)
        if alpha_ratio < 0.6:
            continue

        # Apply lemmatization
        s = lemmatize_sentence(s)

        clean_sentences.append(s)

    return clean_sentences

# -----------------------------
# STOPWORD REMOVAL (OPTIONAL)
# -----------------------------
def remove_stopwords(text: str) -> str:
    tokens = text.split()
    filtered = [w for w in tokens if w not in STOPWORDS]
    return ' '.join(filtered)

# -----------------------------
# MAIN PIPELINE
# -----------------------------
def preprocess_pipeline(text: str, remove_stops: bool = False) -> dict:
    
    # Step 1: Clean raw text
    cleaned = clean_text(text)

    # Step 2: Sentence splitting + filtering + lemmatization
    sentences = tokenize_sentences(cleaned)

    # Step 3: Optional stopword removal
    if remove_stops:
        sentences = [remove_stopwords(s) for s in sentences]

    return {
        "cleaned_text": cleaned,
        "sentences": sentences
    }

# -----------------------------
# FILE PROCESSING
# -----------------------------
def process_file(input_file: str, output_dir: str, remove_stops: bool = False):
    input_path = Path(input_file)
    doc_name = input_path.stem

    # Read file
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()

    # Process
    result = preprocess_pipeline(text, remove_stops=remove_stops)

    # Ensure output directory exists
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save cleaned text
    cleaned_file = output_path / f"{doc_name}_cleaned.txt"
    with open(cleaned_file, 'w', encoding='utf-8') as f:
        f.write(result["cleaned_text"])

    # Save sentences
    sentences_file = output_path / f"{doc_name}_sentences.txt"
    with open(sentences_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result["sentences"]))

    # Save JSON
    json_file = output_path / f"{doc_name}.json"

    data = {
        "document": doc_name,
        "num_sentences": len(result["sentences"]),
        "cleaned_text": result["cleaned_text"],
        "sentences": result["sentences"]
    }

    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    # Logs
    print(f"\n✓ Processed: {doc_name}")
    print(f"  → Sentences kept: {len(result['sentences'])}")
    print(f"  → Cleaned TXT: {cleaned_file}")
    print(f"  → JSON: {json_file}")

# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    print("🔹 Running preprocessing on extracted files...")

    input_dir = Path("data/extracted")
    output_dir = "data/preprocessed"

    for file in input_dir.glob("*.txt"):
        process_file(
            input_file=str(file),
            output_dir=output_dir,
            remove_stops=False  # KEEP FALSE for LDA
        )

    print("\n✅ All files processed successfully!")






