from utils.llm_utils import get_llm

llm = get_llm()

def ask_multiple_questions(questions: list, context: str):
    """Ask LLM multiple questions and return a dictionary of answers."""
    answers = {}
    for q in questions:
        response = llm.invoke(f"{q}\nContext:\n{context}")
        answers[q] = response.content
    return answers
