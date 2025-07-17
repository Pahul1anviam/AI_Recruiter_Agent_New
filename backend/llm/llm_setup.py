import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()  # Load from .env

def get_llm():
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

def get_job_description_chain():
    prompt = PromptTemplate(
        input_variables=["job_title", "department", "responsibilities", "skills_required", "location", "experience_level"],
        template="""
Generate a clear, inclusive, and engaging job description using the following information:

- Job Title: {job_title}
- Department: {department}
- Experience Level: {experience_level}
- Location: {location}

Responsibilities:
{responsibilities}

Required Skills:
{skills_required}

Use professional language, optimize for SEO, and reflect a modern company tone.
"""
    )

    return LLMChain(llm=get_llm(), prompt=prompt)
