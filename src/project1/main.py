import time
from pathlib import Path

from .ai_service import extract_job_details, final_score, parse_resume
from .resume_parser import read_resume


def process_resumes(job_description: str, resume_folder: str = "Resumes"):
    """
    Process all PDF and DOCX resumes in a folder,
    compare them with the job description,
    and return ranked results.
    """

    # Step 1: Extract structured information from job description
    print("Analyzing job description...")
    job = extract_job_details(job_description)

    resume_folder_path = Path(resume_folder)

    if not resume_folder_path.exists():
        raise FileNotFoundError(
            f"Resume folder not found: {resume_folder_path}"
        )

    all_results = []

    # Step 2: Process each resume
    for file_path in resume_folder_path.iterdir():

        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in [".pdf", ".docx"]:
            continue

        print(f"\nProcessing: {file_path.name}")

        try:
            # Read resume
            resume_text = read_resume(file_path)

            if not resume_text.strip():
                print("No readable text found. Skipping...")
                continue

            # Parse resume using AI
            parsed_resume = parse_resume(resume_text)

            # Small delay between API requests
            time.sleep(5)

            # Compare resume with job
            result = final_score(job, parsed_resume)

            time.sleep(5)

            all_results.append(
                {
                    "file_name": file_path.name,
                    "candidate_name": parsed_resume.name,
                    "score": result.score,
                    "details": result.details,
                }
            )

            print(f"Score: {result.score}")

        except Exception as error:
            print(f"Error processing {file_path.name}: {error}")

    # Step 3: Rank candidates
    all_results.sort(
        key=lambda candidate: candidate["score"],
        reverse=True,
    )

    return all_results


def display_results(results):
    """Display ranked candidates in the terminal."""

    if not results:
        print("\nNo valid resumes were processed.")
        return

    print("\n" + "=" * 50)
    print("RESUME SHORTLISTING RESULTS")
    print("=" * 50)

    print("\nTOP CANDIDATES")

    for position, candidate in enumerate(results[:2], start=1):
        print(
            f"\n{position}. "
            f"{candidate['file_name']} "
            f"— {candidate['score']:.1f}%"
        )

        print(f"Details: {candidate['details']}")

    if len(results) > 2:

        print("\nLOWEST MATCHING CANDIDATES")

        for candidate in results[-2:]:
            print(
                f"\n{candidate['file_name']} "
                f"— {candidate['score']:.1f}%"
            )

            print(f"Details: {candidate['details']}")


def main():
    """Run the resume shortlisting application."""

    job_description = """
    Job Title: AI Developer

    Location: Indore (On-site)
    Experience: 6 Months – 2 Years
    Employment Type: Full-time

    About the Role

    We are looking for a motivated AI Developer to design,
    develop, and deploy AI-powered applications.

    The ideal candidate should have experience in Python,
    Machine Learning, Generative AI, and API integration.

    Required Skills:
    - Python
    - Machine Learning
    - Deep Learning
    - Generative AI
    - LLMs
    - Prompt Engineering
    - RAG
    - AI APIs
    - REST APIs
    - Git

    Preferred Qualifications:
    - Bachelor's degree in Computer Science, IT, AI,
      Data Science, or related field.
    - 6 months to 2 years of relevant experience.
    """

    results = process_resumes(job_description)

    display_results(results)


if __name__ == "__main__":
    main()