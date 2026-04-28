# def run_quiz(data):
#     attempts = []

#     for topic in data["results"]:
#         skill = topic["topic_id"]

#         print(f"\n--- Topic {skill} ---")

#         for q in topic["quiz"]:
#             print("\nQ:", q["question"])

#             labels = ["A", "B", "C", "D"]

#             for i, opt in enumerate(q["options"]):
#                 print(f"{labels[i]}. {opt}")

#             user_ans = input("Your answer: ").strip().upper()

#             correct = 1 if user_ans == q["answer"] else 0

#             # ✅ SHOW CORRECT ANSWER
#             print("✅ Correct Answer:", q["answer"])

#             if correct:
#                 print("🎉 Correct!")
#             else:
#                 print("❌ Wrong!")

#             attempts.append((skill, correct))

#     return attempts

def run_quiz(data, user_answers):
    attempts = []

    for topic in data["results"]:
        skill = topic["topic_id"]

        for i, q in enumerate(topic["quiz"]):
            correct = 1 if user_answers[(skill, i)] == q["answer"] else 0
            attempts.append((skill, correct))

    return attempts