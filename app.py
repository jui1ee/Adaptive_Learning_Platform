# import streamlit as st
# import subprocess
# import sys
# import os

# st.set_page_config(page_title="Adaptive Learning System", layout="wide")
# st.title("📚 Adaptive Learning System")

# # ── Session State ────────────────────────────────────────────────────────────
# for key in [
#     "pdf_uploaded",
#     "extraction_done",
#     "preprocessing_done",
#     "topic_modeling_done",
#     "topic_mapping_done",
#     "keyword_extraction_done",
#     "quiz_generated",
# ]:
#     if key not in st.session_state:
#         st.session_state[key] = False

# # ── Helper ───────────────────────────────────────────────────────────────────
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# def run_script_streaming(script_path, output_placeholder):
#     """Run script and stream output line-by-line into a Streamlit placeholder."""
#     env = os.environ.copy()
#     env["PYTHONIOENCODING"] = "utf-8"
#     env["PYTHONUNBUFFERED"] = "1"   # force line-by-line flushing

#     process = subprocess.Popen(
#         [sys.executable, "-u", script_path],   # -u = unbuffered
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,              # merge stderr into stdout
#         text=True,
#         encoding="utf-8",
#         cwd=BASE_DIR,
#         env=env,
#         stdin=subprocess.DEVNULL,
#     )

#     output_lines = []
#     for line in process.stdout:
#         output_lines.append(line)
#         output_placeholder.text_area(
#             "Live Output",
#             value="".join(output_lines),
#             height=350,
#             key=f"live_{script_path}_{len(output_lines)}",
#         )

#     process.wait()
#     return "".join(output_lines), process.returncode

# # ── Step 1: Upload PDF ───────────────────────────────────────────────────────
# st.header("Step 1 — Upload PDF")

# uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
# if uploaded_file:
#     save_path = os.path.join(BASE_DIR, "data", "raw", uploaded_file.name)
#     with open(save_path, "wb") as f:
#         f.write(uploaded_file.read())
#     st.session_state.pdf_uploaded = True
#     st.success(f"✅ Saved: data/raw/{uploaded_file.name}")

# # ── Steps 2–7: NLP Pipeline ─────────────────────────────────────────────────
# st.divider()
# st.header("Steps 2–7 — NLP Pipeline")

# pipeline = [
#     ("Run Extraction",          "nlp/extraction.py",         "extraction_done",         "pdf_uploaded"),
#     ("Run Preprocessing",       "nlp/preprocessing.py",      "preprocessing_done",      "extraction_done"),
#     ("Run Topic Modeling",      "nlp/topic_modeling.py",     "topic_modeling_done",     "preprocessing_done"),
#     ("Run Topic Mapping",       "nlp/topic_mapping.py",      "topic_mapping_done",      "topic_modeling_done"),
#     ("Run Keyword Extraction",  "nlp/keyword_extraction.py", "keyword_extraction_done", "topic_mapping_done"),
#     ("Generate Summary + Quiz", "nlp/summarization.py",      "quiz_generated",          "keyword_extraction_done"),
# ]

# for label, script, done_key, prereq_key in pipeline:
#     prereq_met = st.session_state[prereq_key]
#     col1, col2 = st.columns([4, 1])
#     with col1:
#         if st.button(label, disabled=not prereq_met, key=f"btn_{done_key}"):
#             out_placeholder = st.empty()
#             with st.spinner(f"Running {label}..."):
#                 full_output, rc = run_script_streaming(script, out_placeholder)
#             if rc == 0:
#                 st.success("✅ Done.")
#                 st.session_state[done_key] = True
#             else:
#                 st.error(f"❌ Script failed with exit code {rc}.")
#     with col2:
#         if st.session_state[done_key]:
#             st.success("Done ✅")

# # ── Step 8: DKT / Quiz ───────────────────────────────────────────────────────
# st.divider()
# st.header("Step 8 — Take Quiz (DKT)")

# if not st.session_state.quiz_generated:
#     st.info("Complete the NLP pipeline first.")
# else:
#     if st.button("▶️ Run DKT / Take Quiz"):
#         out_placeholder = st.empty()
#         with st.spinner("Running dkt/main.py ..."):
#             full_output, rc = run_script_streaming("dkt/main.py", out_placeholder)
#         if rc == 0:
#             st.success("✅ Done.")
#         else:
#             st.error(f"❌ Script failed with exit code {rc}.")










import streamlit as st
import subprocess
import sys
import os
import json
from pathlib import Path

st.set_page_config(page_title="Adaptive Learning System", layout="wide")
st.title("📚 Adaptive Learning System")

