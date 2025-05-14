"""
Trend Searcher Agent - Searches the web for trending topics.
"""
from crewai import Agent
from langchain_groq import ChatGroq
from typing import List, Dict, Any
import logging
import random
from utils.web_utils import fetch_webpage, extract_trending_topics_from_google_trends, search_web_for_topic
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendSearcher:
    """
    Agent responsible for searching the web for trending topics.
    """
    
    def __init__(self, llm):
        """
        Initialize the TrendSearcher agent.
        
        Args:
            llm: Language model to use for the agent
        """
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        Create the CrewAI agent for trend searching.
        
        Returns:
            CrewAI Agent
        """
        return Agent(
            role="Trend Research Specialist",
            goal="Find the most engaging and relevant trending topics on the internet",
            backstory="""You are an expert at identifying trending topics across various platforms.
            Your specialty is finding topics that are gaining momentum and have potential for creating
            engaging content. You have a keen eye for distinguishing between fleeting trends and
            topics with staying power.""",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
    
    def search_trending_topics(self, category: str = None, max_topics: int = 5) -> List[Dict[str, Any]]:
        """
        Search for trending topics, optionally filtered by category.
        
        Args:
            category: Optional category to filter topics
            max_topics: Maximum number of topics to return
            
        Returns:
            List of trending topics with details
        """
        logger.info(f"Searching for trending topics{' in ' + category if category else ''}")
        
        all_topics = []
        
        # Fetch from multiple sources
        for source_url in config.TRENDING_SOURCES:
            try:
                html_content = fetch_webpage(source_url)
                if "google.com/trends" in source_url:
                    topics = extract_trending_topics_from_google_trends(html_content)
                    all_topics.extend(topics)
            except Exception as e:
                logger.error(f"Error fetching trends from {source_url}: {e}")
        
        # If no topics found, create some generic ones for demonstration
        if not all_topics:
            logger.warning("No topics found from sources, using fallback topics")
            all_topics = self._generate_fallback_topics()
        
        # Filter by category if specified
        if category:
            filtered_topics = []
            for topic in all_topics:
                # Use the LLM to determine if the topic belongs to the category
                topic_text = f"{topic['title']}. {topic.get('description', '')}"
                is_relevant = self._is_topic_relevant_to_category(topic_text, category)
                if is_relevant:
                    filtered_topics.append(topic)
            all_topics = filtered_topics
        
        # Limit to max_topics
        selected_topics = all_topics[:max_topics]
        
        # Enrich topics with additional information
        enriched_topics = self._enrich_topics(selected_topics)
        
        return enriched_topics
    
    def _generate_fallback_topics(self) -> List[Dict[str, Any]]:
        """
        Generate fallback topics when no topics are found from sources.
        
        Returns:
            List of fallback topics
        """
        fallback_topics = [
            {"title": "Advances in Artificial Intelligence", "description": "Recent breakthroughs in AI technology and their implications"},
            {"title": "Climate Change Initiatives", "description": "New policies and technologies addressing climate change"},
            {"title": "Space Exploration Updates", "description": "Latest developments in space missions and discoveries"},
            {"title": "Cryptocurrency Market Trends", "description": "Current movements in the cryptocurrency market"},
            {"title": "Health and Wellness Innovations", "description": "New approaches to health, fitness, and mental wellbeing"},
        ]
        return fallback_topics
    
    def _is_topic_relevant_to_category(self, topic_text: str, category: str) -> bool:
        """
        Use the LLM to determine if a topic is relevant to a category.
        
        Args:
            topic_text: Text describing the topic
            category: Category to check relevance against
            
        Returns:
            True if the topic is relevant to the category, False otherwise
        """
        prompt = f"""
        Determine if the following topic is relevant to the category '{category}':
        
        Topic: {topic_text}
        
        Answer with only 'yes' or 'no'.
        """
        
        try:
            response = self.llm.invoke(prompt).content.strip().lower()
            return response == "yes"
        except Exception as e:
            logger.error(f"Error determining topic relevance: {e}")
            # Default to including the topic if there's an error
            return True
    
    def _enrich_topics(self, topics: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich topics with additional information.
        
        Args:
            topics: List of topics to enrich
            
        Returns:
            List of enriched topics
        """
        enriched_topics = []
        
        for topic in topics:
            try:
                # Get additional information about the topic
                search_results = search_web_for_topic(topic['title'])
                
                # Extract key points using the LLM
                key_points = self._extract_key_points(topic['title'], search_results)
                
                enriched_topic = {
                    **topic,
                    "search_results": search_results,
                    "key_points": key_points
                }
                
                enriched_topics.append(enriched_topic)
            except Exception as e:
                logger.error(f"Error enriching topic {topic['title']}: {e}")
                # Include the original topic if enrichment fails
                enriched_topics.append(topic)
        
        return enriched_topics
    
    def _extract_key_points(self, topic_title: str, search_results: List[Dict[str, Any]]) -> List[str]:
        """
        Extract key points about a topic using the LLM.
        
        Args:
            topic_title: Title of the topic
            search_results: Search results about the topic
            
        Returns:
            List of key points about the topic
        """
        # Combine search result snippets
        combined_text = "\n".join([result.get('snippet', '') for result in search_results if 'snippet' in result])
        
        prompt = f"""
        Based on the following information about "{topic_title}", extract 3-5 key points that would be important for creating content on this topic:
        
        {combined_text}
        
        Format each key point as a separate bullet point.
        """
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            
            # Parse bullet points
            key_points = []
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    key_points.append(line.lstrip('•-* '))
            
            return key_points
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return ["No key points available due to processing error"]
