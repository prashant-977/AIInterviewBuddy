from langchain.agents import initialize_agent, AgentType
from langchain.tools import tool
from utils.llm_utils import get_llm

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

def compare_profiles(candidate: str, job: str):
    """Invoke LLM comparison."""
    prompt = (
        f"Compare the candidate's profile {candidate} with the job advert {job}. "
        "List matching skills, missing skills, and suggestions for improvement. "
        "Finally, produce a Python list of missing skills."
    )
    result = agent.invoke(prompt)
    return result["output"]

comparison_output = compare_profiles(st, summary_job) #??

# Specify the filename
output_filename = "comparison_results.txt"

# Save the output to a file
with open(output_filename, "w") as f:
    f.write(comparison_output)

print(f"Comparison results saved to {output_filename}")