# ── Session State ─────────────────────────────────────────
for key in [
    "pdf_uploaded",
    "extraction_done",
    "preprocessing_done",
    "topic_modeling_done",
    "topic_mapping_done",
    "keyword_extraction_done",
    "quiz_generated",
]:
    if key not in st.session_state:
        st.session_state[key] = False

# ── Paths (FIXED: use Path everywhere) ─────────────────────
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
SUMMARY_DIR = BASE_DIR / "data" / "summary"
ATTEMPT_DIR = BASE_DIR / "data" / "attempts"

# ── Helper ────────────────────────────────────────────────
def run_script_streaming(script_path, output_placeholder, is_module=False):
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"

    if is_module:
        cmd = [sys.executable, "-m", script_path]
    else:
        cmd = [sys.executable, "-u", script_path]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        cwd=BASE_DIR,
        env=env,
        stdin=subprocess.DEVNULL,
    )

    output_lines = []
    for line in process.stdout:
        output_lines.append(line)
        output_placeholder.text_area(
            "Live Output",
            value="".join(output_lines),
            height=300,
            key=f"live_{script_path}_{len(output_lines)}",
        )

    process.wait()
    return "".join(output_lines), process.returncode

# ── Step 1: Upload PDF ────────────────────────────────────
st.header("Step 1 — Upload PDF")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])
if uploaded_file:
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    save_path = RAW_DIR / uploaded_file.name

    with open(save_path, "wb") as f:
        f.write(uploaded_file.read())

    st.session_state.pdf_uploaded = True
    st.success(f"✅ Saved: {save_path}")

# ── Pipeline ──────────────────────────────────────────────
st.divider()
st.header("Steps 2–7 — NLP Pipeline")

pipeline = [
    ("Run Extraction",         "nlp/extraction.py",         "extraction_done",         "pdf_uploaded"),
    ("Run Preprocessing",      "nlp/preprocessing.py",      "preprocessing_done",      "extraction_done"),
    ("Run Topic Modeling",     "nlp/topic_modeling.py",     "topic_modeling_done",     "preprocessing_done"),
    ("Run Topic Mapping",      "nlp/topic_mapping.py",      "topic_mapping_done",      "topic_modeling_done"),
    ("Run Keyword Extraction", "nlp/keyword_extraction.py", "keyword_extraction_done", "topic_mapping_done"),
    ("Generate Summary + Quiz","nlp/summarization.py",      "quiz_generated",          "keyword_extraction_done"),
]

for label, script, done_key, prereq_key in pipeline:
    prereq_met = st.session_state[prereq_key]

    col1, col2 = st.columns([4, 1])

    with col1:
        if st.button(label, disabled=not prereq_met, key=f"btn_{done_key}"):
            out_placeholder = st.empty()

            with st.spinner(f"Running {label}..."):
                _, rc = run_script_streaming(script, out_placeholder)

            if rc == 0:
                st.success("✅ Done.")
                st.session_state[done_key] = True
            else:
                st.error(f"❌ Script failed with exit code {rc}.")

    with col2:
        if st.session_state[done_key]:
            st.success("Done ✅")

# ── Step 8: Summary & Quiz ────────────────────────────────
st.divider()
st.header("Step 8 — Summary & Quiz")

