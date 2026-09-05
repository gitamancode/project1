# 🤖 AI Resume Shortlisting System

An AI-powered resume screening and candidate-job matching system that helps recruiters analyze resumes against job requirements using an LLM.

The application extracts structured information from job descriptions and resumes, evaluates the candidate across multiple hiring criteria, and generates a weighted compatibility score with a recruitment recommendation.

## 🚀 Live Demo

👉 https://sortlistyourresume.streamlit.app/

## 📌 Overview

Recruiters often need to review a large number of resumes for a single job opening.

Traditional keyword-based screening can miss relevant candidates because the same skill or experience can be described using different terminology.

This project uses an LLM to perform **context-aware resume evaluation** rather than relying only on exact keyword matching.

The system analyzes:

- Job requirements
- Candidate skills
- Candidate experience
- Education
- Responsibilities
- Preferred skills

It then produces structured evaluation results and calculates a final weighted candidate score.

---

## ✨ Features

### 1. AI Job Description Analysis

The system analyzes a job description and extracts structured requirements such as:

- Required skills
- Experience requirements
- Education requirements
- Responsibilities
- Preferred skills

The extracted information is validated using Pydantic models.

### 2. Resume Parsing

The application supports resume extraction from common document formats.

Currently supported:

- PDF
- DOCX

Resume information is converted into structured data before evaluation.

### 3. Context-Aware Skill Matching

The system does not depend solely on exact keyword matching.

It attempts to understand relationships between:

- Abbreviations and full forms
- Alternative terminology
- Common technical terminology
- Different wording
- Contextual references

For example, a technology or concept can be recognized even when the resume and job description use different but clearly equivalent terminology.

However, related technologies are not automatically treated as identical.

### 4. Multi-Criteria Candidate Evaluation

Candidates are evaluated across five categories:

- Skills
- Experience
- Education
- Responsibilities
- Preferred Skills

Each category receives a score from **0–100**.

### 5. Weighted Candidate Score

The application calculates a final score using fixed weights:

| Category | Weight |
|---|---:|
| Skills | 40% |
| Experience | 20% |
| Education | 10% |
| Responsibilities | 20% |
| Preferred Skills | 10% |

### 6. Recruitment Recommendation

The system provides a recommendation based on the overall candidate evaluation.

The results also include:

- Matching skills
- Missing important skills
- Experience assessment
- Education assessment
- Responsibility assessment
- Preferred skills assessment

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────┐
                         │      Recruiter      │
                         └──────────┬──────────┘
                                    │
                         Job Description
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Streamlit UI     │
                         │     web_app.py      │
                         └──────────┬──────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
          ┌──────────────────┐            ┌──────────────────┐
          │  Job Description │            │  Resume Upload   │
          │    Processing    │            │    PDF / DOCX    │
          └────────┬─────────┘            └────────┬─────────┘
                   │                               │
                   ▼                               ▼
          ┌──────────────────┐            ┌──────────────────┐
          │   Job Details    │            │  Resume Parser   │
          │   Extraction     │            │  resume_parser.py│
          └────────┬─────────┘            └────────┬─────────┘
                   │                               │
                   └───────────────┬───────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │      Groq LLM       │
                         │   AI Evaluation     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │   Match Evaluation  │
                         │                     │
                         │ Skills              │
                         │ Experience          │
                         │ Education           │
                         │ Responsibilities    │
                         │ Preferred Skills    │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Weighted Score      │
                         │ + Recommendation    │
                         └─────────────────────┘