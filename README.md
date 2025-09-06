# Quick Teams

Quick Teams is a web application that helps users form project teams based on skills and domains. It allows users to manage profiles, view and create teams, send and accept invitations, and find teammates with complementary skills for collaborative projects.

## Features

- Create and manage user profiles with skills and domain expertise.
- These skills will be extracted from resume provided by the user.
- Match making will be done by the categorizing the domain based and check the percentage of score he is suitable for the project to contribute.
- View teams and team members along with their skills.
- Send and respond to team invitations.
- Matchmaking feature to find suitable teammates.

## Video demo link
   [link](https://drive.google.com/file/d/15YuRfPvFWqjRaTHJdcXV3GaXP0r2vJss/view?usp=drivesdk)

## Installation


 ```bash
 #Clone the repository
   git clone <your-repo-link>
   cd <your-repo-folder>

 #Install dependencies
   pip install -r requirements.txt

 #Initialize the data base of the webpage
   python init_db.py

 #Insert required (domains) database
   python seed_domains.py
   
 #Run the app
   python app.py

#Open in browser
```cpp
http://127.0.0.1:5000



