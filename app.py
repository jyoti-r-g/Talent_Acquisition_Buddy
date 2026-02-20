import os
import tempfile
import pandas as pd
import streamlit as st
import re
import json

from functions3 import (
    file_to_md, flatten_tables, read_text_from_md,
    extract_location, score_location, extract_email, extract_contact_number,
    gemini_email, gemini_cover_letter
)

from utils import llm_model  # Ensure you have this (Gemini chat model) in your utils.py

st.set_page_config(page_title="Talent Acquisition Buddy", layout="wide")
st.title("📄 Talent Acquisition Buddy ")

# ----------- Helper functions ------------

def extract_keywords_from_text(text, model_name="Gemini Flash"):
    prompt = f"""
You are an expert at extracting short, self-explanatory keywords from documents.

Extract a comma-separated list of contextually meaningful and **self-explanatory** keywords from the following text. 
Each keyword should be as short as possible but fully clear in meaning and context (e.g. "bachelor degree in computer science", "master degree in physics", "certification in data science", "Python", "Machine Learning", "AWS"). 
Expand all short forms and abbreviations to their full forms.
Avoid unnecessary length, full sentences, or vague terms.

Return ONLY the JSON below (no extra words):

{{
  "keywords": [ ... ]
}}

TEXT:
{text}
"""
    from langchain_core.prompts import ChatPromptTemplate
    chain = ChatPromptTemplate.from_template("{prompt}") | llm_model
    response = chain.invoke({"prompt": prompt})
    output = response.content.strip()
    json_match = re.search(r"\{[\s\S]*\}", output)
    keywords = []
    if json_match:
        try:
            out = json.loads(json_match.group())
            keywords = [kw.strip().lower() for kw in out.get("keywords", []) if kw.strip()]
        except Exception:
            pass
    if not keywords:
        keywords = [w.strip().lower() for w in output.split(",") if w.strip()]
    keywords = list(set(keywords))
    keywords.sort()
    return keywords

def compute_weighted_score(resume_kw, high_kw, med_kw, low_kw):
    resume_kw_set = set(k.strip().lower() for k in resume_kw)
    a = len(resume_kw_set & set(k.strip().lower() for k in high_kw))
    b = len(resume_kw_set & set(k.strip().lower() for k in med_kw))
    c = len(resume_kw_set & set(k.strip().lower() for k in low_kw))
    return a*3 + b*2 + c*1

# ---------- Session state ----------
if "jd_keywords" not in st.session_state:
    st.session_state["jd_keywords"] = None
if "high_priority" not in st.session_state:
    st.session_state["high_priority"] = []
if "medium_priority" not in st.session_state:
    st.session_state["medium_priority"] = []
if "set_priority_step" not in st.session_state:
    st.session_state["set_priority_step"] = 0
if "priority_keywords" not in st.session_state:
    st.session_state["priority_keywords"] = []
if "interim_results" not in st.session_state:
    st.session_state["interim_results"] = None
if "loc_done" not in st.session_state:
    st.session_state["loc_done"] = False

# ---------- User Inputs ------------
st.header("Upload Files for Batch 1")
resumes = st.file_uploader(
    "Upload any number of Resumes (PDF/DOCX)",
    type=["pdf", "docx"],
    accept_multiple_files=True,
    key="batch1_resumes",
)

days_available = []
if resumes:
    st.markdown("**Enter Days after which each candidate is available:**")
    for r in resumes:
        day_val = st.number_input(
            f"Days for {r.name}",
            min_value=1,
            max_value=365,
            value=1,
            step=1,
            key=f"day_{r.name}",
        )
        days_available.append(day_val)

jd = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"], key="batch1_jd")
# Removed LLM choice, default to Gemini

# ---------- JD Keyword Extraction & Priority Setting ----------

def extract_jd_keywords(jd_file):
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_md_path = file_to_md(jd_file, tmpdir)
        jd_flat_md_path = flatten_tables(jd_md_path, tmpdir)
        jd_text = read_text_from_md(jd_flat_md_path)
        keywords = extract_keywords_from_text(jd_text)
        return keywords

if jd and st.session_state["jd_keywords"] is None:
    st.info("Extracting keywords from job description using Gemini...")
    st.session_state["jd_keywords"] = extract_jd_keywords(jd)
    st.session_state["set_priority_step"] = 1
    st.session_state["high_priority"] = []
    st.session_state["medium_priority"] = []
    st.session_state["priority_keywords"] = st.session_state["jd_keywords"].copy()

if st.session_state["set_priority_step"] == 1 and st.session_state["jd_keywords"]:
    st.subheader("Step 1: Select HIGH Priority JD Keywords")
    selected_high = st.multiselect(
        "Tick the keywords that are HIGH priority for this job description:",
        st.session_state["priority_keywords"], default=[]
    )
    if st.button("Confirm High Priority Selection"):
        st.session_state["high_priority"] = selected_high
        st.session_state["priority_keywords"] = [
            x for x in st.session_state["priority_keywords"] if x not in selected_high
        ]
        st.session_state["set_priority_step"] = 2

