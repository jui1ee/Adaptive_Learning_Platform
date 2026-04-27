# import json
# from pathlib import Path
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from gensim import corpora
# from gensim.models import LdaModel
# from gensim.models.phrases import Phrases, Phraser

# # -----------------------------
# # SET PATHS
# # -----------------------------
# INPUT_DIR = Path("data/preprocessed")
# OUTPUT_DIR = Path("data/topics")

# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# # -----------------------------
# # NLTK SETUP
# # -----------------------------
# nltk.download('punkt', quiet=True)
# nltk.download('stopwords', quiet=True)

# STOPWORDS = set(stopwords.words('english'))


# # -----------------------------
# # LOAD JSON
# # -----------------------------
# def load_json(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         return json.load(f)


# # -----------------------------
# # SAVE JSON
# # -----------------------------
# def save_json(data, file_path):
#     with open(file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=4)


# # -----------------------------
# # PREPROCESS
# # -----------------------------
# def preprocess(sentences):
#     texts = []

#     for sentence in sentences:
#         tokens = word_tokenize(sentence.lower())
#         tokens = [
#             w for w in tokens
#             if w.isalpha() and w not in STOPWORDS and len(w) > 2
#         ]

#         if tokens:  # 🔥 avoid empty entries
#             texts.append(tokens)

#     if not texts:
#         return []

#     # Bigrams (slightly relaxed threshold)
#     bigram = Phrases(texts, min_count=2, threshold=5)
#     bigram_model = Phraser(bigram)

#     texts = [bigram_model[text] for text in texts]

#     return texts


# # -----------------------------
# # LDA
# # -----------------------------
# def run_lda(texts, num_topics=3):  # 🔥 reduced topics
#     if not texts or len(texts) < 2:
#         return None

#     dictionary = corpora.Dictionary(texts)

#     # 🔥 better filtering
#     dictionary.filter_extremes(no_below=3, no_above=0.5)

#     if len(dictionary) == 0:
#         return None

#     corpus = [dictionary.doc2bow(text) for text in texts]

#     lda_model = LdaModel(
#         corpus=corpus,
#         id2word=dictionary,
#         num_topics=num_topics,
#         passes=15,
#         alpha='auto',
#         random_state=42
#     )

#     return lda_model


# # -----------------------------
# # EXTRACT TOPICS
# # -----------------------------
# def extract_topics(lda_model):
#     if lda_model is None:
#         return []

#     topics = []

#     for topic_id, words in lda_model.show_topics(num_words=15, formatted=False):  # 🔥 more words
#         topic_words = [word for word, _ in words]

#         topics.append({
#             "topic_id": topic_id,
#             "words": topic_words
#         })

#     return topics


# # -----------------------------
# # PROCESS FILE
# # -----------------------------
# def process_file(input_path):
#     data = load_json(input_path)

#     document = data.get("document", input_path.stem)
#     sentences = data.get("sentences", [])

#     if not sentences:
#         print(f"⚠️ Skipped (no sentences): {input_path.name}")
#         return

#     texts = preprocess(sentences)

#     if not texts:
#         print(f"⚠️ Skipped (empty after preprocessing): {input_path.name}")
#         return

#     lda_model = run_lda(texts)
#     topics = extract_topics(lda_model)

#     output_data = {
#         "document": document,
#         "topics": topics
#     }

#     output_file = OUTPUT_DIR / f"{input_path.stem}_topics.json"
#     save_json(output_data, output_file)

#     print(f"✅ Processed: {input_path.name} → {output_file.name}")


# # -----------------------------
# # MAIN
# # -----------------------------
# def main():
#     json_files = list(INPUT_DIR.glob("*.json"))

#     if not json_files:
#         print("❌ No JSON files found in data/preprocessed/")
#         return

#     for file_path in json_files:
#         process_file(file_path)

#     print("\n✅ All files processed successfully.")


# if __name__ == "__main__":
#     main()









#COHORENCE SCORE CODE
import json
from pathlib import Path
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from gensim.models.phrases import Phrases, Phraser

