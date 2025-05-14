# Content Creation Multi-Agent System

A multi-agent system for automated content creation using CrewAI, AgentOps, and Groq's LLaMA Versatile model.

## Overview

This system consists of two agents:
1. **Trend Searcher Agent**: Searches the web for trending topics
2. **Content Creator Agent**: Creates high-quality content based on trending topics

The system is built using:
- [CrewAI](https://github.com/joaomdmoura/crewAI) for the multi-agent framework
- [AgentOps](https://github.com/AgentOps-AI/agentops) for monitoring and observability
- [Groq](https://groq.com/) for LLM inference using the LLaMA Versatile model

## Project Structure

```
.
├── agents/
│   ├── trend_searcher.py     # Trend Searcher Agent
│   └── content_creator.py    # Content Creator Agent
├── utils/
│   ├── web_utils.py          # Web scraping utilities
│   └── monitoring.py         # AgentOps monitoring utilities
├── output/                   # Generated content output directory
├── .env                      # Environment variables (create from .env.example)
├── .env.example              # Example environment variables
├── config.py                 # Configuration settings
├── main.py                   # Main application entry point
├── requirements.txt          # Required packages
└── README.md                 # This file
```

## Setup

1. Clone the repository
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file from `.env.example` and add your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   AGENTOPS_API_KEY=your_agentops_api_key_here
   ```

## Usage

Run the main application:

```
python main.py
```

The system will:
1. Search for trending topics in the configured categories
2. Create content for each trending topic
3. Save the generated content to the `output` directory

## Configuration

You can configure the system by modifying `config.py`:

- `LLM_MODEL`: The Groq LLM model to use
- `MAX_TRENDING_TOPICS`: Maximum number of trending topics to retrieve
- `CONTENT_MIN_WORDS` and `CONTENT_MAX_WORDS`: Word count limits for generated content
- `TRENDING_SOURCES`: Web sources for trending topics
- `CONTENT_CATEGORIES`: Categories for content creation

## Monitoring

The system uses AgentOps for monitoring and observability. You can view the monitoring data in the AgentOps dashboard.

## License

[MIT License](LICENSE)
