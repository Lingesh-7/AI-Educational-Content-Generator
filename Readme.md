# AI Educational Content Generator

## Overview

This project implements a structured, two-agent AI system to generate and evaluate educational content. The system produces grade-appropriate explanations and multiple-choice questions (MCQs), and then validates the output using a reviewer agent. If issues are detected, the system performs a single refinement pass based on structured feedback.

The application is deployed using Streamlit and supports dynamic input for grade level, topic, and number of questions.

**Live Application:**
https://ai-educational-content-generator-lingesh.streamlit.app/

---

## Problem Statement

Generating educational content using LLMs often results in:

* Inconsistent structure
* Incorrect or vague concepts
* Lack of validation

This project addresses these issues by introducing a **dual-agent pipeline** with strict validation and controlled refinement.

---

## System Architecture

The system consists of two independent agents:

### 1. Generator Agent

**Responsibility:**
Generate structured educational content for a given grade and topic.

**Input:**

```json
{
  "grade": 4,
  "topic": "Types of angles",
  "num_questions": 3
}
```

**Output:**

```json
{
  "explanation": "...",
  "mcqs": [
    {
      "question": "...",
      "options": ["A", "B", "C", "D"],
      "answer": "A"
    }
  ]
}
```

**Constraints:**

* Language must match grade level
* Concepts must be factually correct
* Output must follow a strict JSON schema
* Each MCQ must contain exactly four options

---

### 2. Reviewer Agent

**Responsibility:**
Evaluate the generator output based on defined criteria.

**Evaluation Criteria:**

* Age appropriateness
* Conceptual correctness
* Clarity

**Output:**

```json
{
  "status": "pass",
  "feedback": []
}
```

If issues are detected:

```json
{
  "status": "fail",
  "feedback": [
    {
      "issue": "...",
      "fix instruction": "..."
    }
  ]
}
```

---

## Refinement Logic

If the reviewer returns a failure:

* Feedback is transformed into actionable instructions
* Generator is re-invoked with feedback
* Only **one refinement iteration** is allowed

This ensures controlled improvement without infinite loops.

---

## UI Workflow

The Streamlit interface provides a transparent pipeline:

1. User inputs:

   * Grade
   * Topic
   * Number of questions

2. System execution:

   * Content generation
   * Review evaluation
   * Optional refinement

3. Output displayed:

   * Generator output
   * Reviewer feedback
   * Refined output (if applicable)
   * Step-by-step execution status

---

## Tech Stack

* Python
* Streamlit
* LangChain
* ChatGroq (LLM inference)

---

## Installation

### 1. Clone repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Configure environment variables

Create a `.env` file:

```bash
GROQ_API_KEY=your_api_key_here
```

---

### 4. Run application

```bash
streamlit run app.py
```

---

## Requirements

```txt
langchain
langchain-community
langchain-core
langchain-groq
streamlit
```

---

## Example Execution

**Input:**

```json
{
  "grade": 4,
  "topic": "Types of angles",
  "num_questions": 3
}
```

**Output:**

* Structured explanation
* MCQs with valid options and answers
* Reviewer validation
* Refined content if necessary

---

## Key Design Decisions

* Strict JSON enforcement to avoid downstream failures
* Separation of concerns via independent agents
* Controlled refinement (single iteration) to prevent instability
* Validation layer to ensure structural correctness

---

## Limitations

* Dependent on LLM response quality
* No persistent storage or user management
* Limited to single-pass refinement

---

## Future Work

* Multi-pass refinement with scoring
* Adaptive difficulty adjustment
* Content personalization
* API-based deployment
* Logging and monitoring

---

## Author

Lingesh R

---

## License

This project is intended for educational and demonstration purposes.
