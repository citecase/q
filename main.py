import os
import requests
import google.generativeai as genai

# Configuration
# The Doc ID is extracted from your URL: 1_NzJj5qisdbWigMdc53kt9ddjs7z4XwQdaG2UzCdQWs
DOC_ID = "1_NzJj5qisdbWigMdc53kt9ddjs7z4XwQdaG2UzCdQWs"
EXPORT_URL = f"https://docs.google.com/document/d/{DOC_ID}/export?format=txt"

def fetch_doc_content():
    """Fetches the plain text content of the Google Doc."""
    try:
        response = requests.get(EXPORT_URL)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching document: {e}")
        return None

def generate_questions(content):
    """Uses Gemini API to generate legal questions based on the doc content."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return

    genai.configure(api_key=api_key)
    
    # Using the free gemini-pro model
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Based on the following legal text containing case summaries and interpretations of Indian law (BNSS, Industrial Disputes Act, Constitution of India, etc.), 
    please generate a comprehensive list of all possible legal questions (and their answers/references) that could arise from these points. 
    Focus on clarity, legal nuance, and specific article/section references mentioned in the text.
    
    TEXT CONTENT:
    {content}
    """
    
    try:
        response = model.generate_content(prompt)
        print("--- GENERATED LEGAL QUESTIONS ---")
        print(response.text)
        
        # Optional: Save to a local file in the repo (GitHub can commit this back if needed)
        with open("daily_questions.md", "w", encoding="utf-8") as f:
            f.write(response.text)
            
    except Exception as e:
        print(f"Error calling Gemini API: {e}")

if __name__ == "__main__":
    print("Starting daily legal question generation...")
    text = fetch_doc_content()
    if text:
        generate_questions(text)
    else:
        print("Failed to retrieve content.")
