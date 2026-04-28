# # nlp/summarization.py

# import requests
# import json
# import os

# API_KEY = "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"   # 🔴 replace this

# URL = "https://openrouter.ai/api/v1/chat/completions"

# def call_llm(prompt):
#     headers = {
#         "Authorization": f"Bearer {API_KEY}",
#         "Content-Type": "application/json"
#     }

#     data = {
#         "model": "openai/gpt-4o-mini",  # fast + cheap
#         "messages": [
#             {"role": "user", "content": prompt}
#         ]
#     }

#     response = requests.post(URL, headers=headers, json=data)

#     try:
#         return response.json()["choices"][0]["message"]["content"]
#     except:
#         print("Error in API response:", response.text)
#         return None
    
# def create_prompt(keywords, sentences):
#     return f"""
# You are an educational AI assistant.

# Keywords: {keywords}
# Sentences: {sentences}

# Tasks:
# 1. Generate a clear summary (5-6 lines)
# 2. Generate 3 MCQs with 4 options and correct answer

# Output ONLY in JSON format:
# {{
#   "summary": "...",
#   "quiz": [
#     {{
#       "question": "...",
#       "options": ["A", "B", "C", "D"],
#       "answer": "..."
#     }}
#   ]
# }}
# """

# def process_topic(topic):
#     topic_id = topic["topic_id"]
#     keywords = topic["keywords"][:15]       # limit size
#     sentences = topic["sentences"][:5]      # limit size

#     prompt = create_prompt(keywords, sentences)

#     result = call_llm(prompt)

#     if result is None:
#         return None

#     try:
#         parsed = json.loads(result)
#     except:
#         print(f"JSON parsing failed for topic {topic_id}")
#         return None

#     return {
#         "topic_id": topic_id,
#         "summary": parsed.get("summary", ""),
#         "quiz": parsed.get("quiz", [])
#     }

# def process_file(input_path, output_path):
#     with open(input_path, "r") as f:
#         data = json.load(f)

#     final_output = {
#         "document": data["document"],
#         "results": []
#     }

#     for topic in data["topics"]:
#         print(f"Processing topic {topic['topic_id']}...")

#         result = process_topic(topic)

#         if result:
#             final_output["results"].append(result)

#     # save output
#     with open(output_path, "w") as f:
#         json.dump(final_output, f, indent=4)

#     print("✅ Output saved to:", output_path)


# if __name__ == "__main__":
#     input_file = "data/keywords/sample1_mapped_keywords.json"
#     output_file = "data/summary/sample1_output.json"

#     process_file(input_file, output_file)



#OPEN ROUTER API
# import requests
# import json
# import os
# from pathlib import Path
# import time

# # =============================
# # CONFIG
# # =============================
# API_KEY = "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"   
# URL = "https://openrouter.ai/api/v1/chat/completions"

# INPUT_DIR = "data/keywords"
# OUTPUT_DIR = "data/summary"

# os.makedirs(OUTPUT_DIR, exist_ok=True)


# # =============================
# # LLM CALL
# # =============================
# def call_llm(prompt, retries=3):
#     import time

#     for attempt in range(retries):
#         time.sleep(6)

#         response = requests.post(URL, headers={
#             "Authorization": f"Bearer {API_KEY}",
#             "Content-Type": "application/json"
#         }, json={
#             "model": "meta-llama/llama-3.2-3b-instruct:free",
#             "messages": [{"role": "user", "content": prompt}],
#             "temperature": 0
#         })

#         res_json = response.json()

#         if "choices" in res_json:
#             return res_json["choices"][0]["message"]["content"]

#         print(f"Retry {attempt+1}:", res_json)
#         time.sleep(5)

#     return None

# # =============================
# # PROMPTS
# # =============================

# # 🔹 Combined Summary Prompt
# def create_summary_prompt(all_keywords, all_sentences):
#     return f"""
# You are an educational AI assistant.

# Keywords: {all_keywords}
# Sentences: {all_sentences}

# Task:
# Generate a single combined summary (8-10 lines) covering all topics.

# Return ONLY JSON:
# {{
#   "summary": "..."
# }}
# """


# # 🔹 Quiz Prompt (Topic-wise)
# def create_quiz_prompt(keywords, sentences):
#     return f"""
# You are an educational AI assistant.

# Keywords: {keywords}
# Sentences: {sentences}

# Task:
# Generate 5 MCQ questions with 4 options and correct answer.

# Return ONLY JSON:
# {{
#   "quiz": [
#     {{
#       "question": "...",
#       "options": ["A", "B", "C", "D"],
#       "answer": "..."
#     }}
#   ]
# }}
# """


# # =============================
# # MAIN PROCESS FUNCTION
# # =============================
# def process_file(input_path):
#     with open(input_path, "r") as f:
#         data = json.load(f)

#     document_name = data["document"]

#     # =============================
#     # 🔥 STEP 1: COMBINE ALL DATA
#     # =============================
#     all_keywords = []
#     all_sentences = []

#     for topic in data["topics"]:
#         all_keywords.extend(topic["keywords"][:10])
#         all_sentences.extend(topic["sentences"][:3])

#     # =============================
#     # 🔥 STEP 2: GENERATE ONE SUMMARY
#     # =============================
#     summary_prompt = create_summary_prompt(all_keywords, all_sentences)
#     summary_result = call_llm(summary_prompt)

