import json
import re
from pathlib import Path
from rake_nltk import Rake
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords

# -----------------------------
# PATHS
# -----------------------------
INPUT_DIR = Path("data/topic_mapped")
OUTPUT_DIR = Path("data/keywords")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STOPWORDS = set(stopwords.words('english'))

# -----------------------------
# LOAD / SAVE
# -----------------------------
def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# -----------------------------
# RAKE
# -----------------------------
def get_rake_keywords(text):
    rake = Rake(stopwords=STOPWORDS)
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()[:15]

# -----------------------------
# TF-IDF
# -----------------------------
def get_tfidf_keywords(sentences):
    if len(sentences) < 2:
        return []

    vectorizer = TfidfVectorizer(
        stop_words='english',
        max_features=20,
        ngram_range=(1, 2)
    )

    X = vectorizer.fit_transform(sentences)
    return list(vectorizer.get_feature_names_out())

# -----------------------------
# MERGE
# -----------------------------
def merge_keywords(rake_kw, tfidf_kw):
    return list(set([kw.lower() for kw in rake_kw + tfidf_kw]))

# -----------------------------
# CLEAN KEYWORDS (IMPROVED)
# -----------------------------
def clean_keywords(keywords):
    cleaned = set()

    bad_words = {
        "one", "two", "use", "used", "using", "make", "does",
        "need", "needs", "know", "also", "called", "given",
        "example", "result", "system", "different", "ways"
    }

    for kw in keywords:
        kw = kw.lower().strip()

        words = kw.split()

        # keep only 1–3 words
        if not (1 <= len(words) <= 3):
            continue

        # remove numbers
        if re.search(r"\d", kw):
            continue

        # remove phrases with all bad words
        if all(w in bad_words for w in words):
            continue

        # remove very short
        if len(kw) < 3:
            continue

        # basic normalization (plural → singular)
        if kw.endswith("s") and len(words) == 1:
            kw = kw[:-1]

        cleaned.add(kw)

    return sorted(cleaned)

# -----------------------------
# PROCESS FILE
# -----------------------------
def process_file(input_path):
    data = load_json(input_path)

    document = data["document"]
    topics = data["topics"]

    for topic in topics:
        sentences = topic.get("sentences", [])

        if not sentences:
            topic["keywords"] = []
            continue

        full_text = " ".join(sentences)

        rake_kw = get_rake_keywords(full_text)
        tfidf_kw = get_tfidf_keywords(sentences)

        merged = merge_keywords(rake_kw, tfidf_kw)

        final_keywords = clean_keywords(merged)

        topic["keywords"] = final_keywords

    output_data = {
        "document": document,
        "topics": topics
    }

    output_file = OUTPUT_DIR / f"{input_path.stem}_keywords.json"
    save_json(output_data, output_file)

    print(f"✅ {input_path.name} → {output_file.name}")

# -----------------------------
# MAIN
# -----------------------------
def main():
    files = list(INPUT_DIR.glob("*.json"))

    if not files:
        print("❌ No topic_mapped files found")
        return

    for f in files:
        process_file(f)

    print("\n✅ Keyword extraction completed")


if __name__ == "__main__":
    main()