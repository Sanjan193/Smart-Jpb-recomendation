import openai
import tkinter as tk
from tkinter import filedialog
import PyPDF2
import requests
import ast
import os

# Securely API setting 
openai.api_key = os.getenv("OPENAI_API_KEY", "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")

#Selecting PDF
def select_pdf():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select Resume PDF",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

#Extract text code
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    # print(text)            
    return text

# Extract perticular skills using an gpt LLM 
def extract_skills_with_llm(resume_text):
   
    if len(resume_text) > 4000:
        resume_text = resume_text[:4000] + "..."
    
    prompt = f"""
    You are an expert resume parser. Extract key technical skills which are required for a company tehnical rolls from the text below.Keep the most important skills at the first of the list. 
    Return them as a clean Python list (no duplicates).Keep the list short not too vast, with the most demanded skills.

    Resume:
    {resume_text}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    
    # Converting string to list
    skills_str = response.choices[0].message["content"].strip()

    # Removing code block markers if present
    if skills_str.startswith("```"):
      skills_str = skills_str.split("```")[1]  
      skills_str = skills_str.replace("python", "").strip()
    
    



    try:
        skills = ast.literal_eval(skills_str)
    except Exception:
        
        skills = []
        lines = skills_str.strip().split('\n')
        for line in lines:
            if line.startswith('- '):
                skills.append(line[2:].strip())
            elif line.startswith('* '):
                skills.append(line[2:].strip())
        if not skills:
            skills = [s.strip() for s in skills_str.split(',')]
    return skills


# Fetching jobs from API
def fetch_jobs(skills):
    url = "https://jsearch.p.rapidapi.com/search?query=developer%20jobs%20in%20ch"
    querystring = {"query": ",".join(skills[:5]),"page": "1", "num_pages": "1"}
    
    headers = {
        "x-rapidapi-key": "cab7bb7636msh81186f48afc3d76p1a4eafjsnc5bd9c3b1ecd",
        "x-rapidapi-host": "jsearch.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # print(f"API Response: {data}") 
            
            # Check if the response contains the expected data structure
            if "data" in data:
                jobs = data.get("data", [])
                return [
                    {"title": job.get("job_title", "\n"), 
                     
                         "company": job.get("employer_name", "\n"), 

                         "link": job.get("job_apply_link", "\n")
                         } 
                          for job in jobs[:5]]
            else:
                print(f"Unexpected API response format: {data}")
                return []
        else:
            print(f"API Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error fetching jobs: {e}")
        return []


if __name__ == "__main__":
    pdf_path = select_pdf()
    if pdf_path:
        resume_text = extract_text_from_pdf(pdf_path)
        print("Extracting skills using LLM\n")
        skills = extract_skills_with_llm(resume_text)
        print("Skills found:", skills)

        
        for skill in skills:
            print(f"\nJobs for {skill}:\n")
            job_results = fetch_jobs(skill)
            if job_results:
                for j in job_results:
                    print(f"Title- {j['title']}\n Company- {j['company']}\n Apply Link- ({j['link']})\n")
            else:
                print("No jobs found")    
    else:
        print("No file selected.")