import sys
sys.path.append(r'C:\Users\tranq\Documents\Job_Preps\Startup Refugees\AIJobBuddy\.venv\Lib\site-packages')
import requests
from bs4 import BeautifulSoup

def scrape_job(job_title: str) -> list:
    """Scrape top 3 job links for a given title from jobly.fi"""
    url = f"https://www.jobly.fi/tyopaikat?search={job_title}"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    job_listings = soup.find_all("a", class_="recruiter-job-link")

    job_links = [listing['href'] for listing in job_listings]
    top3_jobs = job_links[::2][:3]
    return top3_jobs


def fetch_job_descriptions(job_links: list) -> dict:
    """Fetch job descriptions from given job URLs."""
    descriptions = {}
    for i, link in enumerate(job_links):
        response = requests.get(link)
        soup = BeautifulSoup(response.content, "html.parser")
        job_description_element = soup.find("div", class_="l-main")
        if not job_description_element:
            continue

        job_text = job_description_element.get_text(strip=True)
        text = "Hae paikkaaTallenna työpaikka"
        first_occurrence = job_text.find(text)
        second_occurrence = job_text.find(text, first_occurrence + 1)
        extracted_text = job_text[first_occurrence + len(text):second_occurrence]
        descriptions[i] = extracted_text+" "+link
    return descriptions
