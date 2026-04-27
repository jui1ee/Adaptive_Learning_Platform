
import json
from pathlib import Path
import re

from .model import DKT
from .train import train_on_attempts
from .inference import predict_mastery, classify
from .llm_bridge import call_llm, generate_adaptive_quiz

# -------------------------
# SAFE JSON PARSER
# -------------------------
def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            return None
    return None

def save_attempts(attempts, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(attempts, f, indent=2)

# -------------------------
# PATH SETUP
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
SUMMARY_DIR = BASE_DIR / "data" / "summary"
ATTEMPT_DIR = BASE_DIR / "data" / "attempts"

# -------------------------
# LOAD ONLY REAL QUIZ FILE (FIXED)
# -------------------------
files = list(SUMMARY_DIR.glob("*_output.json"))   # ✅ FIX

if not files:
    print("❌ No quiz files found in summary folder!")
    exit()

latest_file = max(files, key=lambda f: f.stat().st_mtime)

print(f"\n📂 Using quiz file: {latest_file.name}")

with open(latest_file, encoding="utf-8") as f:
    data = json.load(f)

NUM_SKILLS = len(data.get("results", []))
print(f"\nLoaded Quiz | Skills (Topics): {NUM_SKILLS}")

# -------------------------
# FIX FILENAME MISMATCH (SPACE ISSUE)
# -------------------------
safe_name = latest_file.stem.replace(" ", "_")
attempt_file = ATTEMPT_DIR / f"{safe_name}_attempts.json"

# -------------------------
# LOAD ATTEMPTS (FROM STREAMLIT)
# -------------------------
if not attempt_file.exists():
    print(f"❌ No attempt file found: {attempt_file.name}")
    print("👉 Please take quiz in Streamlit first.")
    exit()

with open(attempt_file, encoding="utf-8") as f:
    all_attempts = json.load(f)

if not all_attempts:
    print("⚠️ No attempts found.")
    exit()

# -------------------------
# INIT MODEL
# -------------------------
model = DKT(NUM_SKILLS)

# -------------------------
# ADAPTIVE LOOP
# -------------------------
print("\n--- ADAPTIVE LEARNING SESSION ---")

for i in range(2):

    print(f"\n========== QUIZ {i+1} ==========")

    # -------------------------
    # FORMAT ATTEMPTS FOR DKT
    # -------------------------
    formatted_attempts = []

    for a in all_attempts:
        skill = int(a["topic_id"])
        result = 1 if a["is_correct"] else 0
        formatted_attempts.append((skill, result))

    # -------------------------
    # TRAIN DKT
    # -------------------------
    model = train_on_attempts(model, formatted_attempts, NUM_SKILLS)

    # -------------------------
    # PREDICT MASTERY
    # -------------------------
    mastery = predict_mastery(model, formatted_attempts, NUM_SKILLS)

    print("\n📊 Topic Mastery Probabilities:\n")
    weak, medium, strong = classify(mastery)

    for topic in range(NUM_SKILLS):
        prob = mastery.get(topic, 0)

        if topic in weak:
            label = "🔴 Weak"
        elif topic in medium:
            label = "🟡 Medium"
        else:
            label = "🟢 Strong"

        print(f"Topic {topic}: {prob:.2f} → {label}")

    print("\nSummary:")
    print("🔴 Weak:", weak)
    print("🟡 Medium:", medium)
    print("🟢 Strong:", strong)

    # -------------------------
    # GENERATE ADAPTIVE QUIZ
    # -------------------------
    if weak:
        print("\n⚡ Generating adaptive quiz from weak topics...")

        prompt = generate_adaptive_quiz(weak, data)

        try:
            response = call_llm(prompt)

            if isinstance(response, dict):
                new_data = response
            else:
                new_data = safe_json_load(response)

            if new_data and "results" in new_data:
                adaptive_data = new_data
                print("✅ Adaptive quiz generated successfully")

                # SAVE adaptive quiz
                adaptive_path = SUMMARY_DIR / "adaptive_quiz.json"

                with open(adaptive_path, "w", encoding="utf-8") as f:
                    json.dump(new_data, f, indent=2)

                print("💾 Adaptive quiz saved")

            else:
                print("⚠️ Invalid LLM response format")

        except Exception as e:
            print("❌ LLM Error:", e)

    else:
        print("\n🎯 No weak topics detected → no adaptation needed")

print("\n✅ Session Complete")
