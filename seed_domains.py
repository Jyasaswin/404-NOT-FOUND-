import sqlite3

domains = [
    ("Web Development", "HTML,CSS,JavaScript,React,Node.js,SQL"),
    ("Data Science", "Python,Statistics,Machine Learning,SQL,Pandas,Numpy"),
    ("AI/ML", "Python,TensorFlow,PyTorch,Deep Learning,NLP"),
    ("Cybersecurity", "Networking,Linux,Cryptography,Ethical Hacking"),
    ("Mobile Development", "Java,Kotlin,Flutter,Swift,React Native")
]

conn = sqlite3.connect("users.db")
cur = conn.cursor()
cur.executemany("INSERT INTO domains (name, required_skills) VALUES (?, ?)", domains)
conn.commit()
conn.close()
print("Domains inserted ✅")
