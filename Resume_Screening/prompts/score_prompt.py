from langchain_core.prompts import PromptTemplate

score_prompt = PromptTemplate(
    input_variables=["match_data"],
    template="""
Assign a score (0–100) based on:
- Skill match
- Experience relevance

Match Data:
{match_data}

Return ONLY:
{{ "score": number }}
"""
)