# -----------------------------
# SET PATHS
# -----------------------------
INPUT_DIR = Path("data/preprocessed")
OUTPUT_DIR = Path("data/topics")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# NLTK SETUP
# -----------------------------
nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

STOPWORDS = set(stopwords.words('english'))

# -----------------------------
# LOAD JSON
# -----------------------------
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# -----------------------------
# SAVE JSON
# -----------------------------
def save_json(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
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

        if tokens:
            texts.append(tokens)

    if not texts:
        return []

    # Bigrams
    bigram = Phrases(texts, min_count=2, threshold=5)
    bigram_model = Phraser(bigram)
    texts = [bigram_model[text] for text in texts]

    return texts

# -----------------------------
# RUN LDA + COHERENCE
# -----------------------------
def run_lda(texts, num_topics=5):
    if not texts or len(texts) < 2:
        return None, None, None, None

    dictionary = corpora.Dictionary(texts)

    dictionary.filter_extremes(no_below=3, no_above=0.5)

    if len(dictionary) == 0:
        return None, None, None, None

    corpus = [dictionary.doc2bow(text) for text in texts]

    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        passes=15,
        alpha='auto',
        random_state=42
    )

    # 🔥 Coherence Score
    coherence_model = CoherenceModel(
        model=lda_model,
        texts=texts,
        dictionary=dictionary,
        coherence='c_v'
    )

    coherence_score = coherence_model.get_coherence()

    return lda_model, dictionary, corpus, coherence_score

# -----------------------------
# EXTRACT TOPICS
# -----------------------------
def extract_topics(lda_model):
    if lda_model is None:
        return []

    topics = []

    for topic_id, words in lda_model.show_topics(num_words=15, formatted=False):
        topic_words = [word for word, _ in words]

        topics.append({
            "topic_id": topic_id,
            "words": topic_words
        })

    return topics

# -----------------------------
# OPTIONAL: FIND BEST TOPIC NUMBER 🔥
# -----------------------------
def find_best_topic_count(texts):
    topic_range = [3, 5, 8]
    best_score = 0
    best_k = 3

    print("\n🔍 Finding best number of topics...")

    for k in topic_range:
        lda_model, dictionary, corpus, score = run_lda(texts, num_topics=k)

        if score:
            print(f"Topics: {k} → Coherence: {score:.4f}")

            if score > best_score:
                best_score = score
                best_k = k

    print(f"\n✅ Best Topic Count: {best_k} (Score: {best_score:.4f})\n")

    return best_k, best_score

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

    # 🔥 Find best number of topics
    best_k, best_score = find_best_topic_count(texts)

    # Run final LDA with best_k
    lda_model, dictionary, corpus, coherence_score = run_lda(texts, num_topics=best_k)

    if lda_model is None:
        print(f"⚠️ LDA failed: {input_path.name}")
        return

    topics = extract_topics(lda_model)

    # Save output
    output_data = {
        "document": document,
        "num_topics": best_k,
        "coherence_score": round(coherence_score, 4),
        "topics": topics
    }

    output_file = OUTPUT_DIR / f"{input_path.stem}_topics.json"
    save_json(output_data, output_file)

    print(f"✅ Processed: {input_path.name}")
    print(f"   → Topics: {best_k}")
    print(f"   → Coherence Score: {coherence_score:.4f}")
    print(f"   → Output: {output_file.name}")

# -----------------------------
# MAIN
# -----------------------------
def main():
    json_files = list(INPUT_DIR.glob("*.json"))

    if not json_files:
        print("❌ No JSON files found in data/preprocessed/")
        return

    for file_path in json_files:
        process_file(file_path)

    print("\n✅ All files processed successfully.")

if __name__ == "__main__":
    main()










#WITHOUT COHORENCE SCORE CODE
# import json
# from pathlib import Path
# import nltk
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords
# from gensim import corpora
# from gensim.models import LdaModel
# from gensim.models.phrases import Phrases, Phraser

