import streamlit as st
import pandas as pd
import openai
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Access the secret
api_key = st.secrets["OPENAI_API_KEY"]

# Configure OpenAI
openai.api_key = api_key

# Set up the Streamlit page layout
st.set_page_config(page_title="Chatbot with CSV Data", page_icon="🤖", layout="wide")
st.title("Chatbot with CSV Data")

# Load CSV
csv_url = "https://raw.githubusercontent.com/nurkayevaa/cinsy/refs/heads/main/extracted_data.csv"
try:
    data = pd.read_csv(csv_url)
    st.success("CSV file loaded successfully!")
except Exception as e:
    st.error(f"Error loading CSV file: {e}")
    st.stop()

# Ensure required columns are present
if "link" not in data.columns or "text" not in data.columns:
    st.error("The CSV file must contain 'link' and 'text' columns.")
    st.stop()

# Function to find the most relevant context based on cosine similarity
def find_relevant_context(question, texts, top_n=5):
    vectorizer = TfidfVectorizer(stop_words="english")
    text_vectors = vectorizer.fit_transform(texts)  # Fit and transform text column
    question_vector = vectorizer.transform([question])  # Transform the question
    similarities = cosine_similarity(question_vector, text_vectors).flatten()  # Compute cosine similarity
    top_indices = similarities.argsort()[-top_n:][::-1]  # Get top N most similar indices
    relevant_texts = [texts[i] for i in top_indices if similarities[i] > 0]
    return " ".join(relevant_texts), top_indices

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

# Main Chat Interface
st.markdown("### Chat with the Assistant")

question = st.text_area("Type your question:", height=100)

if question:
    # Find the most relevant context
    with st.spinner("Finding relevant context..."):
        relevant_context, relevant_indices = find_relevant_context(question, data["text"].dropna().tolist())
    
    if relevant_context:
        st.markdown("#### Relevant Context")
        st.write(relevant_context)

        # Generate the response
        with st.spinner("Generating response..."):
            answer = generate_response(question, relevant_context)
        
        st.markdown("#### Response")
        st.write(answer)

    else:
        st.warning("No relevant context found in the dataset.")

# To make it more chat-like, clear and centered, you could also include:
st.markdown("<style> .css-1d391g3 { display: none; } </style>", unsafe_allow_html=True)  # Hides Streamlit default footer
