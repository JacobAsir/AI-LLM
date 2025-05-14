"""
Content Creator Agent - Creates content based on trending topics.
"""
from crewai import Agent
from langchain_groq import ChatGroq
from typing import List, Dict, Any, Optional
import logging
import random
import config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentCreator:
    """
    Agent responsible for creating content based on trending topics.
    """
    
    def __init__(self, llm):
        """
        Initialize the ContentCreator agent.
        
        Args:
            llm: Language model to use for the agent
        """
        self.llm = llm
        self.agent = self._create_agent()
    
    def _create_agent(self) -> Agent:
        """
        Create the CrewAI agent for content creation.
        
        Returns:
            CrewAI Agent
        """
        return Agent(
            role="Content Creation Specialist",
            goal="Create engaging, informative, and high-quality content on trending topics",
            backstory="""You are a versatile content creator with expertise in multiple formats and styles.
            You have a talent for crafting compelling narratives that capture audience attention while
            providing valuable information. Your content is known for its clarity, engagement, and
            relevance to current trends.""",
            verbose=True,
            llm=self.llm,
            allow_delegation=False
        )
    
    def create_content(self, 
                       topic: Dict[str, Any], 
                       content_type: str = "article", 
                       tone: str = "informative",
                       target_audience: str = "general",
                       min_words: int = None,
                       max_words: int = None) -> Dict[str, Any]:
        """
        Create content based on a trending topic.
        
        Args:
            topic: Topic information including title, description, and key points
            content_type: Type of content to create (article, social post, etc.)
            tone: Tone of the content (informative, casual, professional, etc.)
            target_audience: Target audience for the content
            min_words: Minimum word count (defaults to config setting)
            max_words: Maximum word count (defaults to config setting)
            
        Returns:
            Dictionary containing the created content and metadata
        """
        min_words = min_words or config.CONTENT_MIN_WORDS
        max_words = max_words or config.CONTENT_MAX_WORDS
        
        logger.info(f"Creating {content_type} content for topic: {topic['title']}")
        
        # Extract topic information
        title = topic['title']
        description = topic.get('description', '')
        key_points = topic.get('key_points', [])
        search_results = topic.get('search_results', [])
        
        # Generate content
        content = self._generate_content(
            title=title,
            description=description,
            key_points=key_points,
            search_results=search_results,
            content_type=content_type,
            tone=tone,
            target_audience=target_audience,
            min_words=min_words,
            max_words=max_words
        )
        
        # Generate metadata
        metadata = self._generate_metadata(title, content, content_type)
        
        return {
            "title": title,
            "content": content,
            "content_type": content_type,
            "tone": tone,
            "target_audience": target_audience,
            "metadata": metadata,
            "word_count": len(content.split()),
            "timestamp": self._get_timestamp()
        }
    
    def _generate_content(self,
                         title: str,
                         description: str,
                         key_points: List[str],
                         search_results: List[Dict[str, Any]],
                         content_type: str,
                         tone: str,
                         target_audience: str,
                         min_words: int,
                         max_words: int) -> str:
        """
        Generate content using the LLM.
        
        Args:
            title: Topic title
            description: Topic description
            key_points: Key points about the topic
            search_results: Search results about the topic
            content_type: Type of content to create
            tone: Tone of the content
            target_audience: Target audience for the content
            min_words: Minimum word count
            max_words: Maximum word count
            
        Returns:
            Generated content
        """
        # Format key points as a string
        key_points_str = "\n".join([f"- {point}" for point in key_points])
        
        # Format search results as a string
        search_results_str = ""
        for result in search_results:
            if 'title' in result and 'snippet' in result:
                search_results_str += f"- {result['title']}: {result['snippet']}\n"
        
        prompt = f"""
        Create {content_type} content about "{title}" with a {tone} tone for a {target_audience} audience.
        
        Topic Description: {description}
        
        Key Points:
        {key_points_str}
        
        Additional Information:
        {search_results_str}
        
        Guidelines:
        - The content should be between {min_words} and {max_words} words
        - Use a {tone} tone throughout
        - Target a {target_audience} audience
        - Format appropriately for a {content_type}
        - Include a compelling headline/title
        - Organize the content with appropriate sections and subheadings
        - Include a strong introduction and conclusion
        
        Create the complete {content_type} now:
        """
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            return response
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error generating content for {title}. Please try again later."
    
    def _generate_metadata(self, title: str, content: str, content_type: str) -> Dict[str, Any]:
        """
        Generate metadata for the content.
        
        Args:
            title: Content title
            content: Generated content
            content_type: Type of content
            
        Returns:
            Dictionary of metadata
        """
        prompt = f"""
        Generate metadata for the following {content_type} titled "{title}".
        
        Based on this content:
        {content[:500]}...
        
        Generate:
        1. A list of 5-7 relevant keywords/tags
        2. A short description (max 150 characters)
        3. SEO title (max 60 characters)
        
        Format your response as:
        Keywords: keyword1, keyword2, keyword3, ...
        Description: your description here
        SEO Title: your SEO title here
        """
        
        try:
            response = self.llm.invoke(prompt).content.strip()
            
            # Parse the response
            metadata = {
                "keywords": [],
                "description": "",
                "seo_title": ""
            }
            
            for line in response.split('\n'):
                line = line.strip()
                if line.startswith('Keywords:'):
                    keywords = line.replace('Keywords:', '').strip()
                    metadata['keywords'] = [k.strip() for k in keywords.split(',')]
                elif line.startswith('Description:'):
                    metadata['description'] = line.replace('Description:', '').strip()
                elif line.startswith('SEO Title:'):
                    metadata['seo_title'] = line.replace('SEO Title:', '').strip()
            
            return metadata
        except Exception as e:
            logger.error(f"Error generating metadata: {e}")
            return {
                "keywords": [title.lower()],
                "description": f"Content about {title}",
                "seo_title": title
            }
    
    def _get_timestamp(self) -> str:
        """
        Get the current timestamp in ISO format.
        
        Returns:
            Current timestamp
        """
        from datetime import datetime
        return datetime.now().isoformat()
