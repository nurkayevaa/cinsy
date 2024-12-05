import streamlit as st
import pandas as pd
import openai

# Access the secret
api_key = st.secrets["OPENAI_API_KEY"]

# Configure OpenAI
openai.api_key = api_key

st.set_page_config(
    page_title="home",
    page_icon="👋",
)

# Title of the app
st.title("Chatbot with CSV Data")

# Load the CSV file
csv_url = "https://raw.githubusercontent.com/nurkayevaa/cinsy/refs/heads/main/extracted_data.csv"
st.markdown(f"Using data from: `{csv_url}`")
try:
    data = pd.read_csv(csv_url)
    st.success("CSV file loaded successfully!")
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

# Display data for verification
st.markdown("### Preview of the Data")
st.write(data.head())

# Ensure required columns are present
if "link" not in data.columns or "text" not in data.columns:
    st.error("The CSV file must contain 'link' and 'text' columns.")
    st.stop()

# Function to generate a chatbot response
def generate_response(question, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # You can use 'gpt-3.5-turbo' or 'gpt-4'
            messages=[
                {"role": "system", "content": "You are a helpful assistant who answers based on provided context."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error generating response: {e}"

# Chatbot interface
st.markdown("### Ask a Question")
question = st.text_input("Enter your question:")

if question:
    # Combine text from all rows as the context
    full_context = " ".join(data["text"].dropna().tolist())
    with st.spinner("Generating response..."):
        answer = generate_response(question, full_context)
    st.markdown("### Response")
    st.write(answer)
