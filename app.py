import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ------------------------------------------
# PAGE CONFIG
#------------------------------------------
st.set_page_config(
    page_title="Career-Sync Analyzer",
    page_icon="📊",
    layout="centered"
)

# -----------------------------------------
# DATABASE SETUP
# -----------------------------------------
def init_db():
    conn = sqlite3.connect("skills.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS skill_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_skills TEXT,
            job_skills TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            match_score REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_analysis(resume, job, matched, missing, score):
    conn = sqlite3.connect("skills.db")
    c = conn.cursor()

    c.execute("""INSERT INTO skill_history (resume_skills, job_skills, matched_skills, missing_skills, match_score)
                 VALUES (?, ?, ?, ?, ?)""",
              (resume, job, matched, missing, score))
    
    conn.commit()
    conn.close()

@st.cache_data(ttl=60)
def load_history():
    conn = sqlite3.connect("skills.db")
    df = pd.read_sql_query("SELECT id, match_score, timestamp FROM skill_history ORDER BY timestamp DESC LIMIT 10", conn)
    conn.close()
    return df

# -----------------------------------------
# HELPER FUNCTION
# -----------------------------------------
def parse_skills(text):
    return set(
        skill.strip().lower()        for skill in text.split(',')
        if skill.strip()
    )

# -----------------------------------------
# UI START
# -----------------------------------------
st.title("📊 Career-Sync: Skill Gap Analyzer")
st.write("Compare your Resume skills with job Discription requriements.")

st.divider()

resume_skills = st.text_area("Enter your Skills (comma separated)",
                             placeholder="e.g., Python, SQL, Power BI, Excel")
job_skills = st.text_area("Enter Job Description Skills (comma separated)",
                          placeholder="e.g., Python, SQL,Tableau, Machine Learning")

# -----------------------------------------
# ANALYZE BUTTON
# -----------------------------------------

if st.button("🔍 Analyze Gap"):

    if not resume_skills.strip() or not job_skills.strip():
        st.warning("please enter skills in both fields.")
    else:
        r_set = parse_skills(resume_skills)
        j_set = parse_skills(job_skills)

        matched = r_set.intersection(j_set)
        missing = j_set - r_set

        match_percent = len(matched) / len(j_set) * 100 if j_set else 0
        match_percent = round(match_percent, 1)

        # ---------------------------
        # DISPLAY RESULTS
        # ---------------------------

        st.subheader("📈 Analysis Results")

        col1, col2 = st.columns(2)

        with col1:
            st.success(f"✅ Matched Skills:\n\n {', '.join(sorted(matched)) if matched else 'None'}")

            with col2:
                st.error(f"❌ Missing Skills to Learn:\n\n {', '.join(sorted(missing)) if missing else 'None'}")

                st.markdown(f"### 🎯 Job Match Score: {match_percent}%")


                st.progress(min(match_percent / 100, 1.0))

                # ----------------------------
                # BAR CHART
                # ----------------------------

                chart_data = pd.DataFrame({
                    'Category': ['Matched', 'Missing'],
                    'Count': [len(matched), len(missing)]
                })

                st.bar_chart(chart_data.set_index('Category'))

                # ----------------------------
                # SAVE TO DATABASE
                # ----------------------------

                save_analysis(resume_skills, job_skills, ", ".join(sorted(matched)), ", ".join(sorted(missing)), match_percent)

                st.cache_data.clear()  # Clear cache to refresh history on next load

                st.success("📁 Analysis saved successfully!")

                st.divider()

                # ----------------------------
                # HISTORY SECTION
                # ----------------------------
                st.subheader("🕓 Recent Analyses")

                history_df = load_history()

                if not history_df.empty:
                    st.dataframe(history_df, use_container_width=True)
                else:
                    st.info("No previous analyses found.")
    