# # -----------------------------
# # SET PATHS
# # -----------------------------
# INPUT_DIR = Path("data/preprocessed")
# OUTPUT_DIR = Path("data/topics")

# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# # -----------------------------
# # NLTK SETUP
# # -----------------------------
# nltk.download('punkt', quiet=True)
# nltk.download('stopwords', quiet=True)

# STOPWORDS = set(stopwords.words('english'))

# # -----------------------------
# # LOAD JSON
# # -----------------------------
# def load_json(file_path):
#     with open(file_path, 'r', encoding='utf-8') as f:
#         return json.load(f)

# # -----------------------------
# # SAVE JSON
# # -----------------------------
# def save_json(data, file_path):
#     with open(file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=4)

# # -----------------------------
# # PREPROCESS
# # -----------------------------
# def preprocess(sentences):
#     texts = []

#     for sentence in sentences:
#         tokens = word_tokenize(sentence.lower())
#         tokens = [
#             w for w in tokens
#             if w.isalpha() and w not in STOPWORDS and len(w) > 2
#         ]

#         if tokens:
#             texts.append(tokens)

#     if not texts:
#         return []

#     # Bigrams
#     bigram = Phrases(texts, min_count=2, threshold=5)
#     bigram_model = Phraser(bigram)
#     texts = [bigram_model[text] for text in texts]

#     return texts

# # -----------------------------
# # RUN LDA (NO COHERENCE)
# # -----------------------------
# def run_lda(texts, num_topics=3):
#     if not texts or len(texts) < 2:
#         return None

#     dictionary = corpora.Dictionary(texts)
#     dictionary.filter_extremes(no_below=2, no_above=0.6)

#     if len(dictionary) == 0:
#         return None

#     corpus = [dictionary.doc2bow(text) for text in texts]

#     lda_model = LdaModel(
#         corpus=corpus,
#         id2word=dictionary,
#         num_topics=num_topics,
#         passes=8,  # 🔥 reduced for speed
#         alpha='auto',
#         random_state=42
#     )

#     return lda_model

# # -----------------------------
# # EXTRACT TOPICS
# # -----------------------------
# def extract_topics(lda_model):
#     if lda_model is None:
#         return []

#     topics = []

#     for topic_id, words in lda_model.show_topics(num_words=10, formatted=False):
#         topic_words = [word for word, _ in words]

#         topics.append({
#             "topic_id": topic_id,
#             "words": topic_words
#         })

#     return topics

# # -----------------------------
# # PROCESS FILE
# # -----------------------------
# def process_file(input_path):
#     data = load_json(input_path)

#     document = data.get("document", input_path.stem)
#     sentences = data.get("sentences", [])

#     if not sentences:
#         print(f"⚠️ Skipped (no sentences): {input_path.name}")
#         return

#     texts = preprocess(sentences)

#     if not texts:
#         print(f"⚠️ Skipped (empty after preprocessing): {input_path.name}")
#         return

#     # 🔥 Fixed number of topics (fast)
#     lda_model = run_lda(texts, num_topics=3)

#     if lda_model is None:
#         print(f"⚠️ LDA failed: {input_path.name}")
#         return

#     topics = extract_topics(lda_model)

#     # Save output
#     output_data = {
#         "document": document,
#         "num_topics": 3,
#         "topics": topics
#     }

#     output_file = OUTPUT_DIR / f"{input_path.stem}_topics.json"
#     save_json(output_data, output_file)

#     print(f"✅ Processed: {input_path.name}")
#     print(f"   → Topics: 3")
#     print(f"   → Output: {output_file.name}")

# # -----------------------------
# # MAIN
# # -----------------------------
# def main():
#     json_files = list(INPUT_DIR.glob("*.json"))

#     if not json_files:
#         print("❌ No JSON files found in data/preprocessed/")
#         return

#     for file_path in json_files:
#         process_file(file_path)

#     print("\n✅ All files processed successfully.")

# if __name__ == "__main__":
#     main()