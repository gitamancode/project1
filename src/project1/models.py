from pydantic import BaseModel


class JobD(BaseModel):
    role: str
    required_skills: list[str]
    preffered_skills: list[str]
    minimum_experience: float
    educational_requirement: list[str]
    responsibilities: list[str]


class MatchResult(BaseModel):
    score: float
    details: dict


class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skill_used: list[str]


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    linkedin: str | None = None
    github: str | None = None
    total_experience: float | None = None
    education: list[str]
    skills: list[str]
    experiences: list[Experience]
    projects: list[str]
    certifications: list[str]