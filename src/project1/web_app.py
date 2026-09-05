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


# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="AI Resume Shortlister",
    page_icon="🤖",
    layout="wide",
)


# ---------------------------------------------------------
# Helper Function: Display Candidate Result
# ---------------------------------------------------------

def display_candidate_result(candidate):

    with st.container(border=True):

        # Candidate Header
        col1, col2 = st.columns([3, 1])

        with col1:

            st.markdown(
                f"### ✅ {candidate['candidate_name']}"
            )

            st.write(
                f"**Resume:** {candidate['file_name']}"
            )

        with col2:

            st.metric(
                "Match Score",
                f"{candidate['score']:.1f}%",
            )

        # Score Breakdown
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

        # Recruiter Analysis
        st.write("### 📝 Recruiter Analysis")

        st.json(candidate["details"])


# ---------------------------------------------------------
# Application UI
# ---------------------------------------------------------

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
# Analyze Button
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

        with st.spinner("🔍 Analyzing job description..."):

            job = extract_job_details(job_description)

        st.success("✅ Job description analyzed successfully.")

        results = []

        # -------------------------------------------------
        # Processing Section
        # -------------------------------------------------

        st.divider()

        st.subheader("⚙️ Resume Analysis in Progress")

        progress_text = st.empty()

        progress = st.progress(0)

        current_resume = st.empty()

        # This container stores completed full results
        completed_results = st.container()

        total_resumes = len(uploaded_files)

        # -------------------------------------------------
        # Process Resumes Sequentially
        # -------------------------------------------------

        for index, uploaded_file in enumerate(uploaded_files):

            current_number = index + 1

            progress_text.info(
                f"📊 Processing resume {current_number} "
                f"of {total_resumes}"
            )

            current_resume.warning(
                f"🔄 Currently analyzing: "
                f"**{uploaded_file.name}**"
            )

            suffix = Path(uploaded_file.name).suffix

            temp_path = None

            try:

                # -----------------------------------------
                # Create Temporary File
                # -----------------------------------------

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as temp_file:

                    temp_file.write(uploaded_file.getbuffer())

                    temp_path = Path(temp_file.name)

                # -----------------------------------------
                # Extract Resume Text
                # -----------------------------------------

                resume_text = read_resume(temp_path)

                if not resume_text.strip():

                    with completed_results:

                        st.warning(
                            f"⚠️ Could not extract text from "
                            f"**{uploaded_file.name}**"
                        )

                    continue

                # -----------------------------------------
                # Parse Resume Using AI
                # -----------------------------------------

                resume = parse_resume(resume_text)

                # -----------------------------------------
                # Evaluate Candidate
                # -----------------------------------------

                result = final_score(job, resume)

                # -----------------------------------------
                # Calculate Final Weighted Score
                # -----------------------------------------

                final_score_value = calculate_weighted_score(
                    result
                )

                # -----------------------------------------
                # Store Candidate Result
                # -----------------------------------------

                candidate = {
                    "file_name": uploaded_file.name,
                    "candidate_name": resume.name or "Unknown",
                    "score": final_score_value,
                    "skills_score": result.skills_score,
                    "experience_score": result.experience_score,
                    "education_score": result.education_score,
                    "responsibilities_score": (
                        result.responsibilities_score
                    ),
                    "preferred_skills_score": (
                        result.preferred_skills_score
                    ),
                    "details": result.details,
                }

                results.append(candidate)

                # -----------------------------------------
                # SHOW FULL RESULT IMMEDIATELY
                # -----------------------------------------

                with completed_results:

                    display_candidate_result(candidate)

            except Exception as error:

                with completed_results:

                    st.error(
                        f"❌ Failed to process "
                        f"**{uploaded_file.name}**"
                    )

                    st.caption(f"Error: {error}")

            finally:

                # -----------------------------------------
                # Delete Temporary File
                # -----------------------------------------

                if temp_path:

                    temp_path.unlink(missing_ok=True)

                # -----------------------------------------
                # Update Progress
                # -----------------------------------------

                progress.progress(
                    current_number / total_resumes
                )

        # -------------------------------------------------
        # Processing Complete
        # -------------------------------------------------

        current_resume.empty()

        progress_text.success(
            f"🎉 Analysis complete! "
            f"{len(results)} of {total_resumes} "
            f"resumes analyzed successfully."
        )

        if not results:

            st.error("No resumes could be processed.")
            st.stop()

        # -------------------------------------------------
        # Sort Candidates After ALL Processing
        # -------------------------------------------------

        results.sort(
            key=lambda candidate: candidate["score"],
            reverse=True,
        )

        # -------------------------------------------------
        # Final Ranking
        # -------------------------------------------------

        st.divider()

        st.subheader("🏆 Final Candidate Ranking")

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
                        f"### {badge} #{position} "
                        f"{candidate['candidate_name']}"
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

    except Exception as error:

        st.error(
            f"Something went wrong: {error}"
        )