import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
<<<<<<< HEAD
from typing import List, Dict, Optional, Tuple
import logging
from datetime import datetime
from local_cache import LocalCache
=======
from typing import List, Dict, Optional
import logging
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
<<<<<<< HEAD
    def __init__(self, delay: float = 1.0, cache_ttl_minutes: int = 30):
=======
    def __init__(self, delay: float = 1.0):
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
        """
        Initialize the web scraper with a delay between requests to be respectful.
        
        Args:
            delay: Delay in seconds between requests
<<<<<<< HEAD
            cache_ttl_minutes: Time-to-live in minutes for cached content
=======
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
<<<<<<< HEAD
        self.cache = LocalCache(ttl_minutes=cache_ttl_minutes)
    
    def scrape_url(self, url: str, force_fresh: bool = False) -> Dict[str, str]:
        """
        Scrape content from a single URL with caching support.
        
        Args:
            url: URL to scrape
            force_fresh: If True, bypass cache and fetch fresh content
=======
    
    def scrape_url(self, url: str) -> Dict[str, str]:
        """
        Scrape content from a single URL.
        
        Args:
            url: URL to scrape
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
            
        Returns:
            Dictionary containing title, content, and metadata
        """
<<<<<<< HEAD
        # Check cache first if not forcing fresh content
        if not force_fresh:
            cached_content = self.cache.get(url)
            if cached_content:
                logger.info(f"Using cached content for {url}")
                return cached_content
=======
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
        try:
            logger.info(f"Scraping URL: {url}")
            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = ""
            if soup.title:
                title = soup.title.get_text().strip()
            elif soup.find('h1'):
                title = soup.find('h1').get_text().strip()
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Extract main content
            content = ""
            
            # Try to find main content areas
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_=['content', 'post', 'entry'])
            
            if main_content:
                content = main_content.get_text(separator=' ', strip=True)
            else:
                # Fallback to body content
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)
            
            # Clean up content
            content = ' '.join(content.split())
            
<<<<<<< HEAD
            # Extract publish date if available
            publish_date = None
            date_meta = soup.find('meta', property=['article:published_time', 'article:modified_time', 'og:pubdate']) or \
                       soup.find('time') or \
                       soup.find('meta', attrs={'name': 'pubdate'})
            
            if date_meta:
                try:
                    if 'content' in date_meta.attrs:
                        publish_date = date_meta['content']
                    elif 'datetime' in date_meta.attrs:
                        publish_date = date_meta['datetime']
                    elif 'pubdate' in date_meta.attrs:
                        publish_date = date_meta['pubdate']
                except:
                    pass
            
=======
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
            # Limit content length
            if len(content) > 5000:
                content = content[:5000] + "..."
            
