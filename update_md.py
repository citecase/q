import pandas as pd
import requests
from io import StringIO

# URL of your published Google Sheet in CSV format
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTbuiw7kYMTHrOmgjV_A8kDEx3BHnRjUwjjw9i_sVG-BXch7Bq515zH6R5ywuNMQ0rN1YJzgGZz5vAU/pub?output=csv"

def update_markdown():
    # Download data
    response = requests.get(SHEET_CSV_URL)
    if response.status_code == 200:
        # Read CSV data
        df = pd.read_csv(StringIO(response.text))
        
        # Convert to Markdown
        md_content = "# Spreadsheet Data\n\n"
        md_content += df.to_markdown(index=False)
        
        # Save to file
        with open("data.md", "w", encoding="utf-8") as f:
            f.write(md_content)
        print("Markdown file updated successfully.")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    update_markdown()
