from scraping.job_scraper import scrape_job, fetch_job_descriptions
from analysis.compare_portfolio import compare_profiles
#from analysis.ask_questions import ask_multiple_questions
from analysis.preparation_suggestion import get_preparation_suggestions

import datetime
import os
import glob
import json # Import json

def main():
    # Check for existing job description files
    list_of_files = glob.glob('data/job_descriptions_*.txt')
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"Using existing job descriptions from: {latest_file}")

        job_descriptions = {}
        with open(latest_file, "r", encoding="utf-8") as f:
            content = f.read()
            job_entries = content.strip().split("Job ")
            for entry in job_entries:
                if entry:
                    lines = entry.split('\n', 1)
                    if len(lines) > 1:
                        try:
                            job_description_text = lines[1].strip()
                            job_descriptions[lines[0].strip()] = job_description_text
                        except ValueError:
                            print(f"Could not parse job entry: {lines[0]}")
                            continue
    else:
        # If no existing files, prompt for job title and scrape
        job_title = input("Enter job title to search: ")
        links = scrape_job(job_title)
        job_descriptions = fetch_job_descriptions(links) # This now saves to a file and returns the descriptions dictionary


    df_cv = pd.read_excel("data/CV.xlsx", header=None)
    #df_cv
    st=''
    for index, row in df_cv.iterrows():
      #print(row.values[1])
      st+=row.values[1]
    candidate_profile = st # Using the 'st' variable from your notebook

    # Check for existing comparison results file
    comparison_results_files = glob.glob('data/comparison_results_*.json')
    if comparison_results_files:
        latest_comparison_file = max(comparison_results_files, key=os.path.getctime)
        print(f"Using existing comparison results from: {latest_comparison_file}")
        with open(latest_comparison_file, "r", encoding="utf-8") as f:
            comparison_results = json.load(f)
    else:
        # Compare candidate profile with each job description and save results
        comparison_results = {}
        for job_header, job_description in job_descriptions.items():
            print(f"Comparing with {job_header}...")
            comparison_output = compare_profiles(candidate_profile, job_description)
            comparison_results[job_header] = comparison_output

        # Save all comparison results to a new file with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"data/comparison_results_{timestamp}.json" # Using .json to store structured results

        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(comparison_results, f, indent=4)

        print(f"Comparison results saved to {output_filename}")
		
    # --- Add the preparation suggestions logic here ---
    if not comparison_results or not job_descriptions:
         print("Cannot provide preparation suggestions without comparison results and job descriptions.")
         return # Exit if required data is missing

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
    # Pass the actual job index (0, 1, 2...) to the function
    suggestions = get_preparation_suggestions(selected_job_index, comparison_results, job_descriptions)
    print("\n--- Preparation Suggestions ---")
    print(suggestions)		


'''
    # Ask custom questions
    questions = [
        "What are the candidate's strongest matches for this job?",
        "Which areas need upskilling?",
        "What sample projects can strengthen the profile?"
    ]
    answers = ask_multiple_questions(questions, comparison)
    for q, a in answers.items():
        print(f"\nQ: {q}\nA: {a}")

    # Suggest upskilling
    missing_skills = ["Python", "Docker"]  # Replace with parsed list from LLM output
    upskilling_plan = suggest_upskilling(missing_skills)
    print("\nUpskilling Suggestions:\n", upskilling_plan)
'''

if __name__ == "__main__":
    main()
