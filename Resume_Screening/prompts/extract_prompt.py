from langchain_core.prompts import PromptTemplate

extract_prompt = PromptTemplate(
    input_variables=["resume"],
    template="""
You are an AI resume parser.

Extract the following from the resume:
- Skills
- Tools
- Experience (in years)

Rules:
- Do NOT assume anything not present
- Return ONLY JSON

Resume:
{resume}

Output:
"""
)