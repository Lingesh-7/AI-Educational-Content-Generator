import json
import re
# from langchain_community.llms import Ollama
import os
from langchain_groq import ChatGroq

os.environ["GROQ_API_KEY"]=os.getenv("GROQ_API_KEY")


llm= ChatGroq(model="llama-3.1-8b-instant",temperature=0)
# llm = Ollama(model="llama3.1:8b", temperature=0)# If local host


# -------- SAFE TEXT --------
def get_text(response):
    return response.content if hasattr(response, "content") else str(response)


# -------- JSON EXTRACT --------
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return None


# -------- VALIDATION --------
def validate_generator(data, num_questions):
    if not isinstance(data, dict):
        return False

    if "explanation" not in data or not isinstance(data["explanation"], str):
        return False

    if "mcqs" not in data or len(data["mcqs"]) != num_questions:
        return False

    for q in data["mcqs"]:
        if "question" not in q:
            return False
        if "options" not in q or len(q["options"]) != 4:
            return False
        if q.get("answer") not in ["A", "B", "C", "D"]:
            return False

    return True


def validate_review(data):
    if not isinstance(data, dict):
        return False
    if data.get("status") not in ["pass", "fail"]:
        return False
    if not isinstance(data.get("feedback"), list):
        return False
    return True


# -------- FORMAT FEEDBACK --------
def format_feedback(feedback_list):
    lines = []
    for item in feedback_list:
        if isinstance(item, dict):
            issue = item.get("issue", "")
            fix = item.get("fix instruction", "")
            lines.append(f"{issue} → {fix}")
        else:
            lines.append(str(item))
    return "\n".join(lines)


# -------- GENERATOR AGENT --------
def generator_agent(grade, topic, num_questions, feedback=None):
    prompt = f"""
You are a strict educational content generator.

Grade: {grade}
Topic: {topic}

RULES:
- Use simple language appropriate for the grade
- Generate EXACTLY {num_questions} MCQs
- EACH MCQ must have 4 options
- Ensure all concepts are correct

If feedback is provided:
- You MUST rewrite the explanation
- You MUST modify questions
- DO NOT repeat mistakes

Feedback:
{feedback}

OUTPUT JSON ONLY:
{{
 "explanation": "...",
 "mcqs": [
  {{
   "question": "...",
   "options": ["...", "...", "...", "..."],
   "answer": "A"
  }}
 ]
}}
"""

    response = llm.invoke(prompt)
    raw = get_text(response)

    parsed = extract_json(raw)

    if not parsed or not validate_generator(parsed, num_questions):
        return None

    return parsed


# -------- REVIEWER AGENT --------
def reviewer_agent(content, grade):
    prompt = f"""
You are a strict reviewer.

Grade: {grade}

Check:
- Age appropriateness
- Concept correctness
- Clarity

For EACH issue:
- Give clear fix instruction

Content:
{json.dumps(content)}

OUTPUT JSON ONLY:
{{
 "status": "pass" or "fail",
 "feedback": [
  {{
   "issue": "...",
   "fix instruction": "..."
  }}
 ]
}}
"""

    response = llm.invoke(prompt)
    raw = get_text(response)

    parsed = extract_json(raw)

    if not parsed or not validate_review(parsed):
        return {
            "status": "fail",
            "feedback": ["Reviewer failed to produce valid output"]
        }

    return parsed


# -------- PIPELINE --------
def run_pipeline(grade, topic, num_questions):
    steps = []

    # Step 1: Generate
    steps.append("Generating content...")
    content = None

    for _ in range(2):
        content = generator_agent(grade, topic, num_questions)
        if content:
            break

    if not content:
        return {"error": "Generator failed"}

    # Step 2: Review
    steps.append("Reviewing content...")
    review = reviewer_agent(content, grade)

    refined = None

    # Step 3: Refinement
    if review["status"] == "fail":
        steps.append("Refining content...")

        formatted_feedback = format_feedback(review["feedback"])

        refined = generator_agent(
            grade,
            topic,
            num_questions,
            feedback=formatted_feedback
        )

        if not refined:
            refined = content

    steps.append("Done")

    return {
        "initial": content,
        "review": review,
        "refined": refined,
        "steps": steps
    }