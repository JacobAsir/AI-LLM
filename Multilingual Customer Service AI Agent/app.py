import streamlit as st
import groq
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="Multilingual AI Helper (POC)",
    page_icon="🌐",
    layout="centered"
)

# Groq API client setup
def get_groq_response(prompt, model_name="llama3-8b-8192"):
    """
    Get a response from the Groq API

    Args:
        prompt (str): The prompt to send to the model
        model_name (str): The model to use (default: llama3-8b-8192)

    Returns:
        str: The generated text response
    """
    try:
        # Get API key from environment variable
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Error: GROQ_API_KEY not found in environment variables"

        # Initialize Groq client
        client = groq.Client(api_key=api_key)

        # Call the Groq API
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1024,
        )

        # Return the generated text
        return completion.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"

# Initialize session state for conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

if 'analytics' not in st.session_state:
    st.session_state.analytics = {
        'total_queries': 0,
        'english_queries': 0,
        'japanese_queries': 0,
        'avg_response_time': 0,
        'sentiment_stats': {'positive': 0, 'neutral': 0, 'negative': 0}
    }

# Function to analyze sentiment
def analyze_sentiment(text, language):
    """
    Analyze the sentiment of text using Groq

    Args:
        text (str): The text to analyze
        language (str): The language of the text

    Returns:
        str: 'positive', 'neutral', or 'negative'
    """
    sentiment_prompt = f"""
    Analyze the sentiment of the following {language} text and respond with ONLY ONE of these words:
    'positive', 'neutral', or 'negative'.

    Text: "{text}"

    Your response (just one word):
    """

    sentiment = get_groq_response(sentiment_prompt).strip().lower()

    # Ensure we get one of the expected values
    if sentiment not in ['positive', 'neutral', 'negative']:
        sentiment = 'neutral'  # Default to neutral if unexpected response

    return sentiment

# Function to get domain-specific knowledge
def get_domain_knowledge(query, language):
    """
    Retrieve domain-specific knowledge for common customer service queries

    Args:
        query (str): The user's query
        language (str): The language of the query

    Returns:
        str: Domain knowledge if available, empty string otherwise
    """
    # This would ideally connect to a knowledge base or database
    # For this POC, we'll use a simple dictionary with some common questions
    knowledge_base = {
        'business hours': 'Our business hours are Monday to Friday, 9:00 AM to 6:00 PM.',
        '営業時間': '営業時間は月曜日から金曜日の午前9時から午後6時までです。',
        'return policy': 'You can return items within 30 days of purchase with a receipt.',
        '返品ポリシー': '購入から30日以内であれば、レシートがあれば返品可能です。',
        'shipping': 'Standard shipping takes 3-5 business days.',
        '配送': '通常配送は3〜5営業日かかります。'
    }

    # Check if any key phrases are in the query
    for key, value in knowledge_base.items():
        if key.lower() in query.lower():
            # Return the appropriate language version
            if language == 'English' and not key.isascii():
                # Find the English equivalent
                for en_key, en_value in knowledge_base.items():
                    if en_key.isascii() and en_value.isascii() and en_key.lower() in [k.lower() for k in knowledge_base.keys() if not k.isascii()]:
                        return en_value
            elif language == 'Japanese (日本語)' and key.isascii():
                # Find the Japanese equivalent
                for ja_key, ja_value in knowledge_base.items():
                    if not ja_key.isascii() and not ja_value.isascii() and ja_key.lower() in [k.lower() for k in knowledge_base.keys() if k.isascii()]:
                        return ja_value
            else:
                return value

    return ""

# UI Components
st.title("Enterprise Multilingual Customer Service AI")
st.markdown("""
This is an advanced multilingual customer service AI agent for business use.
You can ask questions in English or Japanese, and the AI will respond in your language with context awareness.
""")


# Sidebar for analytics
with st.sidebar:
    st.header("Analytics Dashboard")
    st.metric("Total Queries", st.session_state.analytics['total_queries'])
    st.metric("English Queries", st.session_state.analytics['english_queries'])
    st.metric("Japanese Queries", st.session_state.analytics['japanese_queries'])

    if st.session_state.analytics['total_queries'] > 0:
        st.metric("Avg Response Time", f"{st.session_state.analytics['avg_response_time']:.2f}s")

        # Sentiment breakdown
        st.subheader("Sentiment Analysis")
        sentiment_data = st.session_state.analytics['sentiment_stats']
        st.write(f"Positive: {sentiment_data['positive']}")
        st.write(f"Neutral: {sentiment_data['neutral']}")
        st.write(f"Negative: {sentiment_data['negative']}")


# Language selection
user_language = st.selectbox(
    "Select your language:",
    ["English", "Japanese (日本語)"]
)

