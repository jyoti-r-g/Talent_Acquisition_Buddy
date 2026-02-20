import os
import re
import numpy as np

import pandas as pd
import json
from docx import Document
from PyPDF2 import PdfReader

from table_flattener import flatten_md_tables
from utils import compute_similarity as gemini_similarity, generate_cover_letter as gemini_cover_letter, llm_model

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else ""

def extract_contact_number(text):
    match = re.search(r'(\+?\d[\d\-\(\) ]{8,}\d)', text)
    return match.group(0) if match else ""

def file_to_md(uploaded_file, tmpdir):
    file_path = os.path.join(tmpdir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())
    if file_path.endswith(".pdf"):
        from pdf_to_word import convert_pdf_to_word
        from word_to_md import convert_word_to_md
        docx_path = file_path.replace(".pdf", ".docx")
        convert_pdf_to_word(file_path, docx_path)
        md_path = docx_path.replace(".docx", ".md")
        convert_word_to_md(docx_path, md_path)
    elif file_path.endswith(".docx"):
        from word_to_md import convert_word_to_md
        md_path = file_path.replace(".docx", ".md")
        convert_word_to_md(file_path, md_path)
    else:
        return None
    return md_path

def flatten_tables(md_path, tmpdir):
    flat_md_path = os.path.join(tmpdir, "flattened_" + os.path.basename(md_path))
    flatten_md_tables(md_path, flat_md_path)
    return flat_md_path

def read_text_from_md(md_path):
    with open(md_path, 'r', encoding='utf-8') as f:
        return f.read()





def gemini_email(resume, jd):
    prompt = f"""You are an HR professional writing an email to a candidate. The candidate's resume is below, and so is the job description. Invite the candidate for a discussion/interview, mention why you are interested, and tell a few good points about the company. Write a professional email.
Resume:
{resume}
Job Description:
{jd}
"""
    from utils import llm_model
    from langchain_core.prompts import ChatPromptTemplate
    chain = ChatPromptTemplate.from_template("{prompt}") | llm_model
    response = chain.invoke({"prompt": prompt})
    return response.content.strip()

def extract_location(text, llm_choice):
    prompt = f"""Extract the current city or state location of the candidate from the following resume text. Only return the location, nothing else.\n\n{text}"""
    from utils import llm_model
    from langchain_core.prompts import ChatPromptTemplate
    chain = ChatPromptTemplate.from_template("{prompt}") | llm_model
    response = chain.invoke({"prompt": prompt})
    return response.content.strip()

def score_location(location):
    loc = location.lower()
    if "telangana" in loc or "andhra pradesh" in loc:
        return 0.1
    return 0



# ----------- KEYWORD EXTRACTION FUNCTION (your new requirement) -----------
def key_word_extraction(resume_text, jd_text, llm_choice):
    """
    Extracts keywords and computes match ratio using either Gemini Flash or DeepSeek LLM.
    Returns a string (full answer) and a float (fraction).
    """
    prompt = f"""
You are an expert at extracting and matching keywords from resumes and job descriptions.

Follow these steps:

STEP 1:
Extract a comma-separated list of concise, contextually meaningful, and **self-explanatory** keywords from the RESUME below. 
Each keyword should be as short as possible but still fully clear in meaning and context. e.g Master of Science in Physics, Bachlors degree in Chemistry.
Use the full form for acronyms/abbreviations (e.g., "NLP" → "Natural Language Processing", "B.Tech" → "Bachelor of Technology").
Use short, phrase-level terms when possible, such as 'Python', 'Data Analysis', 'AWS', 'Deep Learning', but also degrees or qualifications such as 'Master of Science in Chemistry', 'Bachelor's degree in Physics'. 
Avoid unnecessary length, sentences, or vague terms. 

STEP 2:
Extract a comma-separated list of concise, contextually meaningful, and **self-explanatory** keywords from the JOB DESCRIPTION below, in the same way as for the resume.

STEP 3:
Create a comma-separated list of common keywords between the resume and job description keywords.
The keywords do not have to match exactly in spelling—consider two keywords as common if they are synonyms or refer to the same skill/concept/qualification, even if phrased differently.

Format your output as strictly structured JSON, like this:
{{
  "resume_keywords": [ ... ],
  "jd_keywords": [ ... ],
  "common_keywords": [ ... ]
}}

RESUME:
{resume_text}

JOB DESCRIPTION:
{jd_text}

"NOTE": Never give out put like "Bachelor's degree", "Master's degree". If are giving some education details then give in out put like "Bachelor's degree in Electronics", "Master's degree in Physics", certification in data science. Given outputs are just example. Give you answer according to the document provided. So the format is " degree/diploma/certification in subject".
"""
    # Generate LLM response
    # Generate LLM response
    from langchain_core.prompts import ChatPromptTemplate
    chain = ChatPromptTemplate.from_template("{prompt}") | llm_model
    response = chain.invoke({"prompt": prompt})
    text = response.content.strip()

    # Try to extract JSON
    json_match = re.search(r"\{[\s\S]*\}", text)
    match_ratio = 0.0
    if json_match:
        try:
            output = json.loads(json_match.group())
            resume_keywords = output.get("resume_keywords", [])
            jd_keywords = output.get("jd_keywords", [])
            common_keywords = output.get("common_keywords", [])
            if len(jd_keywords) > 0:
                match_ratio = round(100 * len(common_keywords) / len(jd_keywords), 2)
        except Exception:
            pass

    # Append the 'answer: <ratio>' line at the end for consistency
    answer_text = f"{text}\nanswer: {match_ratio}"
    return answer_text, match_ratio
