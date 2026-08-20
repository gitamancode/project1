import json
import os
import streamlit as st

from dotenv import load_dotenv
from groq import Groq

from project1.models import JobD, MatchResult, Resume

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found.")

client = Groq(api_key=GROQ_API_KEY)

MODEL = "openai/gpt-oss-20b"


def extract_job_details(job_description: str) -> JobD:
    """Extract structured requirements from a job description."""

    job_schema = JobD.model_json_schema()

    system_prompt = f"""
You are an HR assistant.

Your task is to analyze a job description and extract
structured information from it.

Return ONLY a valid JSON object that matches this schema:

{job_schema}

IMPORTANT:
- Do not return the schema itself.
- Do not include fields such as "properties", "title", or "type".
- Fill the schema using only information present in the job description.
- Do not invent information.
"""

    user_prompt = f"""
Analyze the following job description and extract the
required information:

{job_description}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature = 0,
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content

    if not raw_json:
        raise ValueError("The AI returned an empty response.")

    return JobD(**json.loads(raw_json))


def parse_resume(resume_text: str) -> Resume:
    """Extract structured information from resume text."""

    resume_schema = Resume.model_json_schema()

    system_prompt = f"""
You are an expert resume parser.

Extract information from the resume based on its meaning,
not only based on exact section headings.

Different resumes may use different headings.

For example:
- Experience
- Professional Experience
- Work History
- Employment
- Internships

These may all contain relevant experience.

Skills may appear in:
- Skills section
- Work experience
- Internships
- Projects

Return ONLY valid JSON matching this schema:

{resume_schema}

Important rules:

1. Do not invent information.
2. If a value is not available, return null.
3. If a list has no information, return an empty list.
4. Include internships inside experiences.
5. Extract skills mentioned across the entire resume.
"""

    user_prompt = f"""
Parse the following resume:

{resume_text}
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt,
        },
        {
            "role": "user",
            "content": user_prompt,
        },
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature = 0,
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content

    if not raw_json:
        raise ValueError("The AI returned an empty response.")

    return Resume(**json.loads(raw_json))


def final_score(job: JobD, resume: Resume) -> MatchResult:
    """Evaluate a resume using fixed scoring categories."""

    match_schema = MatchResult.model_json_schema()

    prompt = f"""
You are an expert technical recruiter and resume evaluator.

Your task is to evaluate how well the candidate's resume matches the job
description.

JOB DESCRIPTION:
{job.model_dump_json(indent=2)}

CANDIDATE RESUME:
{resume.model_dump_json(indent=2)}

Evaluate the candidate using these five categories:

1. SKILLS SCORE
2. EXPERIENCE SCORE
3. EDUCATION SCORE
4. RESPONSIBILITIES SCORE
5. PREFERRED SKILLS SCORE

Each category must receive a score from 0 to 100.

IMPORTANT:

Do NOT perform simple keyword matching.

You must understand the meaning and context of the job requirements and
the candidate's resume.

Use your own language understanding and reasoning to determine whether
a skill, technology, concept, abbreviation, or phrase in the resume
represents the same or substantially similar knowledge or experience
required by the job.

For example, if the job description uses a full technical term while the
resume uses a commonly understood abbreviation, recognize the relationship
when the meaning is clearly equivalent.

Similarly, understand differences in:
- abbreviations and full forms
- singular and plural forms
- alternative terminology
- common technical terminology
- related wording
- contextual references
- skills mentioned under different resume sections

Do not require the exact words from the job description to appear in the
resume.

However, do NOT treat two technologies as equivalent merely because they
are related.

For example, knowing one technology does not automatically mean the
candidate knows every technology in the same field.

Use the surrounding context of the resume to determine whether the
candidate actually demonstrates the required skill.

Search for evidence across the ENTIRE resume, including:

- Technical Skills
- Professional Experience
- Internships
- Projects
- Certifications
- Education
- Project descriptions
- Work responsibilities

When deciding whether a skill is missing, ask yourself:

"Does this resume provide reasonable evidence that this candidate knows
or has worked with this concept, even if the exact wording is different?"

If YES, consider it a match.

If NO, consider it missing.

Do not invent skills or experience that are not supported by the resume.

For every matching or missing skill, base your decision on evidence from
the candidate's resume.

Your evaluation should resemble the reasoning of an experienced human
technical recruiter rather than a keyword-based ATS.

IMPORTANT SCORING RULE:

Do NOT calculate an overall score.

Only return the five category scores.

The Python application will calculate the final weighted score separately.

Also provide concise details containing:

- Candidate name
- Matching skills
- Missing important skills
- Experience assessment
- Education assessment
- Responsibility assessment
- Preferred skills assessment
- Final recommendation

Return ONLY valid JSON matching this schema:

{match_schema}

Do not return markdown.
Do not return explanations outside the JSON.
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content

    if not raw_json:
        raise ValueError("The AI returned an empty response.")

    return MatchResult(**json.loads(raw_json))

def calculate_weighted_score(result: MatchResult) -> float:
    """
    Calculate the final candidate score using fixed weights.

    Skills: 40%
    Experience: 20%
    Education: 10%
    Responsibilities: 20%
    Preferred Skills: 10%
    """

    score = (
        result.skills_score * 0.40
        + result.experience_score * 0.20
        + result.education_score * 0.10
        + result.responsibilities_score * 0.20
        + result.preferred_skills_score * 0.10
    )

    return round(score, 2)