# Business domain selection
business_domain = st.selectbox(
    "Business Domain:",
    ["E-commerce", "Banking", "Travel", "Technology Support"]
)

# Query input
user_query = st.text_area(
    "Type your question here:",
    height=100,
    placeholder="e.g., 'What are your business hours?' or '営業時間は何時ですか？'"
)

# Display conversation history
if st.session_state.conversation_history:
    st.subheader("Conversation History")
    for i, (role, text, lang) in enumerate(st.session_state.conversation_history):
        if role == "user":
            st.markdown(f"**You ({lang}):** {text}")
        else:
            st.markdown(f"**AI:** {text}")
    st.markdown("---")


# Submit button
if st.button("Ask AI"):
    if not user_query:
        st.error("Please enter a question.")
    else:
        # Update analytics
        st.session_state.analytics['total_queries'] += 1
        if user_language == "English":
            st.session_state.analytics['english_queries'] += 1
        else:
            st.session_state.analytics['japanese_queries'] += 1

        # Add user message to conversation history
        st.session_state.conversation_history.append(("user", user_query, user_language))

        # Process the query
        start_time = time.time()

        with st.spinner("AI is thinking..."):
            # Analyze sentiment of the query
            query_sentiment = analyze_sentiment(user_query, "English" if user_language == "English" else "Japanese")
            st.session_state.analytics['sentiment_stats'][query_sentiment] += 1

            # Check for domain-specific knowledge
            domain_knowledge = get_domain_knowledge(user_query, user_language)

            # Step 1: Handle input based on selected language
            if user_language == "English":
                # Translate English to Japanese
                translation_prompt = f"Translate the following English text to simple, polite Japanese: '{user_query}'"
                japanese_query = get_groq_response(translation_prompt)
            else:
                # No translation needed for Japanese input
                japanese_query = user_query

            # Step 2: Generate response in Japanese with proper politeness
            # Include conversation history for context
            conversation_context = ""
            if len(st.session_state.conversation_history) > 1:
                conversation_context = "Previous conversation:\n"
                # Get the last 3 exchanges (or fewer if not available)
                for i in range(max(0, len(st.session_state.conversation_history)-6), len(st.session_state.conversation_history)-1):
                    role, text, lang = st.session_state.conversation_history[i]
                    conversation_context += f"{role}: {text}\n"

            agent_prompt = f"""
            You are a helpful customer assistant for a {business_domain} company providing information.
            Embody basic Omotenashi: be polite, welcoming, and concise.
            Always respond in polite Japanese (Teineigo style - using です/ます). Keep sentences relatively simple.
            Do not use overly casual or complex honorifics.

            {conversation_context}

            The user's query is: "{japanese_query}"
            The sentiment of their query is: {query_sentiment}

            {f'Based on our knowledge base: {domain_knowledge}' if domain_knowledge else ''}

            Generate a helpful and polite response in Japanese based on the query.
            If the sentiment is negative, be especially empathetic and apologetic.
            If they are asking about something specific to our business, use the knowledge provided.
            """

            # Use a more capable model for the main response
            japanese_response = get_groq_response(agent_prompt, model_name="llama3-70b-8192")

            # Step 3: Translate response if needed
            if user_language == "English":
                # Translate Japanese response back to English
                translation_prompt = f"Translate the following Japanese text to English: '{japanese_response}'"
                final_response = get_groq_response(translation_prompt)
            else:
                # No translation needed for Japanese output
                final_response = japanese_response

            # Calculate response time and update analytics
            response_time = time.time() - start_time
            current_avg = st.session_state.analytics['avg_response_time']
            total_queries = st.session_state.analytics['total_queries']
            st.session_state.analytics['avg_response_time'] = ((current_avg * (total_queries - 1)) + response_time) / total_queries

            # Add AI response to conversation history
            st.session_state.conversation_history.append(("ai", final_response, user_language))

            # Display the response
            st.markdown("### AI Response:")
            st.markdown(final_response)

            # Optional: Show debug information in an expander
            with st.expander("Show Processing Details"):
                st.markdown(f"**Query Sentiment:** {query_sentiment}")
                st.markdown(f"**Response Time:** {response_time:.2f} seconds")
                st.markdown("**Japanese Query:**")
                st.markdown(f"```\n{japanese_query}\n```")
                st.markdown("**Japanese Response:**")
                st.markdown(f"```\n{japanese_response}\n```")
                if domain_knowledge:
                    st.markdown("**Domain Knowledge Used:**")
                    st.markdown(f"```\n{domain_knowledge}\n```")

# Footer
st.markdown("---")
st.markdown("Multilingual Customer Service AI Agent - Proof of Concept")
