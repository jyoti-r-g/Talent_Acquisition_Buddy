# Talent Acquisition Buddy

A Streamlit-based web application designed to help recruiters and Talent Acquisition professionals streamline their hiring process. It automatically extracts keywords from Job Descriptions, allows priority scoring, analyzes resumes, extracts contact details, and uses AI to generate personalized cover letters and outreach emails.

## Prerequisites

Before running this project, ensure you have the following installed:
- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/)

You will also need a **Google Gemini API Key**.

## Setup Instructions

### 1. Clone the repository
Open your terminal or command prompt and run:
`bash
git clone https://github.com/jyoti-r-g/Talent_Acquisition_Buddy.git
cd Talent_Acquisition_Buddy
`

### 2. Set up a Virtual Environment
It is highly recommended to use a virtual environment to manage dependencies.

**On Windows:**
`bash
python -m venv venv
venv\Scripts\activate
`

**On macOS/Linux:**
`bash
python3 -m venv venv
source venv/bin/activate
`

### 3. Install Dependencies
Install all required Python libraries from the `requirements.txt` file:
`bash
pip install -r requirements.txt
`

### 4. Set up Environment Variables
The application requires API keys to function properly, particularly for Google Gemini AI.

1. Create a `.env` file in the root folder.
2. Open the `.env` file and add your Gemini API Key:
`env
GOOGLE_API_KEY="your_api_key_here"
`

*(Note: Never upload your `.env` file to version control. It is already included in the `.gitignore`)*

### 5. Run the Application
Start the Streamlit web server by running the following command:

`bash
streamlit run app.py
`

This will open your default web browser and launch the "Talent Acquisition Buddy" app. Usually, it's accessible at `http://localhost:8501`.

## Usage Guide
1. **Upload Files:** Upload a Job Description (JD) and a batch of candidate Resumes (supports PDF/DOCX).
2. **Set Keyword Priorities:** The app will extract key requirements from the JD. You can manually categorize them into High, Medium, or Low priority.
3. **Process & Analyze:** The app will parse resumes, extract details (Email, Phone, Location), and rank candidates using a weighted score against your prioritized JD keywords.
4. **Generate AI Responses:** The app automatically generates custom cover letters and outreach emails using Gemini.
5. **Download Results:** Export the final ranked candidate list into an Excel file for your records.