if st.session_state.quiz_generated and SUMMARY_DIR.exists():

    files = list(SUMMARY_DIR.glob("*_output.json"))

    if not files:
        st.warning("⚠️ No summary files found.")
        st.stop()

    # ✅ latest_file is now a Path object (FIXED)
    latest_file = max(files, key=lambda f: f.stat().st_mtime)

    with open(latest_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # ── Summary ──
    st.subheader("📄 Summary")
    summary_text = data.get("summary", "")
    st.write(summary_text if summary_text else "⚠️ Summary missing!")

    # ── Quiz ──
    st.subheader("🧠 Quiz")

    for t_idx, topic in enumerate(data.get("results", [])):
        st.markdown(f"### Topic {t_idx + 1}")

        for q_idx, q in enumerate(topic.get("quiz", [])):
            st.write(f"Q{q_idx + 1}: {q['question']}")

            st.radio(
                "Choose answer:",
                q["options"],
                key=f"{t_idx}_{q_idx}"
            )

    # ── Submit ──
    if st.button("Submit Quiz"):

        attempts = []

        for t_idx, topic in enumerate(data.get("results", [])):
            topic_id = topic["topic_id"]

            for q_idx, q in enumerate(topic.get("quiz", [])):
                user = st.session_state.get(f"{t_idx}_{q_idx}")
                correct = q["answer"]

                def extract_option(text):
                    if not text:
                        return ""
                    return text.strip()[0].lower()

                user_opt = extract_option(user)
                correct_opt = extract_option(correct)

                is_correct = user_opt == correct_opt

                attempts.append({
                    "topic_id": topic_id,
                    "is_correct": int(is_correct)
                })

        # ✅ Save attempts (FIXED filename bug)
        ATTEMPT_DIR.mkdir(parents=True, exist_ok=True)

        attempt_path = ATTEMPT_DIR / f"{latest_file.stem}_attempts.json"

        with open(attempt_path, "w") as f:
            json.dump(attempts, f, indent=2)

        st.success(f"✅ Attempts saved: {attempt_path.name}")

        score = sum(a["is_correct"] for a in attempts)
        st.success(f"🎯 Score: {score}/{len(attempts)}")

# ── Step 9: Run DKT ───────────────────────────────────────
st.divider()
st.header("Step 9 — Adaptive Learning (DKT)")

if st.button("▶️ Run DKT"):
    out_placeholder = st.empty()

    with st.spinner("Running DKT model..."):
        _, rc = run_script_streaming("dkt.main", out_placeholder, is_module=True)

    if rc == 0:
        st.success("✅ DKT Completed.")
    else:
        st.error(f"❌ Failed (code {rc})")

# ── Step 10: Adaptive Quiz ────────────────────────────────
st.divider()
st.header("Step 10 — Adaptive Quiz")

adaptive_path = SUMMARY_DIR / "adaptive_quiz.json"

if adaptive_path.exists():

    with open(adaptive_path, "r", encoding="utf-8") as f:
        adaptive_data = json.load(f)

    st.subheader("⚡ Personalized Adaptive Quiz")

    # ✅ Session state for adaptive quiz
    if "adaptive_submitted" not in st.session_state:
        st.session_state.adaptive_submitted = False

    # Store results for saving later
    adaptive_results = []

    for t_idx, topic in enumerate(adaptive_data.get("results", [])):
        st.markdown(f"### Weak Topic {topic['topic_id']}")

        for q_idx, q in enumerate(topic.get("quiz", [])):
            st.write(f"Q{q_idx + 1}: {q['question']}")

            selected = st.radio(
                "Choose answer:",
                q["options"],
                key=f"adaptive_{t_idx}_{q_idx}"
            )

    # ── Submit Button ──
    if st.button("Submit Adaptive Quiz"):
        st.session_state.adaptive_submitted = True

    # ── Evaluation ──
    if st.session_state.adaptive_submitted:

        score = 0
        total = 0

        st.subheader("📊 Results")

        for t_idx, topic in enumerate(adaptive_data.get("results", [])):

            st.markdown(f"### Topic {topic['topic_id']}")

            for q_idx, q in enumerate(topic.get("quiz", [])):

                total += 1

                user = st.session_state.get(f"adaptive_{t_idx}_{q_idx}")
                correct = q["answer"]

                def extract_option(text):
                    if not text:
                        return ""
                    return text.strip()[0].upper()

                user_opt = extract_option(user)
                correct_opt = extract_option(correct)

                is_correct = user_opt == correct_opt

                if is_correct:
                    score += 1

                # Save for file
                adaptive_results.append({
                    "topic_id": topic["topic_id"],
                    "is_correct": int(is_correct)
                })

                # ── Display Question Result ──
                st.markdown("---")
                st.write(f"Q{q_idx + 1}: {q['question']}")

                for opt in q["options"]:
                    opt_letter = opt.strip()[0].upper()

                    if opt_letter == correct_opt:
                        st.markdown(f"✅ **{opt}**")
                    elif opt_letter == user_opt:
                        st.markdown(f"❌ **{opt}**")
                    else:
                        st.markdown(opt)

                # Optional explanation (if added later)
                if "explanation" in q:
                    st.markdown(f"💡 **Explanation:** {q['explanation']}")

        # ── Final Score ──
        st.success(f"🎯 Score: {score}/{total}")

        # ── Save Adaptive Attempts ──
        ATTEMPT_DIR.mkdir(parents=True, exist_ok=True)

        adaptive_attempt_path = ATTEMPT_DIR / "adaptive_attempts.json"

        if adaptive_attempt_path.exists():
            with open(adaptive_attempt_path, "r") as f:
                old = json.load(f)
        else:
            old = []

        old.extend(adaptive_results)

        with open(adaptive_attempt_path, "w") as f:
            json.dump(old, f, indent=2)

        st.success(f"✅ Adaptive attempts saved: {adaptive_attempt_path.name}")

else:
    st.info("⚠️ Run DKT to generate adaptive quiz.")