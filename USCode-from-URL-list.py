import re
import requests
import pandas as pd
import PyPDF2
from io import BytesIO
import time
import random

# Pattern to detect U.S. Code citations (e.g., "Title 5, Section 552")
US_CODE_PATTERN = re.compile(r'\bTitle\s*\d+,\s*Section\s*\d+\b', re.IGNORECASE)

def extract_us_code_citations(pdf_text):
    """Extract unique U.S. Code citations from the text of a PDF."""
    citations = set(re.findall(US_CODE_PATTERN, pdf_text))
    return list(citations)

def download_pdf_text(url, session, retries=3, timeout=30):
    """Download PDF from a URL and return its text content if successful."""
    for attempt in range(retries):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
            }
            response = session.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Check for successful download
            pdf_reader = PyPDF2.PdfReader(BytesIO(response.content))
            pdf_text = ""
            for page in pdf_reader.pages:
                pdf_text += page.extract_text() or ""
            return pdf_text
        except (requests.RequestException, PyPDF2.errors.PdfReadError) as e:
            print(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(random.uniform(2, 5))  # Random delay before retrying
    print(f"All {retries} attempts failed for {url}")
    return ""

def main():
    # Input and output file names
    input_file = 'url-list.xlsx'
    output_file = 'USCode-from-URL-list.xlsx'
    
    # Load the URL list from the Excel file
    df = pd.read_excel(input_file)
    urls = df['URL'].dropna().tolist()  # Ensure no empty URLs
    
    # Initialize list to store results
    results = []
    
    # Create a session to handle cookies and headers
    with requests.Session() as session:
        # Process each URL
        for url in urls:
            print(f"Processing {url}")
            
            # Random delay to mimic human browsing behavior
            time.sleep(random.uniform(5, 10))
            
            pdf_text = download_pdf_text(url, session)
            
            if pdf_text:
                # Extract U.S. Code citations
                citations = extract_us_code_citations(pdf_text)
                for citation in citations:
                    results.append({'URL': url, 'U.S. Code Citation': citation})
    
    # Convert results to DataFrame and save to Excel
    output_df = pd.DataFrame(results)
    output_df.to_excel(output_file, index=False)
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()