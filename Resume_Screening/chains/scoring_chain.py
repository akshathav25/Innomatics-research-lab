from llm import llm
from prompts.score_prompt import score_prompt

scoring_chain = score_prompt | llm