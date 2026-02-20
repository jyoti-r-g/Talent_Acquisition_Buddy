import os
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

#Initialize models
# embedding_model = GoogleGenerativeAIEmbeddings(
#     model="models/gemini-embedding-exp-03-07", google_api_key=api_key
# )

# embedding_model = GoogleGenerativeAIEmbeddings(
#     model="models/embedding-001", google_api_key=api_key
# )

embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004", google_api_key=api_key
)

llm_model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=api_key,
    temperature=0.4,
    max_tokens=2000,
    max_retries=2,
)

# LangChain Prompt Template for cover letter
cover_letter_prompt = ChatPromptTemplate.from_template("""
You are a helpful assistant that writes professional cover letters.

Write a tailored cover letter using the following resume (in markdown format):
----------------
{resume}
----------------

{jd_section}
Please take the help of {resume} and fill the details of the cover letter like,

[Your Name]
[Your Address]
[Your Phone Number]
[Your Email Address]

After filling the above details do not put square brackets around above mentioned things.

Following is the not expected output example for the above instructions:

[Riya Dubey]  
[Laxmi Nagar, Delhi]  
[9822001387]  
[riya@gmail.com]

Following is the expected output example for the above instructions:

Riya Dubey  
Laxmi Nagar, Delhi  
9822001387  
riya@gmail.com

Make it concise, relevant, and formal in tone. Begin with a compelling intro, and end with a thank you and a call to action.
""".strip())

# === Function to compute similarity ===
def compute_similarity(resume_text, job_text):
    resume_vector = embedding_model.embed_query(resume_text)
    jd_vector = embedding_model.embed_query(job_text)
    similarity_score = cosine_similarity([resume_vector], [jd_vector])[0][0]
    return round(similarity_score, 2)

# === Updated Function to generate cover letter ===
def generate_cover_letter(resume, job_description):
    jd_section = (
        f"The job description is:\n----------------\n{job_description}\n----------------"
        if job_description.strip()
        else "There is no job description provided."
    )
    chain = cover_letter_prompt | llm_model
    response = chain.invoke({"resume": resume, "jd_section": jd_section})
    return response.content
