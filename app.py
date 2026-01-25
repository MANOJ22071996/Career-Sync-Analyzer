import streamlit as st

st.title("📊 Career-Sync: Skill Gap Analyzer")
st.write("Resume vs Job Description Analysis")

resume_skills = st.text_area("Enter your Skills (e.g., Python, SQL, Power BI):")
job_skills = st.text_area("Enter Job Description Skills:")

if st.button("Analyze Gap"):
    r_set = set([s.strip().lower() for s in resume_skills.split(',')])
    j_set = set([s.strip().lower() for s in job_skills.split(',')])

    matched = r_set.intersection(j_set)
    missing = j_set - r_set

    st.subheader("Results")
    st.success(f"✅ Matched Skills: {', '.join(matched) if matched else 'None'}")
    st.error(f"⚠️ Missing Skills to Learn: {', '.join(missing) if missing else 'None'}")

    match_percent = len(matched) / len(j_set) * 100 if j_set else 0
    st.write(f"Job Match Score: {match_percent:.1f}%")
    st.progress(match_percent / 100)