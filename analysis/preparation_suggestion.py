import json
import os
import glob
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
    job_description = job_descriptions.get(job_key, "Job description not found.") # Get the job description using the same key

    # Use the LLM to generate suggestions based on the comparison output and job description
    # This prompt asks for STAR questions, project ideas, and study materials
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

    # Assuming 'agent' is your initialized LangChain agent from previous cells
    # If not, you'll need to re-initialize it or use a direct LLM call
    try:
        preparation_suggestions = agent.invoke(prompt)
        # Return the text output
        return preparation_suggestions['output']
    except NameError:
        return "Error: LangChain agent 'agent' is not defined. Please run the cell that initializes the agent."
    except Exception as e:
        return f"An error occurred while generating suggestions: {e}"

def save_text_as_pdf(text, filename):
    """Saves a given string as a PDF file."""
    c = canvas.Canvas(filename, pagesize=letter)
    # Set font and size
    c.setFont("Helvetica", 12)

    # Add text to the PDF
    # Split text into lines and add them to the PDF
    lines = text.split('\n')
    y_position = 750 # Starting y position (top of the page)
    line_height = 14

    for line in lines:
        # Check if we need a new page
        if y_position < 50: # Add a new page if close to the bottom
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = 750
        c.drawString(50, y_position, line)
        y_position -= line_height

    c.save()


# --- Main execution flow ---

# Load the latest comparison results
comparison_results_files = glob.glob('data/comparison_results_*.json')
if not comparison_results_files:
    print("No comparison results found. Please run the comparison step first.")
else:
    latest_comparison_file = max(comparison_results_files, key=os.path.getctime)
    print(f"Loading comparison results from: {latest_comparison_file}")
    with open(latest_comparison_file, "r", encoding="utf-8") as f:
        comparison_results = json.load(f)

    # Load the latest job descriptions
    job_description_files = glob.glob('data/job_descriptions_*.txt')
    if not job_description_files:
        print("No job description files found. Cannot provide detailed suggestions.")
        job_descriptions = {} # Provide an empty dict to avoid errors
    else:
        latest_job_file = max(job_description_files, key=os.path.getctime)
        print(f"Loading job descriptions from: {latest_job_file}")
        job_descriptions = {}
        with open(latest_job_file, "r", encoding="utf-8") as f:
            content = f.read()
            job_entries = content.strip().split("Job ")
            for entry in job_entries:
                if entry:
                    lines = entry.split('\n', 1)
                    if len(lines) > 1:
                        try:
                             # Use the same key format as in comparison_results
                            job_descriptions[f"Job {lines[0].split(' ')[0]}"] = lines[1].strip()
                        except ValueError:
                            print(f"Could not parse job entry: {lines[0]}")
                            continue


    # Ask the user which job they want to prepare for
    print("\nAvailable jobs for preparation:")
    # Display job keys from comparison_results as they are guaranteed to exist
    job_keys = list(comparison_results.keys())
    for i, job_key in enumerate(job_keys):
        print(f"{i}: {job_key}")

    while True:
        try:
            selected_job_index = int(input(f"Enter the number of the job you want to prepare for (0 to {len(job_keys) - 1}): "))
            if 0 <= selected_job_index < len(job_keys):
                break
            else:
                print("Invalid number. Please enter a number within the range.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    # Get preparation suggestions
    suggestions_text = get_preparation_suggestions(selected_job_index, comparison_results, job_descriptions)

    # Check if suggestions were generated successfully
    if suggestions_text and not suggestions_text.startswith("Error:") and not suggestions_text.startswith("Invalid job index"):
        # Generate a filename
        selected_job_key = job_keys[selected_job_index]
        pdf_filename = f"job_prep_suggestions_{selected_job_key.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"

        # Save the suggestions to a PDF
        save_text_as_pdf(suggestions_text, pdf_filename)
        print(f"\nPreparation suggestions saved to {pdf_filename}")
    else:
        print(f"\nCould not generate suggestions: {suggestions_text}")