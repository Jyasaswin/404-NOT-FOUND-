import pdfplumber

SKILLS_DB = [
    "Python", "Java", "C++", "JavaScript", "HTML", "CSS",
    "SQL", "Machine Learning", "Data Analysis", "React",
    "Django", "Flask", "AWS", "Git"
]

def extract_skills(file_path):
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"
    except:
        return ""

    text_lower = text.lower()
    extracted = [skill for skill in SKILLS_DB if skill.lower() in text_lower]
    return ", ".join(extracted)
