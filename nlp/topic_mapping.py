import json
from pathlib import Path
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import LdaModel
from gensim.models.phrases import Phrases, Phraser

# -----------------------------
# PATHS
# -----------------------------
INPUT_DIR = Path("data/preprocessed")
OUTPUT_DIR = Path("data/topic_mapped")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# NLTK
# -----------------------------
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)
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
# PREPROCESS
# -----------------------------
def preprocess(sentences):
    texts = []

    for sentence in sentences:
        tokens = word_tokenize(sentence.lower())
        tokens = [
            w for w in tokens
            if w.isalpha() and w not in STOPWORDS and len(w) > 2
        ]

        if tokens:  # 🔥 avoid empty
            texts.append(tokens)

    if not texts:
        return []

    bigram = Phrases(texts, min_count=2, threshold=5)
    bigram_model = Phraser(bigram)

    texts = [bigram_model[text] for text in texts]

    return texts

# -----------------------------
# LDA + MAPPING
# -----------------------------
def map_sentences_to_topics(texts, sentences, num_topics=3):  # 🔥 fixed
    if not texts or len(texts) < 2:
        return []

    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=3, no_above=0.5)

    if len(dictionary) == 0:
        return []

    corpus = [dictionary.doc2bow(text) for text in texts]

    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        passes=15,
        alpha='auto',
        random_state=42
    )

    # Initialize topic structure
    topic_data = {
        i: {"topic_id": i, "words": [], "sentences": []}
        for i in range(num_topics)
    }

    # Add topic words
    for topic_id, words in lda_model.show_topics(num_words=15, formatted=False):
        topic_data[topic_id]["words"] = [w for w, _ in words]

    # Assign sentences (🔥 with threshold)
    for i, bow in enumerate(corpus):
        topic_probs = lda_model.get_document_topics(bow)

        if not topic_probs:
            continue

        best_topic, prob = max(topic_probs, key=lambda x: x[1])

        # 🔥 IMPORTANT FIX: ignore weak assignments
        if prob < 0.5:
            continue

        topic_data[best_topic]["sentences"].append(sentences[i])

    return list(topic_data.values())

# -----------------------------
# PROCESS FILE
# -----------------------------
def process_file(input_path):
    data = load_json(input_path)

    document = data.get("document", input_path.stem)
    sentences = data.get("sentences", [])

    if not sentences:
        print(f"⚠️ Skipped (no sentences): {input_path.name}")
        return

    texts = preprocess(sentences)

    if not texts:
        print(f"⚠️ Skipped (empty after preprocessing): {input_path.name}")
        return

    topic_mapped = map_sentences_to_topics(texts, sentences)

    output_data = {
        "document": document,
        "topics": topic_mapped
    }

    output_file = OUTPUT_DIR / f"{input_path.stem}_mapped.json"
    save_json(output_data, output_file)

    print(f"✅ {input_path.name} → {output_file.name}")

# -----------------------------
# MAIN
# -----------------------------
def main():
    files = list(INPUT_DIR.glob("*.json"))

    if not files:
        print("❌ No files found")
        return

    for f in files:
        process_file(f)

    print("\n✅ Topic mapping completed")


if __name__ == "__main__":
    main()