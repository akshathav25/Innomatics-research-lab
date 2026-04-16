from llm import llm
from prompts.explain_prompt import explain_prompt

explanation_chain = explain_prompt | llm