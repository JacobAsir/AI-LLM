"""
Main application for the content creation multi-agent system.
"""
import os
import logging
import json
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Import LLM
from langchain_groq import ChatGroq

# Note: CrewAI imports are commented out due to AgentOps integration issues
# from crewai import Crew, Task, Agent

from agents.trend_searcher import TrendSearcher
from agents.content_creator import ContentCreator
from utils.monitoring import AgentOpsMonitoring
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("content_creation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def setup_llm():
    """
    Set up the language model.

    Returns:
        Configured LLM
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        logger.warning("Using placeholder Groq API key. This will cause authentication errors when making API calls.")
        logger.warning("Please set a valid GROQ_API_KEY in your .env file.")

    try:
        return ChatGroq(
            groq_api_key=api_key,
            model_name=config.LLM_MODEL,
            temperature=0.7,
            max_tokens=4096
        )
    except Exception as e:
        logger.error(f"Error setting up LLM: {e}")
        raise

def setup_monitoring():
    """
    Set up AgentOps monitoring.

    Returns:
        Configured monitoring instance
    """
    api_key = os.getenv("AGENTOPS_API_KEY")
    if not api_key:
        logger.warning("AGENTOPS_API_KEY environment variable not set, monitoring will be disabled")
        return None

    return AgentOpsMonitoring(api_key=api_key, project_name="content_creation_agents")

def save_content(content: Dict[str, Any], output_dir: str = "output"):
    """
    Save generated content to a file.

    Args:
        content: Content to save
        output_dir: Directory to save content to
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    title_slug = content['title'].lower().replace(' ', '_').replace('/', '_').replace('\\', '_')
    filename = f"{timestamp}_{title_slug}.json"
    filepath = os.path.join(output_dir, filename)

    # Save content to file
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2)

    logger.info(f"Content saved to {filepath}")

    # Also save a text version for easy reading
    text_filepath = os.path.join(output_dir, f"{timestamp}_{title_slug}.txt")
    with open(text_filepath, 'w', encoding='utf-8') as f:
        f.write(f"Title: {content['title']}\n\n")
        f.write(content['content'])

    logger.info(f"Text version saved to {text_filepath}")

def main():
    """
    Main function to run the content creation multi-agent system.
    """
    logger.info("Starting content creation multi-agent system")

    try:
        # Setup LLM
        llm = setup_llm()
        logger.info(f"LLM setup complete using model: {config.LLM_MODEL}")

        # Setup monitoring
        monitoring = setup_monitoring()
        if monitoring and monitoring.initialized:
            monitoring.start_session(
                session_name=f"content_creation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                metadata={"model": config.LLM_MODEL}
            )

        # Initialize agents
        trend_searcher = TrendSearcher(llm)
        content_creator = ContentCreator(llm)
        logger.info("Agents initialized")

        # Create CrewAI tasks
        search_task = Task(
            description="Search for trending topics on the internet",
            agent=trend_searcher.agent,
            expected_output="A list of trending topics with details",
            async_execution=False
        )

        create_task = Task(
            description="Create high-quality content based on trending topics",
            agent=content_creator.agent,
            expected_output="Engaging content articles on trending topics",
            async_execution=False
        )

        # Note: We're skipping CrewAI execution due to AgentOps integration issues
        # Instead, we'll directly use our agent implementations

        # Log start of process
        if monitoring and monitoring.initialized:
            monitoring.log_agent_action(
                agent_name="system",
                action_type="process_start",
                inputs={},
                outputs={},
                metadata={"timestamp": datetime.now().isoformat()}
            )

        # Execute the process directly
        logger.info("Starting direct execution (skipping CrewAI)")

        # For direct execution without CrewAI process orchestration, uncomment the following:
        # Search for trending topics
        logger.info("Starting direct trend search")
        categories = config.CONTENT_CATEGORIES
        selected_category = categories[0]  # Default to first category

        if monitoring and monitoring.initialized:
            monitoring.log_agent_action(
                agent_name="trend_searcher",
                action_type="search_start",
                inputs={"category": selected_category},
                outputs={},
                metadata={"timestamp": datetime.now().isoformat()}
            )

        trending_topics = trend_searcher.search_trending_topics(
            category=selected_category,
            max_topics=config.MAX_TRENDING_TOPICS
        )

        if monitoring and monitoring.initialized:
            monitoring.log_agent_action(
                agent_name="trend_searcher",
                action_type="search_complete",
                inputs={"category": selected_category},
                outputs={"topics_count": len(trending_topics)},
                metadata={"timestamp": datetime.now().isoformat()}
            )

        logger.info(f"Found {len(trending_topics)} trending topics")

        # Create content for each topic
        for i, topic in enumerate(trending_topics):
            logger.info(f"Creating content for topic {i+1}/{len(trending_topics)}: {topic['title']}")

            if monitoring and monitoring.initialized:
                monitoring.log_agent_action(
                    agent_name="content_creator",
                    action_type="creation_start",
                    inputs={"topic": topic['title']},
                    outputs={},
                    metadata={"timestamp": datetime.now().isoformat()}
                )

            content = content_creator.create_content(
                topic=topic,
                content_type="article",
                tone="informative",
                target_audience="general"
            )

            if monitoring and monitoring.initialized:
                monitoring.log_agent_action(
                    agent_name="content_creator",
                    action_type="creation_complete",
                    inputs={"topic": topic['title']},
                    outputs={"word_count": content['word_count']},
                    metadata={"timestamp": datetime.now().isoformat()}
                )

            # Save the content
            save_content(content)

        # End monitoring session
        if monitoring and monitoring.initialized:
            monitoring.end_session(
                status="completed",
                metadata={"topics_processed": len(trending_topics)}
            )

        logger.info("Content creation process completed successfully")

    except Exception as e:
        logger.error(f"Error in content creation process: {e}", exc_info=True)

        # End monitoring session with error status
        if monitoring and monitoring.initialized:
            monitoring.end_session(
                status="failed",
                metadata={"error": str(e)}
            )

if __name__ == "__main__":
    main()
