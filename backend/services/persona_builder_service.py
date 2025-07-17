from backend.llm.llm_setup import get_llm
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

def generate_persona_from_resume(resume_text: str) -> str:
    prompt = PromptTemplate(
        input_variables=["resume_text"],
        template="""
You're an AI hiring assistant. Given the following resume text, generate a structured candidate persona summary.

Include:
- Name (if identifiable)
- Profession / Title
- Years of experience
- Key skills and technologies
- Personality traits or strengths
- Suggested/ideal roles

Resume:
{resume_text}

Respond in clean markdown format.
"""
    )

    chain = LLMChain(llm=get_llm(), prompt=prompt)
    result = chain.run({"resume_text": resume_text})
    return result.strip()
