import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

def get_llm(model="gpt-4", temperature=0):
    return ChatOpenAI(
        temperature=temperature,
        model=model,
        api_key=os.getenv("OPENAI_API_KEY")
    )
