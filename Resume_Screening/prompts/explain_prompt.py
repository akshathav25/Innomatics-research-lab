from langchain_core.prompts import PromptTemplate

explain_prompt = PromptTemplate(
    input_variables=["resume_data", "match_data", "score"],
    template="""
Explain why this candidate received the score.

Include:
- Strengths
- Weaknesses
- Final justification

Resume:
{resume_data}

Match:
{match_data}

Score:
{score}
"""
)