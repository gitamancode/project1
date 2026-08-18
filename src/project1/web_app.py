import tempfile
from pathlib import Path

import streamlit as st

from project1.ai_service import (
    calculate_weighted_score,
    extract_job_details,
    final_score,
    parse_resume,
)
from project1.resume_parser import read_resume


st.set_page_config(
    page_title="AI Resume Shortlister",
    page_icon="🤖",
    layout="wide",
)


st.title("🤖 AI Resume Shortlisting System")

st.write(
    "Analyze job descriptions and rank candidates using "
    "LLM-powered resume screening."
)


# ---------------------------------------------------------
# Job Description
# ---------------------------------------------------------

st.subheader("1. Job Description")

job_description = st.text_area(
    "Paste the job description",
    height=300,
    placeholder="Paste the complete job description here...",
)


# ---------------------------------------------------------
# Resume Upload
# ---------------------------------------------------------

st.subheader("2. Upload Resumes")

uploaded_files = st.file_uploader(
    "Upload candidate resumes",
    type=["pdf", "docx"],
    accept_multiple_files=True,
)


# ---------------------------------------------------------
# Analyze
# ---------------------------------------------------------

if st.button("🚀 Analyze Resumes", type="primary"):

    if not job_description.strip():
        st.error("Please enter a job description.")
        st.stop()

    if not uploaded_files:
        st.error("Please upload at least one resume.")
        st.stop()

    try:

        # -------------------------------------------------
        # Analyze Job Description
        # -------------------------------------------------

        with st.spinner("Analyzing job description..."):

            job = extract_job_details(job_description)

        st.success("Job description analyzed successfully.")

        results = []

        # -------------------------------------------------
        # Process Resumes
        # -------------------------------------------------

        progress = st.progress(0)

        for index, uploaded_file in enumerate(uploaded_files):

            st.write(f"Processing **{uploaded_file.name}**...")

            suffix = Path(uploaded_file.name).suffix

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as temp_file:

                temp_file.write(uploaded_file.getbuffer())
                temp_path = Path(temp_file.name)

            try:

                # Extract resume text
                resume_text = read_resume(temp_path)

                if not resume_text.strip():
                    st.warning(
                        f"Could not extract text from "
                        f"{uploaded_file.name}."
                    )
                    continue

                # Parse resume
                resume = parse_resume(resume_text)

                # Calculate category scores
                result = final_score(job, resume)

                # Calculate final weighted score using Python
                final_score_value = calculate_weighted_score(result)

                results.append(
            {
                "file_name": uploaded_file.name,
                "candidate_name": resume.name or "Unknown",
                "score": final_score_value,
                "skills_score": result.skills_score,
                "experience_score": result.experience_score,
                "education_score": result.education_score,
                "responsibilities_score": result.responsibilities_score,
                "preferred_skills_score": result.preferred_skills_score,
                "details": result.details,
            }
            )
            finally:

                # Delete temporary file
                temp_path.unlink(missing_ok=True)

            progress.progress(
                (index + 1) / len(uploaded_files)
            )

        # -------------------------------------------------
        # Sort Results
        # -------------------------------------------------

        results.sort(
            key=lambda candidate: candidate["score"],
            reverse=True,
        )

        if not results:
            st.error("No resumes could be processed.")
            st.stop()

        # -------------------------------------------------
        # Display Results
        # -------------------------------------------------

        st.divider()

        st.subheader("🏆 Candidate Ranking")

        for position, candidate in enumerate(
            results,
            start=1,
        ):

            score = candidate["score"]

            if position == 1:
                badge = "🥇"

            elif position == 2:
                badge = "🥈"

            elif position == 3:
                badge = "🥉"

            else:
                badge = "👤"

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:

                    st.markdown(
                        f"### {badge} {candidate['candidate_name']}"
                    )

                    st.write(
                        f"**Resume:** "
                        f"{candidate['file_name']}"
                    )

                with col2:

                    st.metric(
                        "Match Score",
                        f"{score:.1f}%",
                    )

                st.write("### 📊 Score Breakdown")

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric(
                        "Skills",
                        f"{candidate['skills_score']:.0f}/100",
                    )

                with col2:
                    st.metric(
                        "Experience",
                        f"{candidate['experience_score']:.0f}/100",
                    )

                with col3:
                    st.metric(
                        "Education",
                        f"{candidate['education_score']:.0f}/100",
                    )

                with col4:
                    st.metric(
                        "Responsibilities",
                        f"{candidate['responsibilities_score']:.0f}/100",
                    )

                with col5:
                    st.metric(
                        "Preferred Skills",
                        f"{candidate['preferred_skills_score']:.0f}/100",
                    )

                st.write("### 📝 Recruiter Analysis")

                st.json(candidate["details"])

    except Exception as error:

                st.error(
                f"Something went wrong: {error}"
            )