#     try:
#         summary_json = json.loads(summary_result)
#         final_summary = summary_json.get("summary", "")
#     except:
#         print("Summary parsing failed")
#         final_summary = ""

#     # =============================
#     # 🔥 STEP 3: QUIZ PER TOPIC
#     # =============================
#     results = []

#     for topic in data["topics"]:
#         topic_id = topic["topic_id"]

#         quiz_prompt = create_quiz_prompt(
#             topic["keywords"][:10],
#             topic["sentences"][:5]
#         )

#         quiz_result = call_llm(quiz_prompt)

#         try:
#             quiz_json = json.loads(quiz_result)
#             quiz = quiz_json.get("quiz", [])
#         except:
#             print(f"Quiz parsing failed for topic {topic_id}")
#             quiz = []

#         results.append({
#             "topic_id": topic_id,
#             "quiz": quiz
#         })

#     # =============================
#     # SAVE OUTPUT
#     # =============================
#     final_output = {
#         "document": document_name,
#         "summary": final_summary,
#         "results": results
#     }

#     output_path = os.path.join(OUTPUT_DIR, f"{document_name}_output.json")

#     with open(output_path, "w") as f:
#         json.dump(final_output, f, indent=4)

#     print(f"✅ Done: {output_path}")


# # =============================
# # RUN FOR ALL FILES
# # =============================
# def process_all_files():
#     files = Path(INPUT_DIR).glob("*.json")

#     for file in files:
#         print(f"\nProcessing: {file}")
#         process_file(file)


# # =============================
# # ENTRY POINT
# # =============================
# if __name__ == "__main__":
#     process_all_files()



#GROQ API

import json
import os
from pathlib import Path
from groq import Groq

# =============================
# CONFIG
# =============================
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

INPUT_DIR = "data/keywords"
OUTPUT_DIR = "data/summary"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize client
client = Groq(api_key=API_KEY)

# =============================
# LLM CALL
# =============================
def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0  # ✅ consistency
        )

        return response.choices[0].message.content

    except Exception as e:
        print("API Error:", e)
        return None


# =============================
# PROMPTS
# =============================

def create_summary_prompt(all_keywords, all_sentences):
    return f"""
You are an expert educational assistant.

Keywords: {all_keywords}
Sentences: {all_sentences}

Task:
Write a clear, well-structured paragraph summary (6-8 lines).

Rules:
- Do NOT return keywords or dictionary
- Write like a textbook explanation
- Cover key concepts logically
- Keep it concise and coherent

Output ONLY JSON:
{{
  "summary": "your paragraph summary here"
}}
"""


def create_quiz_prompt(keywords, sentences):
    return f"""
You are an expert question setter.

Keywords: {keywords}
Sentences: {sentences}

Task:
Generate 5 MCQs that test understanding (not simple definitions).

Rules:
- Avoid very easy or obvious questions
- Focus on concepts and differences
- All options must be plausible
- Only ONE correct answer
- Answer MUST be one of: A, B, C, D

Output ONLY JSON:
{{
  "quiz": [
    {{
      "question": "...",
      "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
      "answer": "A"
    }}
  ]
}}
"""


# =============================
# MAIN PROCESS FUNCTION
# =============================
def process_file(input_path):
    with open(input_path, "r") as f:
        data = json.load(f)

    document_name = data["document"]

    # Combine all data
    all_keywords = []
    all_sentences = []

    for topic in data["topics"]:
        all_keywords.extend(topic["keywords"][:5])
        all_sentences.extend(topic["sentences"][:2])

    # =============================
    # SUMMARY
    # =============================
    summary_prompt = create_summary_prompt(all_keywords, all_sentences)
    summary_result = call_llm(summary_prompt)

    if summary_result:
        try:
            summary_json = json.loads(summary_result)
            final_summary = summary_json.get("summary", "")
        except:
            print("Summary parsing failed")
            final_summary = summary_result  # fallback
    else:
        final_summary = ""
    # =============================
    # QUIZ
    # =============================
    results = []

    for topic in data["topics"]:
        topic_id = topic["topic_id"]

        quiz_prompt = create_quiz_prompt(
            topic["keywords"][:5],
            topic["sentences"][:2]
        )

        quiz_result = call_llm(quiz_prompt)

        if quiz_result:
            try:
                quiz_json = json.loads(quiz_result)
                quiz = quiz_json.get("quiz", [])
            except:
                print(f"Quiz parsing failed for topic {topic_id}")
                quiz = []
        else:
            quiz = []

        results.append({
            "topic_id": topic_id,
            "quiz": quiz
        })

    # =============================
    # SAVE OUTPUT
    # =============================
    final_output = {
        "document": document_name,
        "summary": final_summary,
        "results": results
    }

    output_path = os.path.join(OUTPUT_DIR, f"{document_name}_output.json")

    with open(output_path, "w") as f:
        json.dump(final_output, f, indent=4)

    print(f"✅ Done: {output_path}")


# =============================
# RUN FOR ALL FILES
# =============================
def process_all_files():
    files = Path(INPUT_DIR).glob("*.json")

    for file in files:
        print(f"\nProcessing: {file}")
        process_file(file)


# =============================
# ENTRY POINT
# =============================
if __name__ == "__main__":
    process_all_files()
