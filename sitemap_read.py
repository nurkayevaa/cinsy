import streamlit as st
import pandas as pd
import openai

# Access the secret
api_key = st.secrets["OPENAI_API_KEY"]

# Configure OpenAI
openai.api_key = api_key

st.set_page_config(page_title="Chatbot with CSV Data", page_icon="🤖")
st.title("Chatbot with CSV Data")

# Load CSV
csv_url = "https://raw.githubusercontent.com/nurkayevaa/cinsy/refs/heads/main/extracted_data.csv"
try:
    data = pd.read_csv(csv_url)
    st.success("CSV file loaded successfully!")
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

if "link" not in data.columns or "text" not in data.columns:
    st.error("The CSV file must contain 'link' and 'text' columns.")
    st.stop()

st.markdown("### Ask a Question")
question = st.text_input("Enter your question:")

def generate_response(question, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error generating response: {e}"

if question:
    # Filter rows based on question and limit context
    filtered_data = data[data["text"].str.contains(question, case=False, na=False)]
    limited_context = " ".join(filtered_data["text"].tolist()[:10])  # Use top 10 rows

    with st.spinner("Generating response..."):
        answer = generate_response(question, limited_context)
    st.markdown("### Response")
    st.write(answer)
