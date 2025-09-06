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


1. Clone the repository
---bash
git clone <your-repo-link>
cd <your-repo-folder>

2. Install dependencies
---bash
pip install -r requirements.txt

3. Initialize the data base of the webpage
---bash
   python init_db.py

4. Insert required (domains) database
---bash
   python seed_domains.py
   
6. Run the app
--bash
python app.py

7. Open in browser
cpp
http://127.0.0.1:5000




