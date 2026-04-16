from dotenv import load_dotenv
load_dotenv()

from chains.extraction_chain import extraction_chain
from chains.matching_chain import matching_chain
from chains.scoring_chain import scoring_chain
from chains.explanation_chain import explanation_chain

import json
import re

def clean_json(response):
    content = response.content

    if isinstance(content, list):
        content = " ".join([item["text"] for item in content if "text" in item])

    content = re.sub(r"```json|```", "", content).strip()

    return json.loads(content)

# Sample Data
resume = """
Python developer with 2 years experience.
Worked with Machine Learning and Pandas.
"""

job_description = """
Looking for Data Scientist with Python, Machine Learning,
Deep Learning, SQL, and 3+ years experience.
"""

# Step 1: Extract
resume_data = clean_json(extraction_chain.invoke({"resume": resume}))

# Step 2: Match
match_data = clean_json(matching_chain.invoke({
    "resume_data": resume_data,
    "job_description": job_description
}))

# Step 3: Score
score = clean_json(scoring_chain.invoke({"match_data": match_data}))

# Step 4: Explain
response = explanation_chain.invoke({
    "resume_data": resume_data,
    "match_data": match_data,
    "score": score
})

explanation = response.content[0]["text"]

print("\n=== FINAL OUTPUT ===")
print("Resume Data:", resume_data)
print("Match:", match_data)
print("Score:", score)
print("Explanation:", explanation)