# Interview Questions Generator

An AI-powered application that generates interview questions for students using Google's Gemini AI.

## Features

- Generate theoretical or code-based interview questions
- Choose difficulty levels: Easy, Medium, Hard, or Mixed
- Content validation and quality scoring
- Export questions to markdown files
- Download generated content

## Setup

1. Get a Google Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Add your API key to Streamlit secrets (for deployment) or .env file (for local)

## Environment Variables

- `GEMINI_API_KEY`: Your Google Gemini API key

## Usage

1. Enter the topic for your interview questions
2. Select question type (Theoretical or Code-based)
3. Choose difficulty level
4. Set number of questions to generate
5. Click "Generate Questions"
6. Review validation results and download the file

## Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Live Demo

[Your Streamlit App URL will be here after deployment]
