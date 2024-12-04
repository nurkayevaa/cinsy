import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import streamlit as st
import pandas as pd
import io

# Helper function to fetch sitemap content from a URL
def fetch_sitemap(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Error fetching sitemap: {e}")
        return None

# Helper function to extract URLs from sitemap content
def extract_urls_from_sitemap(sitemap_content):
    try:
        # Use 'lxml' parser to handle XML content
        soup = BeautifulSoup(sitemap_content, "lxml")
        urls = [loc.text for loc in soup.find_all("loc")]
        return urls
    except Exception as e:
        st.error(f"Error parsing sitemap: {e}")
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

# Helper function to extract text from a PDF (without using tempfile)
def extract_text_from_pdf(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Read PDF content directly into memory using BytesIO
        pdf_file = io.BytesIO(response.content)
        pdf_reader = PdfReader(pdf_file)

        # Extract text from the PDF
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()

        return text
    except Exception as e:
        return f"Error extracting text from PDF: {e}"

# Helper function to convert data to CSV
def convert_to_csv(data):
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

# Main Streamlit App
st.title("Sitemap Web Page and PDF Text Extractor")

# Define the sitemap URL
sitemap_url = "https://raw.githubusercontent.com/nurkayevaa/cinsy/refs/heads/main/sitemap_public_services_only.xml"
st.markdown(f"Sitemap URL: `{sitemap_url}`")

# Fetch and parse the sitemap
sitemap_content = fetch_sitemap(sitemap_url)
if sitemap_content:
    urls = extract_urls_from_sitemap(sitemap_content)
    
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
                data.append({"Link": url, "Text": text[:500]})  # Limit text to 500 characters for display

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
