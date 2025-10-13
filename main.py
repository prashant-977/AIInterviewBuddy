from scraping.job_scraper import scrape_job, fetch_job_descriptions
from analysis.compare_portfolio import compare_profiles
from analysis.ask_questions import ask_multiple_questions
from analysis.upskilling import suggest_upskilling

def main():
    job_title = input("Enter job title to search: ")
    links = scrape_job(job_title)
    descriptions = fetch_job_descriptions(links)

    # Example candidate profile (load from file or DB in future)
    candidate_profile = open("data/candidate_profile.txt").read()

    # Compare with the first job description
    comparison = compare_profiles(candidate_profile, descriptions[0])
    print("Comparison:\n", comparison)

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


if __name__ == "__main__":
    main()
