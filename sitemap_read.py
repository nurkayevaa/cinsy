import os
import streamlit as st
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from io import BytesIO

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
        pdf_reader = PdfReader(BytesIO(response.content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

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
        st.write(data)
        st.download_button(
            "Download as CSV",
            data=convert_to_csv(data),
            file_name="extracted_data.csv",
            mime="text/csv",
        )

# Helper function to convert data to CSV
def convert_to_csv(data):
    import pandas as pd
    df = pd.DataFrame(data)
    return df.to_csv(index=False)