if st.session_state["set_priority_step"] == 2 and st.session_state["priority_keywords"]:
    st.subheader("Step 2: Select MEDIUM Priority JD Keywords")
    selected_medium = st.multiselect(
        "Tick the keywords that are MEDIUM priority for this job description:",
        st.session_state["priority_keywords"], default=[]
    )
    if st.button("Confirm Medium Priority Selection"):
        st.session_state["medium_priority"] = selected_medium
        st.session_state["priority_keywords"] = [
            x for x in st.session_state["priority_keywords"] if x not in selected_medium
        ]
        st.session_state["set_priority_step"] = 3

if st.session_state["set_priority_step"] == 3:
    st.success("Priority selection done!")
    st.write("**High Priority:**", st.session_state["high_priority"])
    st.write("**Medium Priority:**", st.session_state["medium_priority"])
    st.write("**Low Priority:**", st.session_state["priority_keywords"])
    if st.button("Proceed to Resume Processing"):
        st.session_state["set_priority_step"] = 4

# ---------- Main Pipeline ----------
def process(resume_files, jd_file, days_available_list,
            high_priority, medium_priority, low_priority, tmpdir):
    if not resume_files or not jd_file:
        return []
    all_results = []
    jd_md_path = file_to_md(jd_file, tmpdir)
    jd_flat_md_path = flatten_tables(jd_md_path, tmpdir)
    jd_text = read_text_from_md(jd_flat_md_path)
    for i, res in enumerate(resume_files):
        res_md_path = file_to_md(res, tmpdir)
        res_flat_md_path = flatten_tables(res_md_path, tmpdir)
        res_text = read_text_from_md(res_flat_md_path)

        # NO embeddings, cosine, projection, etc.
        # LLM cover letter & email (always Gemini)
        cover = gemini_cover_letter(res_text, jd_text)
        email = gemini_email(res_text, jd_text)
        
        location = extract_location(res_text, "Gemini Flash")
        loc_score = score_location(location)
        email_id = extract_email(res_text)
        contact_number = extract_contact_number(res_text)
        resume_keywords = extract_keywords_from_text(res_text)
        weighted_score = compute_weighted_score(
            resume_keywords,
            high_priority,
            medium_priority,
            low_priority
        )
        all_results.append({
            "Resume File": res.name,
            "Job Description": jd_file.name,
            "Candidate Location": location,
            "Cover Letter": cover,
            "Email": email,
            "email_id": email_id,
            "contact_number": contact_number,
            "Days Available": days_available_list[i],
            "Batch": "Batch 1",
            "Location Score": loc_score,
            "Resume_Keywords": ', '.join(resume_keywords),
            "weighted_score": weighted_score
        })
    return all_results

if st.session_state["set_priority_step"] == 4:
    if st.button("Process Batch with Weighted Score"):
        with tempfile.TemporaryDirectory() as tmpdir:
            high_p = st.session_state["high_priority"]
            med_p = st.session_state["medium_priority"]
            low_p = st.session_state["priority_keywords"]
            results = process(
                resumes, jd, days_available,
                high_p, med_p, low_p, tmpdir
            )
            df_init = pd.DataFrame(results)
        st.session_state["interim_results"] = df_init.copy()
        st.session_state["loc_done"] = False

# ---------- Manual Location‑Score Edit ----------
if st.session_state["interim_results"] is not None:
    df_init = st.session_state["interim_results"]
    st.subheader("🔄 Edit Location Score")
    if not df_init.empty:
        st.markdown("You can edit the 'Location Score' column below if you wish to change it manually.")
        edited_scores = []
        for idx, row in df_init.iterrows():
            new_score = st.number_input(
                f"Location Score for {row['Resume File']} (Current: {row['Location Score']}, Location: {row['Candidate Location']})",
                min_value=0.0,
                max_value=1.0,
                value=float(row['Location Score']),
                step=0.01,
                key=f"loc_score_{idx}",
            )
            edited_scores.append(new_score)
        if st.button("✅ Done Editing Location Scores"):
            df_init["Location Score"] = edited_scores
            st.session_state["loc_done"] = True
            st.session_state["interim_results"] = df_init.copy()

# ---------- Final Ranking & Download ----------
if st.session_state.get("loc_done", False):
    df_final = st.session_state["interim_results"].copy()
    # No embeddings/cosine/projection/scaling
    text_cols = [
        "Resume File", "Job Description", "Candidate Location", "Cover Letter", "Email", "email_id", "contact_number", "Days Available", "Batch",
        "Resume_Keywords", "weighted_score"
    ]
    df_final = df_final[text_cols]
    df_final = df_final.sort_values("weighted_score", ascending=False).reset_index(drop=True)
    st.subheader("🔎 Final Results (Sorted by Weighted Score)")
    st.dataframe(df_final)
    out_path = os.path.join(tempfile.gettempdir(), "final_results.xlsx")
    df_final.to_excel(out_path, index=False)
    with open(out_path, "rb") as f:
        st.download_button(
            "📥 Download Excel Results",
            f,
            file_name="final_results.xlsx",
        )
