from backend.llm.llm_setup import get_llm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def score_candidate_match(resume_text: str, job_description: str) -> str:
    prompt = PromptTemplate(
        input_variables=["resume_text", "job_description"],
        template="""
You're an AI hiring assistant. Given the following candidate resume and job description, score the candidate's suitability for the job on a scale of 0 to 100.

Also, provide a 2-3 sentence justification explaining why the score was given.

Resume:
{resume_text}

Job Description:
{job_description}

Respond in the format:
Score: <number>
Justification: <text>
"""
    )

    chain = LLMChain(llm=get_llm(), prompt=prompt)
    result = chain.run({
        "resume_text": resume_text,
        "job_description": job_description
    })

    return result.strip()
