import json
import os

from dotenv import load_dotenv
from groq import Groq

from .models import JobD, MatchResult, Resume


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables.")

client = Groq(api_key=GROQ_API_KEY)

MODEL = "openai/gpt-oss-120b"


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
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content

    if not raw_json:
        raise ValueError("The AI returned an empty response.")

    return Resume(**json.loads(raw_json))


def final_score(job: JobD, resume: Resume) -> MatchResult:
    """Compare a resume against a job description and calculate a match score."""

    match_schema = MatchResult.model_json_schema()

    prompt = f"""
You are an HR recruiter.

Compare the candidate's resume with the job description.

JOB DESCRIPTION:
{job.model_dump_json(indent=2)}

CANDIDATE RESUME:
{resume.model_dump_json(indent=2)}

Return JSON matching this schema:

{match_schema}

Provide:

1. Candidate name
2. Matching skills
3. Missing important skills
4. Whether the experience requirement is met
5. Overall match percentage from 0 to 100
6. A short final verdict

Keep the response concise and easy to read.
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        response_format={"type": "json_object"},
    )

    raw_json = response.choices[0].message.content

    if not raw_json:
        raise ValueError("The AI returned an empty response.")

    return MatchResult(**json.loads(raw_json))