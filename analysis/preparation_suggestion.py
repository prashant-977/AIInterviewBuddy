import json
import os
import glob
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

def get_preparation_suggestions(job_index: int, comparison_results: dict, job_descriptions: dict):
    """
    Generates personalized preparation suggestions based on job comparison.
    Returns the suggestions as a string.
    """
    # Get the key for the selected job from comparison_results
    job_keys = list(comparison_results.keys())
    if not (0 <= job_index < len(job_keys)):
         return "Invalid job index selected."

    job_key = job_keys[job_index]

    if job_key not in comparison_results:
        return "Invalid job index selected."

    comparison_output = comparison_results[job_key]
    job_description = job_descriptions.get(job_key, "Job description not found.")

    # Use the LLM to generate suggestions based on the comparison output and job description
    prompt = (
        f"Based on the following comparison between a candidate's profile and the job requirements:\n\n"
        f"{comparison_output}\n\n"
        f"And the full job description:\n\n"
        f"{job_description}\n\n"
        f"Generate personalized preparation suggestions for the candidate applying for this role. Include:\n"
        f"1. A list of potential STAR interview questions tailored to the required skills and responsibilities.\n"
        f"2. Suggestions for projects the candidate could work on to address any missing skills or strengthen relevant areas.\n"
        f"3. Recommendations for articles, topics, or resources the candidate should study to prepare for the role.\n"
        f"Format the response clearly with headings for each section."
    )

    try:
        # Initialize the LLM directly here
        llm = ChatOpenAI(
            model="gpt-4.1",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Get the response
        response = llm.invoke(prompt)
        preparation_suggestions = response.content
        
        return preparation_suggestions
    except Exception as e:
        return f"An error occurred while generating suggestions: {e}"

def save_text_as_pdf(text, filename):
    """Saves a given string as a PDF file."""
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    lines = text.split('\n')
    y_position = 750
    line_height = 14

    for line in lines:
        if y_position < 50:
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750
        # Wrap long lines if needed
        if len(line) > 90:
            words = line.split(' ')
            current_line = ''
            for word in words:
                if len(current_line + word) < 90:
                    current_line += word + ' '
                else:
                    c.drawString(50, y_position, current_line)
                    y_position -= line_height
                    current_line = word + ' '
                    if y_position < 50:
                        c.showPage()
                        c.setFont("Helvetica", 12)
                        y_position = 750
            if current_line:
                c.drawString(50, y_position, current_line)
                y_position -= line_height
        else:
            c.drawString(50, y_position, line)
            y_position -= line_height

    c.save()

