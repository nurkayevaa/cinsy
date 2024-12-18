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

# Function to find the most relevant context based on cosine similarity
def find_relevant_context(question, texts, top_n=3):
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    text_vectors = vectorizer.fit_transform(texts)
    question_vector = vectorizer.transform([question])
    similarities = cosine_similarity(question_vector, text_vectors).flatten()
    top_indices = similarities.argsort()[-top_n:][::-1]
    relevant_data = [
        {"link": data["link"].iloc[i], "text": data["text"].iloc[i]}
        for i in top_indices if similarities[i] > 0
    ]
    return relevant_data

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
    # Find the most relevant links based on cosine similarity
    with st.spinner("Finding relevant context..."):
        relevant_contexts = find_relevant_context(question, data["text"].dropna().tolist())

    if relevant_contexts:
        # Prepare context for the AI
        context_summary = " ".join([f"Link: {item['link']}, Text: {item['text'][:200]}..." for item in relevant_contexts])

        # Generate the response
        with st.spinner("Generating response..."):
            answer = generate_response(question, context_summary)

        # Add to conversation history
        st.session_state.history.append({"question": question, "answer": answer, "context": relevant_contexts})

        # Display the response
        st.markdown("#### Response")
        st.write(answer)

        # Display the relevant context
        st.markdown("#### Relevant Context")
        for item in relevant_contexts:
            st.write(f"- **Link**: [{item['link']}]({item['link']})")
            st.write(f"  **Text**: {item['text'][:200]}...")  # Show a snippet of text
    else:
        st.warning("No relevant context found in the dataset.")

# Display conversation history
st.markdown("### Conversation History")
for entry in st.session_state.history:
    st.write(f"**You**: {entry['question']}")
    st.write(f"**Assistant**: {entry['answer']}")
    st.markdown("**Context:**")
    for item in entry["context"]:
        st.write(f"- **Link**: [{item['link']}]({item['link']})")
        st.write(f"  **Text**: {item['text'][:200]}...")

# Hide Streamlit default footer
st.markdown("<style> .css-1d391g3 { display: none; } </style>", unsafe_allow_html=True)
