from llm import llm
from prompts.match_prompt import match_prompt

matching_chain = match_prompt | llm