AI Resume Analyzer

An intelligent Applicant Tracking System (ATS) that leverages Google's Gemini AI to analyze candidate resumes against job descriptions.

🚀 Features

PDF Parsing: Automatically extracts text from uploaded PDF resumes.

AI Matching: Uses Gemini 1.5 Flash to compare skills and experience against job requirements.

Database Integration: Securely saves candidate analysis results using SQLite and SQLAlchemy.

Modern UI: Built with Tailwind CSS for a responsive, clean user interface.

🛠️ Tech Stack

Backend: Python, Flask, Flask-SQLAlchemy

Frontend: HTML5, Tailwind CSS, JavaScript

AI Engine: Google Generative AI (Gemini)

Database: SQLite

⚙️ Setup

Clone the repository:

git clone https://github.com/Ishan764/resume_analyzer.git


Create a virtual environment and install dependencies:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


Create a .env file in the root directory and add your API key:

GEMINI_API_KEY="your_actual_key_here"


Run the application:

python3 main.py


🛡️ Security Note

This project utilizes a .gitignore file to ensure sensitive files like .env and venv/ are never committed to version control.
