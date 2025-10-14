from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from utils.llm_utils import get_llm
import json
import os
import datetime
import glob
import pandas as pd
df_cv = pd.read_excel("data/CV.xlsx", header=None)
df_cv

llm = get_llm()

@tool
def compare_portfolio_fn(candidate_profile: str, required_profile: str) -> list:
    """Compare a candidate's profile with the job's requirements."""
    return [candidate_profile, required_profile]

compare_portfolio_tool = compare_portfolio_fn

agent = initialize_agent(
    tools=[compare_portfolio_tool],
    llm=llm,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True
)

st=''
for index, row in df_cv.iterrows():
  #print(row.values[1])
  st+=row.values[1]
st



def compare_profiles(candidate: str, job: str):
    """Invoke LLM comparison."""
    prompt = (
        f"Compare the candidate's profile {candidate} with the job advert {job}. "
        "List matching skills, missing skills, and suggestions for improvement. "
        "Finally, produce a Python list of missing skills."
    )
    result = agent.invoke(prompt)
    return result["output"]

# Find the latest job descriptions file in the 'data' folder
list_of_files = glob.glob('data/job_descriptions_*.txt')
if not list_of_files:
    print("No job description files found in the 'data' folder.")
else:
    latest_file = max(list_of_files, key=os.path.getctime)
    print(f"Reading job descriptions from: {latest_file}")

    job_descriptions = {}
    with open(latest_file, "r", encoding="utf-8") as f:
        content = f.read()
        # Split the file content into individual job descriptions
        job_entries = content.strip().split("Job ")
        for entry in job_entries:
            if entry:
                lines = entry.split('\n', 1)
                if len(lines) > 1:
                    try:
                        job_index = int(lines[0].split(' ')[0]) - 1 # Extract job index (0-based)
                        job_descriptions[job_index] = lines[1].strip()
                    except ValueError:
                        print(f"Could not parse job index from entry: {lines[0]}")
                        continue


    # Assuming 'st' contains the candidate's portfolio string
    candidate_portfolio = st

    # Compare candidate profile with each job description and save results
    comparison_results = {}
    for i, job_description in job_descriptions.items():
        print(f"Comparing with Job {i+1}...")
        comparison_output = compare_profiles(candidate_portfolio, job_description)
        comparison_results[f"Job {i+1}"] = comparison_output

    # Save all comparison results to a new file with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    output_filename = f"data/comparison_results_{timestamp}.json" # Using .json to store structured results

    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(comparison_results, f, indent=4)

    print(f"Comparison results saved to {output_filename}")