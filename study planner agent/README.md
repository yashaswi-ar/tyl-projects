# Study Planner Agent

An AI-based study planning assistant that creates personalized study schedules based on a student's available study time, subjects, workload, exam date, and completed modules.

## Features

- Collects student details and study preferences
- Creates a personalized study plan
- Supports VTU 2022 Scheme subjects
- Considers subject credits and workload
- Takes daily available study hours into account
- Tracks completed/studied modules
- Calculates the remaining days before the exam
- Generates a 7-day study plan when no exam date is provided
- Provides revision-focused planning before exams
- Avoids introducing new topics during the final revision period

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- AI-based planning logic

## Project Structure

```text
study planner agent/
├── backend/
│   └── app.py
├── frontend/
│   ├── index.html
│   ├── script.js
│   └── style.css
├── .env.example
├── README.md
├── requirements.txt
└── study_planner.py

## Development Environment
Visual Studio Code


How It Works
The student provides their study details and preferences.
The agent considers available study hours, subjects, workload, credits, completed modules, and exam date.
It calculates the available preparation period.
It generates a personalized study schedule.
If no exam date is provided, a 7-day study plan is generated.
Before the examination, the plan focuses on revision and avoids introducing new topics during the final revision period.
Running the Project

Install Dependencies
pip install -r requirements.txt
Run the Backend
python backend/app.py

Open the Frontend
Open frontend/index.html in a web browser.

Purpose

The Study Planner Agent demonstrates how AI-based planning logic can be used to create personalized study schedules according to individual student requirements and examination timelines.