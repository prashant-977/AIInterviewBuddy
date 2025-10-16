from scraping.job_scraper import scrape_job, fetch_job_descriptions
from analysis.compare_portfolio import compare_profiles
from analysis.preparation_suggestion import get_preparation_suggestions, save_text_as_pdf

import datetime
import os
import pandas as pd
import glob
import json


def main():
    # Check for existing comparison results file FIRST
    comparison_results_files = glob.glob('data/comparison_results_*.json')
    
    print(f"Looking for comparison results files...")
    print(f"Found {len(comparison_results_files)} comparison result files")
    
    if comparison_results_files:
        latest_comparison_file = max(comparison_results_files, key=os.path.getctime)
        print(f"✓ Using existing comparison results from: {latest_comparison_file}")
        print(f"✓ Skipping comparison step - results already exist")
        
        with open(latest_comparison_file, "r", encoding="utf-8") as f:
            comparison_results = json.load(f)
        
        # Load the corresponding job descriptions file for preparation suggestions
        list_of_files = glob.glob('data/job_descriptions_*.txt')
        if list_of_files:
            latest_file = max(list_of_files, key=os.path.getctime)
            print(f"✓ Using existing job descriptions from: {latest_file}")

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
            print("⚠ Warning: Comparison results found but no job descriptions file!")
            job_descriptions = {}
        
        perform_comparison = False
        
    else:
        # No existing comparison file, so we need to get job descriptions and perform comparison
        print("✗ No existing comparison results found - will perform new comparison")
        perform_comparison = True
        
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
            job_descriptions = fetch_job_descriptions(links)

        # Load candidate profile only when we need to perform comparison
        print("Loading candidate CV...")
        df_cv = pd.read_excel("data/CV.xlsx", header=None)
        st = ''
        for index, row in df_cv.iterrows():
            st += str(row.values[1])
        candidate_profile = st

        # Perform the comparison
        print("\n" + "="*50)
        print("PERFORMING JOB COMPARISONS...")
        print("="*50 + "\n")
        comparison_results = {}
        for job_header, job_description in job_descriptions.items():
            print(f"Comparing with {job_header}...")
            comparison_output = compare_profiles(candidate_profile, job_description)
            comparison_results[job_header] = comparison_output

        # Save all comparison results to a new file with a timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"data/comparison_results_{timestamp}.json"

        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(comparison_results, f, indent=4)

        print(f"\n✓ Comparison results saved to {output_filename}")
        print(f"✓ Comparison complete! Run the script again to get preparation suggestions.")
        return  # Exit after comparison is done

    # --- Preparation suggestions logic (only runs if comparison was NOT performed) ---
    if not comparison_results or not job_descriptions:
        print("⚠ Cannot provide preparation suggestions without comparison results and job descriptions.")
        return

    # Ask the user which job they want to prepare for
    print("\n" + "="*50)
    print("PREPARATION SUGGESTIONS")
    print("="*50)
    print("\nAvailable jobs for preparation:")
    job_keys = list(comparison_results.keys())
    for i, job_key in enumerate(job_keys):
        print(f"{i}: {job_key}")

    # Single attempt to get user input
    try:
        selected_job_index = int(input(f"\nEnter the number of the job you want to prepare for (0 to {len(job_keys) - 1}): "))
        if 0 <= selected_job_index < len(job_keys):
            print("\n⏳ Generating preparation suggestions...")
            # Get preparation suggestions
            suggestions = get_preparation_suggestions(selected_job_index, comparison_results, job_descriptions)
            
            if suggestions and not suggestions.startswith("Error:") and not suggestions.startswith("Invalid job index"):
                print("\n--- Preparation Suggestions ---")
                print(suggestions)
                
                # Save to PDF
                selected_job_key = job_keys[selected_job_index]
                pdf_filename = f"data/job_prep_suggestions_{selected_job_key.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
                save_text_as_pdf(suggestions, pdf_filename)
                print(f"\n✓ Preparation suggestions saved to {pdf_filename}")
            else:
                print(f"\n⚠ Could not generate suggestions: {suggestions}")
        else:
            print("⚠ Invalid number. Please run the script again and enter a valid number.")
    except ValueError:
        print("⚠ Invalid input. Please run the script again and enter a number.")
    except Exception as e:
        print(f"⚠ Error: {e}")


if __name__ == "__main__":
    main()