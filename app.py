import streamlit as st
import requests
import openai
import docx

st.title("AI Job Matcher")

openai_api_key = st.secrets["OPENAI_API_KEY"]
jsearch_api_key = st.secrets["JSEARCH_API_KEY"]

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def get_job_postings(query):
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": jsearch_api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {"query": query, "page": "1", "num_pages": "1"}
    response = requests.get(url, headers=headers, params=params)
    return response.json().get("data", [])

def rank_jobs_with_gpt(resume_text, jobs):
    openai.api_key = openai_api_key
    job_descriptions = "\n\n".join([f"{i+1}. {job['job_title']} at {job['employer_name']}\n{job['job_description'][:300]}" for i, job in enumerate(jobs)])
    prompt = f"""You are an AI career assistant. Based on the following resume or LinkedIn summary, rank the jobs below from most to least relevant.

Resume:
{resume_text}

Jobs:
{job_descriptions}

Return your answer as a list like:
1. Job Title - Employer
2. ... etc.
"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )
    return response.choices[0].message["content"]

# Inputs
option = st.radio("Provide your:", ["Resume (Word)", "LinkedIn URL"])
user_input = None

if option == "Resume (Word)"):
    uploaded_file = st.file_uploader("Upload your resume (.docx)", type="docx")
    if uploaded_file:
        user_input = extract_text_from_docx(uploaded_file)
elif option == "LinkedIn URL":
    user_input = st.text_input("Paste your LinkedIn profile URL")

if user_input:
    query = "entry level professional services"
    jobs = get_job_postings(query)
    if jobs:
        ranked_jobs = rank_jobs_with_gpt(user_input, jobs)
        st.subheader("Top Job Matches:")
        st.markdown(ranked_jobs)
    else:
        st.error("No jobs found.")