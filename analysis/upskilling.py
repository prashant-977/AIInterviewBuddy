from utils.llm_utils import get_llm

llm = get_llm()

def suggest_upskilling(missing_skills: list):
    """Suggest resources or projects for upskilling."""
    skill_list = ", ".join(missing_skills)
    prompt = (
        f"For these missing skills: {skill_list}, "
        "suggest practical projects or online courses (preferably free or open-source)."
    )
    response = llm.invoke(prompt)
    return response.content
