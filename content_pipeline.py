import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

from scraper import WebScraper
from groq_processor import GroqContentProcessor
from email_sender import EmailSender
from youtube_processor import YouTubeTranscriptProcessor
from twitter_processor import TwitterProcessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ContentPipeline:
    def __init__(self, 
                 groq_api_key: Optional[str] = None,
                 resend_api_key: Optional[str] = None,
                 from_email: Optional[str] = None):
        """
        Initialize the content pipeline.
        
        Args:
            groq_api_key: Groq API key
            resend_api_key: Resend API key
            from_email: Sender email address
        """
        self.scraper = WebScraper(delay=1.0)
        try:
            self.processor = GroqContentProcessor(api_key=groq_api_key)
            logger.info("GroqContentProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GroqContentProcessor: {e}")
            raise
        
        # Create YouTube processor with proxy support
        proxy_url = os.getenv('YOUTUBE_PROXY_URL')
        proxy_config = YouTubeTranscriptProcessor.create_proxy_config(proxy_url)
        self.youtube_processor = YouTubeTranscriptProcessor(proxy_config=proxy_config)
        
        # Create Twitter processor
        self.twitter_processor = TwitterProcessor()
        
        self.email_sender = EmailSender(api_key=resend_api_key)
        
        if from_email:
            self.email_sender.from_email = from_email
    
    def process_urls(self, 
                    urls: List[str], 
                    email_recipients: List[str] = None,
                    digest_title: str = "Content Digest",
                    writing_style: str = "professional",
                    force_fresh: bool = False) -> Dict[str, any]:
        """
        Process a list of URLs through the complete pipeline.
        
        Args:
            urls: List of URLs to process
            email_recipients: List of email recipients
            digest_title: Title for the digest
            writing_style: Writing style to use (professional, casual, technical, or custom)
            force_fresh: If True, bypass cache and fetch fresh content
            
        Returns:
            Dictionary containing results and status
        """
        try:
            logger.info(f"Starting content pipeline with {len(urls)} URLs")
            
            # Step 1: Scrape content from URLs with freshness control
            logger.info("Step 1: Scraping content from URLs...")
            articles = self.scraper.scrape_multiple_urls(urls, force_fresh=force_fresh)
            logger.info(f"Retrieved {len(articles)} articles")
            
            # Sort articles by publish date or scrape date for freshness
            logger.info("Sorting articles by freshness...")
            articles = self._sort_articles_by_freshness(articles)
            
            if not articles:
                return {
                    "success": False,
                    "error": "No articles were successfully scraped",
                    "articles": []
                }
            
            # Step 2: Process articles with Groq LLM
            logger.info("Step 2: Processing articles with Groq LLM...")
            processed_articles = self.processor.process_multiple_articles(articles)
            logger.info(f"Processed {len(processed_articles)} articles")
            
            # Step 3: Create digest
            logger.info("Step 3: Creating content digest...")
            digest_content = self.processor.create_digest(processed_articles, digest_title, writing_style)
            
            # Step 4: Send email
            if email_recipients:
                logger.info("Step 4: Sending email digest...")
                email_response = self.email_sender.send_content_digest(
                    content=digest_content,
                    subject=f"{digest_title} - {datetime.now().strftime('%B %d, %Y')}",
                    to_emails=email_recipients
                )
                
                if "error" in email_response:
                    logger.warning(f"Email sending failed: {email_response['error']}")
            else:
                logger.info("Step 4: No email recipients specified, skipping email sending")
                email_response = {"message": "No email recipients specified"}
            
            return {
                "success": True,
                "articles": processed_articles,
                "digest_content": digest_content,
                "email_response": email_response,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "articles": []
            }
    
    def process_rss_feeds(self, 
                         rss_urls: List[str], 
                         max_items_per_feed: int = 5,
                         email_recipients: List[str] = None,
                         digest_title: str = "RSS Feed Digest",
                         writing_style: str = "professional") -> Dict[str, any]:
        """
        Process RSS feeds through the complete pipeline.
        
        Args:
            rss_urls: List of RSS feed URLs
            max_items_per_feed: Maximum items to process per feed
            email_recipients: List of email recipients
            digest_title: Title for the digest
            writing_style: Writing style to use (professional, casual, technical, or custom)
            
        Returns:
            Dictionary containing results and status
        """
        try:
            logger.info(f"Starting RSS pipeline with {len(rss_urls)} feeds")
            
            # Step 1: Scrape RSS feeds
            logger.info("Step 1: Scraping RSS feeds...")
            all_articles = []
            for rss_url in rss_urls:
                articles = self.scraper.scrape_rss_feed(rss_url, max_items_per_feed)
                all_articles.extend(articles)
                logger.info(f"Scraped {len(articles)} articles from {rss_url}")
            
            if not all_articles:
                return {
                    "success": False,
                    "error": "No articles were successfully scraped from RSS feeds",
                    "articles": []
                }
            
            # Step 2: Process articles with Groq LLM
            logger.info("Step 2: Processing articles with Groq LLM...")
            processed_articles = self.processor.process_multiple_articles(all_articles)
            logger.info(f"Processed {len(processed_articles)} articles")
            
            # Step 3: Create digest
            logger.info("Step 3: Creating RSS digest...")
            digest_content = self.processor.create_digest(processed_articles, digest_title, writing_style)
            
            # Step 4: Send email
            if email_recipients:
                logger.info("Step 4: Sending email digest...")
                email_response = self.email_sender.send_content_digest(
                    content=digest_content,
                    subject=f"{digest_title} - {datetime.now().strftime('%B %d, %Y')}",
                    to_emails=email_recipients
                )
                
                if "error" in email_response:
                    logger.warning(f"Email sending failed: {email_response['error']}")
            else:
                logger.info("Step 4: No email recipients specified, skipping email sending")
                email_response = {"message": "No email recipients specified"}
            
            return {
                "success": True,
                "articles": processed_articles,
                "digest_content": digest_content,
                "email_response": email_response,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RSS pipeline error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "articles": []
            }
    
    def process_youtube_urls(self, 
                           youtube_urls: List[str], 
                           email_recipients: List[str] = None,
                           digest_title: str = "YouTube Transcript Digest",
                           writing_style: str = "professional") -> Dict[str, any]:
        """
        Process YouTube URLs and extract transcripts with enhanced content generation.
        
        Args:
            youtube_urls: List of YouTube URLs to process
            email_recipients: List of email recipients
            digest_title: Title for the digest
            writing_style: Writing style to use (professional, casual, technical, or custom)
            
        Returns:
            Dictionary containing results and status
        """
        try:
            logger.info(f"Starting enhanced YouTube transcript pipeline with {len(youtube_urls)} URLs")
            
            # Step 1: Extract transcripts from YouTube videos
            logger.info("Step 1: Extracting YouTube transcripts...")
            youtube_articles = self.youtube_processor.process_youtube_urls(youtube_urls)
            logger.info(f"Extracted {len(youtube_articles)} YouTube transcripts")
            
            if not youtube_articles:
                logger.warning("No YouTube articles were processed - this could be due to transcript extraction failures or missing API keys")
                return {
                    "success": False,
                    "error": "No YouTube content was successfully processed. This could be due to transcript extraction failures, missing YouTube Data API key, or IP blocking restrictions.",
                    "articles": []
                }
            
            # Step 2: Enhance YouTube content with educational insights
            logger.info("Step 2: Enhancing YouTube content with educational insights...")
            enhanced_articles = self._enhance_youtube_content(youtube_articles)
            logger.info(f"Enhanced {len(enhanced_articles)} YouTube articles")
            
            # Step 3: Process articles with specialized Groq LLM prompts
            logger.info("Step 3: Processing enhanced YouTube content with Groq LLM...")
            processed_articles = self._process_youtube_articles_with_specialized_prompts(enhanced_articles)
            logger.info(f"Processed {len(processed_articles)} YouTube articles")
            
            # Step 4: Create specialized digest for educational content
            logger.info("Step 4: Creating specialized YouTube digest...")
            if writing_style == "professional":
                digest_content = self._create_educational_digest(processed_articles, digest_title)
            else:
                digest_content = self.processor.create_digest(processed_articles, digest_title, writing_style)
            
            # Step 5: Send email
            if email_recipients:
                logger.info("Step 5: Sending email digest...")
                email_response = self.email_sender.send_content_digest(
                    content=digest_content,
                    subject=f"{digest_title} - {datetime.now().strftime('%B %d, %Y')}",
                    to_emails=email_recipients
                )
                
                if "error" in email_response:
                    logger.warning(f"Email sending failed: {email_response['error']}")
            else:
                logger.info("Step 5: No email recipients specified, skipping email sending")
                email_response = {"message": "No email recipients specified"}
            
            return {
                "success": True,
                "articles": processed_articles,
                "digest_content": digest_content,
                "email_response": email_response,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"YouTube pipeline error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "articles": []
            }
    
    def _enhance_youtube_content(self, youtube_articles: List[Dict]) -> List[Dict]:
        """
        Enhance YouTube content with educational insights and metadata.
        
        Args:
            youtube_articles: List of YouTube articles to enhance
            
        Returns:
            List of enhanced articles with educational metadata
        """
        enhanced_articles = []
        
        for article in youtube_articles:
            enhanced_article = article.copy()
            
            # Extract video metadata
            video_id = article.get('video_id', '')
            duration = article.get('duration', 0)
            language = article.get('language', 'en')
            snippet_count = article.get('snippet_count', 0)
            
            # Add educational metadata
            enhanced_article['educational_metadata'] = {
                'video_id': video_id,
                'duration_minutes': round(duration / 60, 2) if duration else 0,
                'language': language,
                'transcript_segments': snippet_count,
                'content_type': 'educational_video',
                'processing_timestamp': datetime.now().isoformat()
            }
            
            # Detect content type based on title and content
            title = article.get('title', '').lower()
            content = article.get('content', '').lower()
            
            content_type = self._detect_educational_content_type(title, content)
            enhanced_article['educational_metadata']['detected_type'] = content_type
            
            # Extract key concepts and formulas
            key_concepts = self._extract_key_concepts(content)
            enhanced_article['educational_metadata']['key_concepts'] = key_concepts
            
            # Extract visual elements mentioned
            visual_elements = self._extract_visual_elements(content)
            enhanced_article['educational_metadata']['visual_elements'] = visual_elements
            
            # Extract teaching methods
            teaching_methods = self._extract_teaching_methods(content)
            enhanced_article['educational_metadata']['teaching_methods'] = teaching_methods
            
            enhanced_articles.append(enhanced_article)
        
        return enhanced_articles
    
    def _detect_educational_content_type(self, title: str, content: str) -> str:
        """Detect the type of educational content based on title and content."""
        # Mathematical content indicators
        math_indicators = ['formula', 'equation', 'theorem', 'proof', 'mathematical', 'calculus', 
                          'algebra', 'geometry', 'trigonometry', 'statistics', 'probability']
        
        # Science content indicators
        science_indicators = ['physics', 'chemistry', 'biology', 'experiment', 'scientific', 
                             'research', 'hypothesis', 'theory', 'molecule', 'atom']
        
        # Programming/CS content indicators
        cs_indicators = ['programming', 'coding', 'algorithm', 'data structure', 'software', 
                        'computer science', 'python', 'javascript', 'machine learning', 'ai']
        
        # Visual/Art content indicators
        art_indicators = ['visual', 'design', 'art', 'creative', 'drawing', 'painting', 
                         'animation', 'graphics', 'illustration']
        
        combined_text = f"{title} {content}"
        
        if any(indicator in combined_text for indicator in math_indicators):
            return 'mathematics'
        elif any(indicator in combined_text for indicator in science_indicators):
            return 'science'
        elif any(indicator in combined_text for indicator in cs_indicators):
            return 'computer_science'
        elif any(indicator in combined_text for indicator in art_indicators):
            return 'visual_arts'
        else:
            return 'general_education'
    
    def _extract_key_concepts(self, content: str) -> List[str]:
        """Extract key concepts from video content."""
        # This is a simplified version - in production, you'd use NLP libraries
        concepts = []
        
        # Look for mathematical formulas and concepts
        import re
        
        # Mathematical formulas
        formulas = re.findall(r'[A-Za-z]+\s*[=<>]+\s*[A-Za-z0-9+\-*/^()]+', content)
        concepts.extend(formulas[:5])  # Limit to 5 formulas
        
        # Technical terms (simplified detection)
        technical_terms = re.findall(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', content)
        concepts.extend(technical_terms[:10])  # Limit to 10 terms
        
        return list(set(concepts))  # Remove duplicates
    
    def _extract_visual_elements(self, content: str) -> List[str]:
        """Extract visual elements mentioned in the content."""
        visual_keywords = ['diagram', 'chart', 'graph', 'visualization', 'animation', 
                          'illustration', 'figure', 'plot', 'image', 'picture']
        
        visual_elements = []
        for keyword in visual_keywords:
            if keyword in content.lower():
                visual_elements.append(keyword)
        
        return visual_elements
    
    def _extract_teaching_methods(self, content: str) -> List[str]:
        """Extract teaching methods used in the content."""
        teaching_keywords = ['analogy', 'example', 'demonstration', 'step-by-step', 
                           'explanation', 'tutorial', 'guide', 'walkthrough', 'breakdown']
        
        teaching_methods = []
        for keyword in teaching_keywords:
            if keyword in content.lower():
                teaching_methods.append(keyword)
        
        return teaching_methods
    
    def _sort_articles_by_freshness(self, articles: List[Dict]) -> List[Dict]:
        """Sort articles by publish date or scrape date for freshness."""
        
        def get_article_date(article: Dict) -> datetime:
            """Get the most relevant date for an article."""
            try:
                # Try publish date first
                if article.get('publish_date'):
                    try:
                        # Try parsing the publish date
                        return datetime.fromisoformat(article['publish_date'].replace('Z', '+00:00'))
                    except:
                        pass
                
                # Fall back to scrape date
                if article.get('scraped_at'):
                    return datetime.fromisoformat(article['scraped_at'].replace('Z', '+00:00'))
                
                # Last resort: current time
                return datetime.now()
            except:
                return datetime.now()
        
        # Sort articles by date, newest first
        return sorted(articles, key=get_article_date, reverse=True)
    
    def _process_youtube_articles_with_specialized_prompts(self, enhanced_articles: List[Dict]) -> List[Dict]:
        """
        Process YouTube articles with specialized prompts for educational content.
        
        Args:
            enhanced_articles: List of enhanced YouTube articles
            
        Returns:
            List of processed articles with educational insights
        """
        processed_articles = []
        
        for article in enhanced_articles:
            # Create specialized prompt based on content type
            content_type = article['educational_metadata'].get('detected_type', 'general_education')
            specialized_prompt = self._create_specialized_prompt(content_type, article)
            
            # Process with specialized prompt
            try:
                # Use the existing processor but with specialized prompt
                processed_article = self.processor.process_single_article_with_prompt(
                    article, specialized_prompt
                )
                processed_articles.append(processed_article)
            except Exception as e:
                logger.warning(f"Specialized processing failed for {article.get('url', '')}: {e}")
                # Fallback to standard processing
                processed_article = self.processor.process_single_article(article)
                processed_articles.append(processed_article)
        
        return processed_articles
    
    def _create_specialized_prompt(self, content_type: str, article: Dict) -> str:
        """Create specialized prompt based on content type."""
        base_prompt = """
        Analyze this educational video content and create a comprehensive summary that includes:
        
        1. **Key Learning Objectives**: What are the main concepts being taught?
        2. **Mathematical/Technical Content**: Extract and explain any formulas, equations, or technical concepts
        3. **Visual Learning Elements**: Describe any visual explanations, analogies, or demonstrations
        4. **Teaching Methodology**: How does the instructor explain complex concepts?
        5. **Practical Applications**: What are the real-world applications of these concepts?
        6. **Learning Insights**: What makes this explanation effective for learning?
        7. **Key Takeaways**: What should learners remember from this content?
        """
        
        if content_type == 'mathematics':
            specialized_prompt = base_prompt + """
            
            **MATHEMATICS FOCUS**:
            - Extract and explain all mathematical formulas and equations
            - Identify the mathematical concepts being taught
            - Explain the step-by-step problem-solving approach
            - Highlight visual representations of mathematical concepts
            - Connect abstract concepts to concrete examples
            """
        elif content_type == 'science':
            specialized_prompt = base_prompt + """
            
            **SCIENCE FOCUS**:
            - Explain scientific principles and theories
            - Identify experimental methods and observations
            - Connect concepts to real-world phenomena
            - Highlight the scientific method used
            - Explain cause-and-effect relationships
            """
        elif content_type == 'computer_science':
            specialized_prompt = base_prompt + """
            
            **COMPUTER SCIENCE FOCUS**:
            - Explain algorithms and data structures
            - Identify programming concepts and patterns
            - Highlight practical implementation details
            - Connect theory to code examples
            - Explain computational thinking approaches
            """
        else:
            specialized_prompt = base_prompt
        
        return specialized_prompt
    
    def _create_educational_digest(self, processed_articles: List[Dict], digest_title: str) -> str:
        """
        Create a specialized digest for educational content.
        
        Args:
            processed_articles: List of processed articles
            digest_title: Title for the digest
            
        Returns:
            Formatted digest content
        """
        if not processed_articles:
            return "No educational content available."
        
        # Group articles by content type
        content_groups = {}
        for article in processed_articles:
            content_type = article.get('educational_metadata', {}).get('detected_type', 'general_education')
            if content_type not in content_groups:
                content_groups[content_type] = []
            content_groups[content_type].append(article)
        
        # Create specialized digest
        digest_parts = []
        
        # Header
        digest_parts.append(f"# {digest_title}")
        digest_parts.append(f"**Date**: {datetime.now().strftime('%B %d, %Y')}")
        digest_parts.append(f"**Total Videos**: {len(processed_articles)}")
        digest_parts.append("")
        
        # Content type sections
        for content_type, articles in content_groups.items():
            type_name = content_type.replace('_', ' ').title()
            digest_parts.append(f"## {type_name} Content")
            digest_parts.append("")
            
            for i, article in enumerate(articles, 1):
                title = article.get('title', f'Video {i}')
                url = article.get('url', '')
                summary = article.get('summary', '')
                
                digest_parts.append(f"### {i}. {title}")
                digest_parts.append(f"**URL**: {url}")
                digest_parts.append("")
                
                if summary:
                    digest_parts.append(summary)
                    digest_parts.append("")
                
                # Add educational metadata
                metadata = article.get('educational_metadata', {})
                if metadata:
                    digest_parts.append("**Educational Insights:**")
                    
                    key_concepts = metadata.get('key_concepts', [])
                    if key_concepts:
                        digest_parts.append(f"- **Key Concepts**: {', '.join(key_concepts[:5])}")
                    
                    visual_elements = metadata.get('visual_elements', [])
                    if visual_elements:
                        digest_parts.append(f"- **Visual Elements**: {', '.join(visual_elements)}")
                    
                    teaching_methods = metadata.get('teaching_methods', [])
                    if teaching_methods:
                        digest_parts.append(f"- **Teaching Methods**: {', '.join(teaching_methods)}")
                    
                    duration = metadata.get('duration_minutes', 0)
                    if duration:
                        digest_parts.append(f"- **Duration**: {duration} minutes")
                    
                    digest_parts.append("")
        
        # Overall insights
        digest_parts.append("## Overall Educational Insights")
        digest_parts.append("")
        digest_parts.append("This collection of educational content covers a diverse range of topics and teaching methods. The content demonstrates effective use of visual learning, step-by-step explanations, and practical applications to make complex concepts accessible.")
        digest_parts.append("")
        
        # Learning recommendations
        digest_parts.append("## Learning Recommendations")
        digest_parts.append("")
        digest_parts.append("- **For Students**: Focus on understanding the underlying concepts rather than memorizing formulas")
        digest_parts.append("- **For Educators**: Use visual analogies and step-by-step breakdowns to explain complex topics")
        digest_parts.append("- **For Professionals**: Apply these concepts to real-world problems and projects")
        digest_parts.append("")
        
        return "\n".join(digest_parts)
    
    def process_mixed_sources(self, 
                             urls: List[str] = None,
                             rss_urls: List[str] = None,
                             youtube_urls: List[str] = None,
                             twitter_urls: List[str] = None,
                             max_rss_items: int = 5,
                             email_recipients: List[str] = None,
                             digest_title: str = "Mixed Content Digest",
                             writing_style: str = "professional",
                             force_fresh: bool = True) -> Dict[str, any]:
        """
        Process URLs, RSS feeds, YouTube videos, and Twitter sources in a single pipeline.
        
        Args:
            urls: List of URLs to process
            rss_urls: List of RSS feed URLs
            youtube_urls: List of YouTube URLs to process
            twitter_urls: List of Twitter URLs to process
            max_rss_items: Maximum items to process per RSS feed
            email_recipients: List of email recipients
            digest_title: Title for the digest
            writing_style: Writing style to use (professional, casual, technical, or custom)
            
        Returns:
            Dictionary containing results and status
        """
        try:
            logger.info("Starting mixed content pipeline")
            
            all_articles = []
            
            # Process URLs if provided
            if urls:
                logger.info(f"Processing {len(urls)} URLs...")
                url_articles = self.scraper.scrape_multiple_urls(urls, force_fresh=force_fresh)
                all_articles.extend(url_articles)
                content_state = "fresh" if force_fresh else "latest available"
                logger.info(f"Retrieved {len(url_articles)} {content_state} articles from URLs")
            
            # Process RSS feeds if provided
            if rss_urls:
                logger.info(f"Processing {len(rss_urls)} RSS feeds...")
                for rss_url in rss_urls:
                    rss_articles = self.scraper.scrape_rss_feed(rss_url, max_rss_items, force_fresh=force_fresh)
                    all_articles.extend(rss_articles)
                    content_state = "fresh" if force_fresh else "latest available"
                    logger.info(f"Retrieved {len(rss_articles)} {content_state} articles from {rss_url}")
            
            # Process YouTube URLs if provided
            if youtube_urls:
                logger.info(f"Processing {len(youtube_urls)} YouTube URLs...")
                
                # Separate individual videos from channels
                individual_videos = []
                channel_urls = []
                
                for url in youtube_urls:
                    if self.youtube_processor.is_youtube_channel(url):
                        channel_urls.append(url)
                    else:
                        individual_videos.append(url)
                
                # Process individual videos
                if individual_videos:
                    logger.info(f"Processing {len(individual_videos)} individual YouTube videos...")
                    youtube_articles = self.youtube_processor.process_youtube_urls(individual_videos)
                    all_articles.extend(youtube_articles)
                    logger.info(f"Extracted {len(youtube_articles)} YouTube transcripts from individual videos")
                
                # Process channels (get latest videos)
                if channel_urls:
                    logger.info(f"Processing {len(channel_urls)} YouTube channels...")
                    
                    # Get YouTube Data API key from environment
                    youtube_api_key = os.getenv('YOUTUBE_DATA_API_KEY')
                    
                if not youtube_api_key:
                    logger.warning("YOUTUBE_DATA_API_KEY not found in environment variables")
                    logger.info("To fetch latest videos from channels, set YOUTUBE_DATA_API_KEY environment variable")
                    logger.info("Individual YouTube video URLs will still work, but channel processing requires the API key")
                else:
                    for channel_url in channel_urls:
                        logger.info(f"Fetching latest videos from channel: {channel_url}")
                        latest_videos = self.youtube_processor.get_channel_latest_videos(
                            channel_url, 
                            max_videos=3, 
                            api_key=youtube_api_key
                        )
                        
                        if latest_videos:
                            logger.info(f"Found {len(latest_videos)} videos from {channel_url}")
                            # Process the latest videos as individual videos
                            channel_articles = self.youtube_processor.process_youtube_urls(latest_videos)
                            all_articles.extend(channel_articles)
                            logger.info(f"Extracted {len(channel_articles)} YouTube transcripts from channel videos")
                        else:
                            logger.warning(f"No videos found for channel: {channel_url}")
            
            # Process Twitter URLs if provided
            if twitter_urls:
                logger.info(f"Processing {len(twitter_urls)} Twitter sources...")
                twitter_articles = self.twitter_processor.process_twitter_sources(twitter_urls)
                all_articles.extend(twitter_articles)
                logger.info(f"Processed {len(twitter_articles)} Twitter sources")
            
            if not all_articles:
                error_details = []
                if urls:
                    error_details.append(f"Web scraping: {len(urls)} URLs")
                if rss_urls:
                    error_details.append(f"RSS feeds: {len(rss_urls)} feeds")
                if youtube_urls:
                    error_details.append(f"YouTube videos: {len(youtube_urls)} videos")
                if twitter_urls:
                    error_details.append(f"Twitter sources: {len(twitter_urls)} sources")
                
                return {
                    "success": False,
                    "error": f"No articles were successfully scraped from {', '.join(error_details)}",
                    "articles": []
                }
            
            # Process all articles with Groq LLM
            logger.info("Processing all articles with Groq LLM...")
            processed_articles = self.processor.process_multiple_articles(all_articles)
            logger.info(f"Processed {len(processed_articles)} articles")

            # Content persistence disabled
            saved = 0
            logger.info("Content persistence disabled")
            
            # Create digest
            logger.info("Creating mixed content digest...")
            digest_content = self.processor.create_digest(processed_articles, digest_title, writing_style)
            
            # Send email
            if email_recipients:
                logger.info("Sending email digest...")
                email_response = self.email_sender.send_content_digest(
                    content=digest_content,
                    subject=f"{digest_title} - {datetime.now().strftime('%B %d, %Y')}",
                    to_emails=email_recipients
                )
                
                if "error" in email_response:
                    logger.warning(f"Email sending failed: {email_response['error']}")
            else:
                logger.info("No email recipients specified, skipping email sending")
                email_response = {"message": "No email recipients specified"}
            
            return {
                "success": True,
                "articles": processed_articles,
                "digest_content": digest_content,
                "email_response": email_response,
                "saved_count": saved,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Mixed pipeline error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "articles": []
            }
    
    def save_results(self, results: Dict[str, any], filename: str = None) -> str:
        """
        Save pipeline results to a JSON file.
        
        Args:
            results: Pipeline results dictionary
            filename: Output filename (optional)
            
        Returns:
            Path to saved file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"content_pipeline_results_{timestamp}.json"
        
        # Remove non-serializable content for JSON
        json_results = results.copy()
        if 'digest_content' in json_results:
            # Keep only first 1000 chars of digest for JSON
            json_results['digest_content'] = json_results['digest_content'][:1000] + "..."
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(json_results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {filename}")
        return filename

# Example usage
if __name__ == "__main__":
    # Example configuration
    urls = [
        "https://example.com",
        "https://news.ycombinator.com"
    ]
    
    rss_urls = [
        "https://feeds.bbci.co.uk/news/rss.xml",
        "https://rss.cnn.com/rss/edition.rss"
    ]
    
    # Test email (replace with actual email for testing)
    test_emails = ["test@example.com"]
    
    try:
        # Initialize pipeline
        pipeline = ContentPipeline()
        
        # Process mixed sources
        results = pipeline.process_mixed_sources(
            urls=urls,
            rss_urls=rss_urls,
            max_rss_items=3,
            email_recipients=test_emails,
            digest_title="Test Content Digest"
        )
        
        if results["success"]:
            print("Pipeline completed successfully!")
            print(f"Processed {len(results['articles'])} articles")
            
            # Save results
            filename = pipeline.save_results(results)
            print(f"Results saved to {filename}")
        else:
            print(f"Pipeline failed: {results['error']}")
            
    except Exception as e:
        print(f"Error: {e}")
        print("Please check your API keys and configuration.")
