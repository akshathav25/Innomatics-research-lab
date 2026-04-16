from langchain_core.prompts import PromptTemplate

match_prompt = PromptTemplate(
    input_variables=["resume_data", "job_description"],
    template="""
Compare resume with job description.

Return:
- matched_skills
- missing_skills
- match_percentage (0-100)

Resume Data:
{resume_data}

Job Description:
{job_description}

Return ONLY JSON.
"""
)