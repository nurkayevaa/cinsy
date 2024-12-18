import streamlit as st
import pandas as pd
import openai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Access the secret
api_key = st.secrets["OPENAI_API_KEY"]

# Configure OpenAI
openai.api_key = api_key

# Set up the Streamlit page layout
st.set_page_config(page_title="Chatbot with CSV Data", page_icon="🤖", layout="wide")
st.title("Chatbot with CSV Data")

# Load and cache the CSV
@st.cache_data
def load_csv(url):
    return pd.read_csv(url)

csv_url = "https://raw.githubusercontent.com/nurkayevaa/cinsy/refs/heads/main/extracted_data.csv"
try:
    data = load_csv(csv_url)
    st.success("CSV file loaded successfully!")
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

# Ensure required columns are present
if "link" not in data.columns or "text" not in data.columns:
    st.error("The CSV file must contain 'link' and 'text' columns.")
    st.stop()

# Function to get embeddings for texts
@st.cache_data
def get_embeddings(texts):
    try:
        response = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=texts,
        )
        return [embedding["embedding"] for embedding in response["data"]]
    except Exception as e:
        st.error(f"Error getting embeddings: {e}")
        st.stop()

# Precompute embeddings for the dataset
with st.spinner("Generating embeddings for the dataset..."):
    data["embeddings"] = get_embeddings(data["text"].dropna().tolist())

# Function to find the most relevant context using embeddings
def find_relevant_context(question, embeddings, top_n=3):
    try:
        question_embedding = get_embeddings([question])[0]
        similarities = cosine_similarity([question_embedding], embeddings).flatten()
        top_indices = similarities.argsort()[-top_n:][::-1]
        relevant_data = [
            {"link": data["link"].iloc[i], "text": data["text"].iloc[i]}
            for i in top_indices if similarities[i] > 0
        ]
        return relevant_data
    except Exception as e:
        st.error(f"Error finding relevant context: {e}")
        return []

# Function to generate a chatbot response
def generate_response(question, context):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant trained on a dataset."},
                {"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return f"Error generating response: {e}"

# Initialize conversation history
if "history" not in st.session_state:
    st.session_state.history = []

# Main Chat Interface
st.markdown("### Chat with the Assistant")
question = st.text_area("Type your question:", height=100)

if question:
    with st.spinner("Finding relevant context..."):
        relevant_contexts = find_relevant_context(
            question, np.vstack(data["embeddings"].dropna())
        )

    if relevant_contexts:
        context_summary = " ".join([f"Link: {item['link']}, Text: {item['text'][:200]}..." for item in relevant_contexts])

        with st.spinner("Generating response..."):
            answer = generate_response(question, context_summary)

        # Add to conversation history
        st.session_state.history.append({"question": question, "answer": answer})

        # Display the response
        st.markdown("#### Response")
        st.write(answer)
    else:
        st.warning("No relevant context found in the dataset.")

# Display chat-like conversation history
def display_chat():
    st.markdown("### Chat History")
    for entry in st.session_state.history:
        st.markdown(f"""
        <div style="text-align: left; background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <strong>You:</strong><br>{entry['question']}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: left; background-color: #d3e4f5; padding: 10px; border-radius: 5px; margin: 5px 0;">
            <strong>Assistant:</strong><br>{entry['answer']}
        </div>
        """, unsafe_allow_html=True)

display_chat()

# Hide Streamlit default footer
st.markdown("<style> .css-1d391g3 { display: none; } </style>", unsafe_allow_html=True)
