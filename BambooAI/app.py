import streamlit as st
import pandas as pd
from bambooai import BambooAI
import json
import os
from dotenv import load_dotenv
load_dotenv()


# API Key Configuration
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

os.environ['LLM_CONFIG'] = '[{"agent": "Expert Selector", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 500, "temperature": 0}},{"agent": "Analyst Selector", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 500, "temperature": 0}},{"agent": "Theorist", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 2000, "temperature": 0}},{"agent": "Planner", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 2000, "temperature": 0}},{"agent": "Code Generator", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 2000, "temperature": 0}},{"agent": "Code Debugger", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 2000, "temperature": 0}},{"agent": "Error Corrector", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 2000, "temperature": 0}},{"agent": "Code Ranker", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 500, "temperature": 0}},{"agent": "Solution Summarizer", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 2000, "temperature": 0}},{"agent": "Google Search Query Generator", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 2000, "temperature": 0}},{"agent": "Google Search Summarizer", "details": {"model": "llama-3.3-70b-versatile", "provider":"groq","max_tokens": 2000, "temperature": 0}}]'

agent_configurations = {
    "Expert Selector": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 500,
        "temperature": 0
    },
    "Analyst Selector": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 500,
        "temperature": 0
    },
    "Theorist": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0
    },
    "Planner": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0
    },
    "Code Generator": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0
    },
    "Code Debugger": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0
    },
    "Error Corrector": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0
    },
    "Code Ranker": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 500,
        "temperature": 0
    },
    "Solution Summarizer": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0
    },
    "Google Search Query Generator": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0
    },
    "Google Search Summarizer": {
        "model": "llama-3.3-70b-versatile",
        "provider": "groq",
        "max_tokens": 2000,
        "temperature": 0
    }
}

# Set LLM_CONFIG to include all agents
os.environ['LLM_CONFIG'] = json.dumps([
    {"agent": agent, "details": details}
    for agent, details in agent_configurations.items()
])

# print("Agent configuration updated successfully!")
# print(os.environ['LLM_CONFIG'])

def main():
    st.set_page_config(page_title="BambooAI Loan Prediction App", layout="wide")
    st.title("BambooAI Agent App")

    # Dataset Upload
    st.header("Upload Your Dataset")
    uploaded_file = st.file_uploader("Upload your dataset (CSV, Excel, or TXT format)", type=["csv", "xlsx", "xls", "txt"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith((".xlsx", ".xls")):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith(".txt"):
                df = pd.read_csv(uploaded_file, delimiter="\t")
            else:
                st.error("Unsupported file format!")
                return

            st.write("### Preview of Uploaded Dataset")
            st.dataframe(df.head())

            # Instantiate BambooAI
            bamboo = BambooAI(df, debug=True, vector_db=False, exploratory=True, search_tool=True)

            # Prompt Input
            st.sidebar.header("Provide a Prompt")
            prompt = st.sidebar.text_area("Write your prompt here:")

            if prompt:
                st.write("### BambooAI in Action")
                with st.spinner("Processing... Please wait"):
                    try:
                        # Execute BambooAI
                        result = bamboo.pd_agent_converse(prompt)

                        # Display Agent Actions
                        st.write("#### Agent's Output:")
                        st.json(result)
                    except Exception as e:
                        st.error(f"An error occurred: {e}")

        except Exception as e:
            st.error(f"Failed to load the dataset: {e}")

    else:
        st.info("Please upload a dataset to get started.")

if __name__ == "__main__":
    main()
