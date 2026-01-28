import os
import time
import google.generativeai as genai
from pathlib import Path

# Setup API Key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("Error: GEMINI_API_KEY not found in environment.")
    exit(1)

genai.configure(api_key=api_key)

# Configuration
INPUT_FOLDER = "judgments"
OUTPUT_FILE = "cases.md"
MODEL_NAME = "gemini-2.5-flash-preview-09-2025"

def process_pdf(file_path):
    """Uploads PDF to Gemini Files API and gets Q&A summary."""
    print(f"Processing: {file_path.name}...")
    
    # Upload the file to Gemini's temporary storage
    sample_file = genai.upload_file(path=str(file_path), mime_type="application/pdf")
    
    # Wait for file to be processed by Google's backend
    while sample_file.state.name == "PROCESSING":
        time.sleep(2)
        sample_file = genai.get_file(sample_file.name)

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction="You are a legal expert. Convert the provided judgment PDF into a detailed Question and Answer format. Include sections for: Facts of the case, Legal Issues, Decision (Ratio), and Final Order."
    )
    
    prompt = f"Please analyze the judgment in {file_path.name} and provide a comprehensive Q&A summary."
    
    # Generate content
    # Note: Using exponential backoff would be safer for production, 
    # but a simple sleep is often enough for 10 files.
    response = model.generate_content([sample_file, prompt])
    
    # Clean up the file from Google's server (optional but good practice)
    genai.delete_file(sample_file.name)
    
    return response.text

def main():
    pdf_path = Path(INPUT_FOLDER)
    if not pdf_path.exists():
        os.makedirs(INPUT_FOLDER)
        print(f"Created {INPUT_FOLDER} folder. Add your PDFs there.")
        return

    # Get list of all PDFs
    files = list(pdf_path.glob("*.pdf"))
    if not files:
        print("No PDF files found.")
        return

    new_content = []
    for file in files:
        try:
            qa_text = process_pdf(file)
            
            # Format the output for cases.md
            entry = f"\n## Judgment Analysis: {file.name}\n"
            entry += f"*Processed on: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
            entry += qa_text
            entry += "\n\n---\n"
            
            new_content.append(entry)
            
            # Sleep to respect free-tier rate limits (RPM)
            time.sleep(10) 
            
        except Exception as e:
            print(f"Failed to process {file.name}: {e}")

    if new_content:
        # Append to cases.md (create if not exists)
        with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
            f.write("\n".join(new_content))
        print(f"Successfully updated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
