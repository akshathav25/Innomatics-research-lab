from llm import llm
from prompts.extract_prompt import extract_prompt

extraction_chain = extract_prompt | llm