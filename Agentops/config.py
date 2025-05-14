"""
Configuration settings for the content creation multi-agent system.
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
AGENTOPS_API_KEY = os.getenv("AGENTOPS_API_KEY")

# LLM Configuration
LLM_MODEL = "llama-3.1-70b-versatile"  # Groq's LLaMA Versatile model

# Agent Configuration
MAX_TRENDING_TOPICS = 5  # Maximum number of trending topics to retrieve
CONTENT_MIN_WORDS = 500  # Minimum word count for generated content
CONTENT_MAX_WORDS = 1000  # Maximum word count for generated content

# Web Sources for Trending Topics
TRENDING_SOURCES = [
    "https://trends.google.com/trends/trendingsearches/daily?geo=US",
    "https://twitter.com/explore/tabs/trending",
    "https://www.reddit.com/r/popular/",
]

# Content Categories
CONTENT_CATEGORIES = [
    "Technology",
    "Business",
    "Health",
    "Entertainment",
    "Science",
    "Sports",
]
