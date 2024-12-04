import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import tempfile
import pandas as pd

# Helper function to read the sitemap and extract URLs
def extract_urls_from_sitemap(sitemap_path):
    try:
        with open(sitemap_path, "r") as file:
            sitemap_content = file.read()
        soup = BeautifulSoup(sitemap_content, "xml")
        urls = [loc.text for loc in soup.find_all("loc")]
        return urls
    except Exception as e:
        st.error(f"Error reading sitemap: {e}")
        return []

# Helper function to extract text from a web page
def extract_text_from_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        return soup.get_text(strip=True)
    except Exception as e:
        return f"Error extracting text: {e}"

# Helper function to extract text from a PDF
def extract_text_from_pdf(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Save PDF temporarily to file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf_path = temp_pdf.name

        # Extract text from the temporary PDF file
        text = ""
        pdf_reader = PdfReader(temp_pdf_path)
        for page in pdf_reader.pages:
            text += page.extract_text()

        # Delete the temporary file
        os.remove(temp_pdf_path)
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

# Helper function to convert data to CSV
def convert_to_csv(data):
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

# Main Streamlit App
st.title("Sitemap Web Page and PDF Text Extractor")

# Input file path for the sitemap
sitemap_path = os.path.expanduser("~/sitemap_public_services_only.xml")
st.markdown(f"Sitemap File Path: `{sitemap_path}`")

# Check if sitemap file exists
if not os.path.exists(sitemap_path):
    st.error("Sitemap file not found in the home directory. Please ensure the file exists.")
else:
    # Extract URLs from the sitemap
    urls = extract_urls_from_sitemap(sitemap_path)
    
    if not urls:
        st.error("No URLs found in the sitemap.")
    else:
        st.success(f"Found {len(urls)} URLs in the sitemap.")
        data = []

        # Process each URL
        with st.spinner("Processing URLs..."):
            for url in urls:
                if url.endswith(".pdf"):
                    text = extract_text_from_pdf(url)
                else:
                    text = extract_text_from_webpage(url)
                data.append({"Link": url, "Text": text[:500]})  # Limiting text to 500 chars for display

        # Display results in a table
        st.markdown("### Extracted Text Data")
        st.write(pd.DataFrame(data))

        # Add download button for CSV
        csv_data = convert_to_csv(data)
        st.download_button(
            "Download as CSV",
            data=csv_data,
            file_name="extracted_data.csv",
            mime="text/csv",
        )
