import pdfplumber # type: ignore
from PyPDF2 import PdfReader
import re

SKILLS_DB = [
    "C", "C++", "C#", "Java", "Python", "JavaScript", "TypeScript", "Go", "Rust", "Kotlin", 
    "Swift", "Ruby", "PHP", "Perl", "R", "MATLAB", "Scala", "Dart", "Objective-C", 
    "Shell", "Bash", "PowerShell", "Assembly",

    "HTML", "CSS", "SASS", "TailwindCSS", "Bootstrap", "React", "Angular", "Vue.js", 
    "Next.js", "Nuxt.js", "Node.js", "Express.js", "Django", "Flask", "FastAPI", 
    "Spring", "ASP.NET", "Laravel",

    "SQL", "MySQL", "PostgreSQL", "SQLite", "OracleDB", "MongoDB", "Firebase", 
    "Redis", "Cassandra", "Elasticsearch", "DynamoDB",

    "Machine Learning", "Deep Learning", "Artificial Intelligence", "Data Analysis", 
    "Data Mining", "Computer Vision", "NLP", "Generative AI", "RAG", "LLMs",
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "OpenCV", "HuggingFace", 
    "LangChain", "Pandas", "NumPy", "Matplotlib", "Seaborn", "Statsmodels",

    "AWS", "GCP", "Azure", "Docker", "Kubernetes", "Jenkins", "CI/CD", "Terraform", 
    "Ansible", "Git", "GitHub", "GitLab", "Bitbucket", "Linux", "Shell Scripting",

    "React Native", "Flutter", "Swift", "Kotlin", "Android SDK", "iOS SDK",

    "Cryptography", "Network Security", "Penetration Testing", "Ethical Hacking", 
    "Metasploit", "Burp Suite", "Wireshark",

    "REST API", "GraphQL", "WebSockets", "Microservices", "OOP", 
    "Functional Programming", "Agile", "Scrum", "Design Patterns", 
    "Software Architecture", "Testing", "Selenium", "Cypress", "JUnit", "PyTest"
]


# SECTION_HEADERS = ["projects"]
# EXPERIENCE_HEADERS = ["experience", "work experience", "internship", "professional experience"]
# STOP_HEADERS = ["education", "skills", "technical skills", "certifications", "awards","achievements & awards","leadership & volunteer experience","projects","experience", "work experience", "internship", "professional experience"]

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_skills(file_path):
    text = extract_text_from_pdf(file_path)
    text_lower = text.lower()
    extracted = [skill for skill in SKILLS_DB if skill.lower() in text_lower]
    return ", ".join(extracted)

# def extract_section(pdf_path, headers, stop_headers):
#     text = extract_text_from_pdf(pdf_path)
#     text_lower = text.lower()
#     for header in headers:
#         match = re.search(header, text_lower)
#         if match:
#             start = match.end()
#             stop = len(text)
#             for stop_header in stop_headers:
#                 stop_match = re.search(stop_header, text_lower[start:])
#                 if stop_match:
#                     stop = start + stop_match.start()
#                     break
#             snippet = text[start:stop]
#             lines = re.split(r"[\n•\-]", snippet)
#             results = []
#             for line in lines:
#                 line = line.strip()
#                 if len(line) > 10 and not any(h in line.lower() for h in headers):
#                     results.append(line)
#             return results
#     return []

# def extract_projects(pdf_path):
#     return extract_section(pdf_path, SECTION_HEADERS, STOP_HEADERS)

# def extract_experiences(pdf_path):
#     return extract_section(pdf_path, EXPERIENCE_HEADERS, STOP_HEADERS)
