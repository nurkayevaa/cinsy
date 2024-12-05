import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
import streamlit as st
import pandas as pd
import io
import re

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
        # Use BeautifulSoup to parse the XML content
        soup = BeautifulSoup(sitemap_content, "html.parser")  # Can be "xml" if lxml is installed
        urls = [loc.text for loc in soup.find_all("loc")]
        return urls
    except Exception as e:
        st.error(f"Error parsing sitemap: {e}")
        return []

# Helper function to extract text from a web page, looking for classes with either "main" or "mura"
def extract_text_from_webpage(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        # Find elements with class names that contain either "main" or "mura"
        text_elements = []
        for element in soup.find_all(class_=re.compile(r'.*(main|mura).*', re.IGNORECASE)):
            text_elements.append(element.get_text(strip=True))

        # Join all the text from these elements into a single string
        return " ".join(text_elements) if text_elements else "No relevant text found with class 'main' or 'mura'."
    
    except Exception as e:
        return f"Error extracting text: {e}"

# Helper function to extract text from a PDF
def extract_text_from_pdf(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Read PDF content from response
        text = ""
        pdf_reader = PdfReader(io.BytesIO(response.content))
        for page in pdf_reader.pages:
            text += page.extract_text() or ""

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
                data.append({"Link": url, "Text": text})  # Limit text to 500 characters for display

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
