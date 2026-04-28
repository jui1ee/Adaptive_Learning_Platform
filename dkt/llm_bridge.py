import json
import time
import re
from groq import Groq

import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

def safe_json_load(text):
    try:
        return json.loads(text)

    except:
        try:
            # Extract JSON block if extra text exists
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            return None

    return None

def call_llm(prompt, max_retries=2):

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "Return ONLY valid JSON. No explanation, no extra text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0
            )

            content = response.choices[0].message.content.strip()

            # ✅ Try parsing JSON
            parsed = safe_json_load(content)

            if parsed:
                return parsed

            print(f"⚠️ Invalid JSON (attempt {attempt+1})")

        except Exception as e:
            print(f"❌ API Error (attempt {attempt+1}):", e)

        time.sleep(1)

    print("❌ LLM FAILED AFTER RETRIES")
    return None

def generate_adaptive_quiz(weak_topics, data):

    topic_content = ""

    for topic in data["results"]:
        if topic["topic_id"] in weak_topics:

            # ✅ FIX: fallback to global summary
            topic_text = topic.get("summary")

            if not topic_text:
                topic_text = data.get("summary", "")

            topic_content += f"\nTopic {topic['topic_id']}:\n"
            topic_content += topic_text + "\n"

            print("DEBUG topic_content: ", topic_content)

    return f"""
You are an AI tutor helping a student improve weak topics.

The student is weak in:
{weak_topics}

Below is the ACTUAL STUDY MATERIAL for those topics:

---------------------
{topic_content}
---------------------

Your task:
Generate a NEW quiz STRICTLY based on the above content.

IMPORTANT RULES:
- Use ONLY the provided content (no outside knowledge)
- Questions must be specific to the content
- Avoid generic textbook questions
- Include:
  - 2 conceptual questions
  - 2 application-based questions
  - 1 tricky question
- Each topic must have exactly 5 questions
- Questions should test understanding, not definitions
- Tricky question must involve a common misconception from the content
- Also give a short explanation of the correct option

Return ONLY valid JSON:

{{
  "results": [
    {{
      "topic_id": 0,
      "quiz": [
        {{
          "question": "...",
          "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
          "answer": "A",
          "explanation": "..."
        }}
      ]
    }}
  ]
}}
"""