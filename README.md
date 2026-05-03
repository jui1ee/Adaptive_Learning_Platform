# Interpretable Adaptive Quiz Generation with NLP + Deep Knowledge Tracing

An interpretable document-to-quiz pipeline that generates personalized assessments from uploaded PDFs while maintaining transparency in content flow and adaptive learning.

## Motivation
Most LLM-based quiz generators behave as black boxes, making it difficult to trace how source content influences generated questions.

This project addresses that by combining:
- **Interpretable NLP preprocessing and topic modeling**
- **Constrained LLM-based summarization and quiz generation**
- **Deep Knowledge Tracing (DKT)** for adaptive learning reinforcement

The goal is to ensure that generated quizzes remain grounded in uploaded document content while dynamically adapting to user mastery.

---

## Pipeline Overview

### 1. Document Processing
- PDF upload and text extraction using **PyPlumber**
- Text preprocessing:
  - cleaning
  - tokenization
  - lemmatization
  - soft stopword removal

### 2. Topic Discovery
- Topic modeling using **Latent Dirichlet Allocation (LDA)**
- Keyword extraction using:
  - **TF-IDF**
  - **RAKE**

### 3. Topic Grounding
- Sentences are mapped to extracted topics
- Structured JSON is created containing:
  - topic IDs
  - topic keywords
  - topic-specific sentences

This ensures downstream generation is traceable.

### 4. Controlled LLM Quiz Generation
- Topic JSON is passed to Groq LLM
- LLM generates:
  - topic-wise summaries
  - quiz questions

Constraint: generation is restricted to topic sentences only, reducing hallucination and drift from source content.

### 5. Adaptive Learning with DKT
- User quiz responses are passed to an **LSTM-based Deep Knowledge Tracing model**
- Model predicts mastery probability for each topic

Topics are classified into:
- Weak
- Medium
- Strong

### 6. Reinforcement Loop
- New quizzes are generated only for:
  - weak topics
  - medium topics

This creates a personalized revision loop.

---

## Repository Structure

```bash
.
├── dkt/
│   ├── inference.py
│   ├── llm_bridge.py
│   ├── main.py
│   ├── model.py
│   ├── quiz_engine.py
│   ├── train.py
│
├── nlp/
│   ├── extraction.py
│   ├── keyword_extraction.py
│   ├── preprocessing.py
│   ├── summarization.py
│   ├── topic_mapping.py
│   └── topic_modeling.py
│
├── data/raw/
├── app.py
├── download_nltk.py
└── requirements.txt
```

---

## Results
Tested on engineering PDFs across:
- NLP
- Deep Learning
- Operating Systems
- Computer Networks

Achieved:
- **Topic Coherence Score: 0.55**

---

## Tech Stack
- Python
- PyTorch
- PyPlumber
- NLTK
- Scikit-learn
- LDA
- TF-IDF
- RAKE
- Groq API
- Streamlit / Flask

---

## Future Work
- Replace LDA with BERTopic or embedding-based topic modeling
- Add richer learning analytics dashboard
- Improve DKT personalization with attention-based architectures
- Support multi-document curriculum generation