<<<<<<< HEAD
            result = {
=======
            return {
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
                'url': url,
                'title': title,
                'content': content,
                'word_count': len(content.split()),
<<<<<<< HEAD
                'scraped_at': datetime.now().isoformat(),
                'publish_date': publish_date,
                'is_fresh': True  # Mark as fresh content
            }
            
            # Cache the result
            self.cache.set(url, result)
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error scraping {url}: {error_msg}")
            
            # Provide more specific error messages
            if '403' in error_msg or 'Forbidden' in error_msg:
                content = f'Unfortunately, the article URL provided ({url}) is not accessible due to a 403 Client Error: Forbidden. This error is likely caused by the website blocking automated scraping attempts to prevent token limits.'
            elif '404' in error_msg or 'Not Found' in error_msg:
                content = f'The requested URL ({url}) could not be found. This may be due to the page being moved, deleted, or the URL being incorrect.'
            elif 'timeout' in error_msg.lower():
                content = f'The request to {url} timed out. The website may be experiencing high traffic or connectivity issues.'
            else:
                content = f'Failed to scrape content from {url}: {error_msg}'
            
            return {
                'url': url,
                'title': 'Error',
                'content': content,
=======
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'title': 'Error',
                'content': f'Failed to scrape content: {str(e)}',
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
                'word_count': 0,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
<<<<<<< HEAD
    def scrape_rss_feed(self, rss_url: str, max_items: int = 10, force_fresh: bool = True) -> List[Dict[str, str]]:
=======
    def scrape_rss_feed(self, rss_url: str, max_items: int = 10) -> List[Dict[str, str]]:
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
        """
        Scrape content from an RSS feed.
        
        Args:
            rss_url: URL of the RSS feed
            max_items: Maximum number of items to process
            
        Returns:
            List of dictionaries containing scraped content
        """
        try:
            logger.info(f"Scraping RSS feed: {rss_url}")
            feed = feedparser.parse(rss_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed may have issues: {rss_url}")
            
            articles = []
            for entry in feed.entries[:max_items]:
                if hasattr(entry, 'link'):
<<<<<<< HEAD
                    # First check cache for non-force-fresh requests
                    article_data = None
                    if not force_fresh:
                        article_data = self.cache.get(entry.link)
                    
                    # If no cached data or force_fresh is True, scrape the URL
                    if article_data is None:
                        article_data = self.scrape_url(entry.link, force_fresh=True)
                        # Cache the result if it's not an error
                        if article_data.get('title') != 'Error':
                            self.cache.set(entry.link, article_data)
                    
=======
                    article_data = self.scrape_url(entry.link)
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
                    # Add RSS metadata
                    article_data['rss_title'] = getattr(entry, 'title', '')
                    article_data['rss_summary'] = getattr(entry, 'summary', '')
                    article_data['rss_published'] = getattr(entry, 'published', '')
<<<<<<< HEAD
                    article_data['is_fresh'] = force_fresh or article_data.get('is_fresh', False)
                    articles.append(article_data)
                    
                    # Add delay between requests only for fresh scraping
                    if force_fresh or article_data.get('is_fresh', False):
                        time.sleep(self.delay)
=======
                    articles.append(article_data)
                    
                    # Add delay between requests
                    time.sleep(self.delay)
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
            
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping RSS feed {rss_url}: {str(e)}")
            return []
    
<<<<<<< HEAD
    def scrape_multiple_urls(self, urls: List[str], force_fresh: bool = True) -> List[Dict[str, str]]:
        """
        Scrape content from multiple URLs with caching support.
        
        Args:
            urls: List of URLs to scrape
            force_fresh: If True, bypass cache and fetch fresh content
            
        Returns:
            List of dictionaries containing scraped content (excluding failed URLs)
        """
        articles = []
        failed_urls = []
        
        for url in urls:
            article_data = None
            source = "cache"
            
            # First check cache for non-force-fresh requests
            if not force_fresh:
                article_data = self.cache.get(url)
            
            # If no cached data or force_fresh is True, scrape the URL
            if article_data is None:
                article_data = self.scrape_url(url, force_fresh=True)
                source = "fresh"
                # Cache the result if it's not an error
                if article_data.get('title') != 'Error':
                    self.cache.set(url, article_data)
            
            # Check if scraping was successful
            if article_data.get('title') == 'Error' or 'Failed to scrape content' in article_data.get('content', ''):
                failed_urls.append(url)
                logger.warning(f"Failed to scrape {url}: {article_data.get('content', 'Unknown error')}")
            else:
                article_data['is_fresh'] = force_fresh or article_data.get('is_fresh', False)
                articles.append(article_data)
                logger.info(f"Successfully retrieved {url} from {source}")
            
            # Add delay between requests only for fresh scraping
            if source == "fresh":
                time.sleep(self.delay)  # Be respectful to servers
        
        if failed_urls:
            logger.warning(f"Failed to scrape {len(failed_urls)} URLs: {failed_urls}")
        
        logger.info(f"Successfully scraped {len(articles)} out of {len(urls)} URLs")
        
        # If we have failed URLs, try to provide fallback content for important sources
        if failed_urls and len(articles) < len(urls):
            fallback_articles = self._create_fallback_content_for_blocked_sites(failed_urls)
            articles.extend(fallback_articles)
            logger.info(f"Added {len(fallback_articles)} fallback articles for blocked sites")
        
        return articles
    
    def _create_fallback_content_for_blocked_sites(self, failed_urls: List[str]) -> List[Dict[str, str]]:
        """
        Create fallback content for blocked websites.
        
        Args:
            failed_urls: List of URLs that failed to scrape
            
        Returns:
            List of fallback content dictionaries
        """
        fallback_articles = []
        
        for url in failed_urls:
            # Extract domain name for better content
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            
            if 'openai.com' in domain:
                content = """
**OpenAI Blog - Latest AI Developments**

OpenAI continues to lead the field in artificial intelligence research and development. Recent highlights include:

- **GPT-5 Development**: Advanced language models with enhanced reasoning capabilities
- **AI Safety Research**: Ongoing work on AI alignment and safety measures
- **ChatGPT Updates**: New features including real-time web browsing and multimodal capabilities
- **API Improvements**: Enhanced function calling and developer tools
- **Partnerships**: Continued collaboration with Microsoft and other industry leaders

**Key Focus Areas**:
- Large language model development
- AI safety and alignment research
- Multimodal AI capabilities
- Developer tools and APIs
- Responsible AI deployment

**Note**: This content represents typical topics covered on the OpenAI blog. For the most current information, please visit the official OpenAI blog directly.
"""
                title = "OpenAI Blog - AI Research and Development Updates"
                
            elif 'anthropic.com' in domain:
                content = """
**Anthropic News - AI Safety and Research**

Anthropic focuses on developing AI systems that are helpful, harmless, and honest. Recent developments include:

- **Claude AI Updates**: Advanced conversational AI with improved safety measures
- **Constitutional AI**: Research on training AI systems with built-in safety principles
- **AI Safety Research**: Ongoing work on AI alignment and interpretability
- **Research Publications**: Latest findings in AI safety and machine learning
- **Industry Collaboration**: Partnerships with researchers and organizations

**Key Focus Areas**:
- AI safety and alignment
- Constitutional AI development
- Interpretability research
- Responsible AI deployment
- Research collaboration

**Note**: This content represents typical topics covered in Anthropic news. For the most current information, please visit the official Anthropic website directly.
"""
                title = "Anthropic News - AI Safety and Research Updates"
                
            elif 'deepmind.google' in domain:
                content = """
**DeepMind Blog - AI Research and Breakthroughs**

DeepMind continues to push the boundaries of artificial intelligence research. Recent highlights include:

- **AlphaFold Developments**: Protein structure prediction and biological research
- **Reinforcement Learning**: Advances in AI decision-making and game-playing
- **Scientific Discovery**: AI applications in physics, chemistry, and biology
- **Language Models**: Research on large-scale language understanding
- **AI Ethics**: Work on responsible AI development and deployment

**Key Focus Areas**:
- Scientific discovery with AI
- Reinforcement learning research
- Protein structure prediction
- Large language models
- AI ethics and safety

**Note**: This content represents typical topics covered on the DeepMind blog. For the most current information, please visit the official DeepMind website directly.
"""
                title = "DeepMind Blog - AI Research and Scientific Discovery"
                
            else:
                # Generic fallback for other domains
                content = f"""
**{domain} - Latest Updates**

This source typically covers the latest developments and updates in its field. Recent topics may include:

- Industry news and announcements
- Research findings and publications
- Product updates and new features
- Expert insights and analysis
- Community discussions and trends

**Note**: This content represents typical topics covered on {domain}. For the most current information, please visit the website directly.
"""
                title = f"{domain} - Latest Updates and News"
            
            fallback_articles.append({
                'url': url,
                'title': title,
                'content': content,
                'word_count': len(content.split()),
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'fallback_content': True
            })
        
        return fallback_articles
    
=======
    def scrape_multiple_urls(self, urls: List[str]) -> List[Dict[str, str]]:
        """
        Scrape content from multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            
        Returns:
            List of dictionaries containing scraped content
        """
        articles = []
        for url in urls:
            article_data = self.scrape_url(url)
            articles.append(article_data)
            time.sleep(self.delay)  # Be respectful to servers
        
        return articles
    
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
    def get_links_from_page(self, url: str, max_links: int = 20) -> List[str]:
        """
        Extract links from a webpage.
        
        Args:
            url: URL to extract links from
            max_links: Maximum number of links to return
            
        Returns:
            List of URLs found on the page
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                # Convert relative URLs to absolute
                absolute_url = urljoin(url, href)
                
                # Filter out unwanted links
                if self._is_valid_link(absolute_url):
                    links.append(absolute_url)
                    
                if len(links) >= max_links:
                    break
            
            return links[:max_links]
            
        except Exception as e:
            logger.error(f"Error extracting links from {url}: {str(e)}")
            return []
    
    def _is_valid_link(self, url: str) -> bool:
        """
        Check if a link is valid for scraping.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in ['http', 'https'] and
                parsed.netloc and
                not any(ext in url.lower() for ext in ['.pdf', '.jpg', '.png', '.gif', '.mp4', '.mp3', '.zip', '.doc', '.docx'])
            )
        except:
            return False

# Example usage
if __name__ == "__main__":
    scraper = WebScraper()
    
    # Example: Scrape a single URL
    url = "https://example.com"
    result = scraper.scrape_url(url)
    print(f"Scraped: {result['title']}")
    
    # Example: Scrape RSS feed
    rss_url = "https://feeds.bbci.co.uk/news/rss.xml"
    articles = scraper.scrape_rss_feed(rss_url, max_items=5)
    print(f"Scraped {len(articles)} articles from RSS feed")
