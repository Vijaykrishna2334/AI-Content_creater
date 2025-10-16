import requests
import feedparser
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from typing import List, Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, delay: float = 1.0):
        """
        Initialize the web scraper with a delay between requests to be respectful.
        
        Args:
            delay: Delay in seconds between requests
        """
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict[str, str]:
        """
        Scrape content from a single URL.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing title, content, and metadata
        """
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
            
            # Limit content length
            if len(content) > 5000:
                content = content[:5000] + "..."
            
            return {
                'url': url,
                'title': title,
                'content': content,
                'word_count': len(content.split()),
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return {
                'url': url,
                'title': 'Error',
                'content': f'Failed to scrape content: {str(e)}',
                'word_count': 0,
                'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def scrape_rss_feed(self, rss_url: str, max_items: int = 10) -> List[Dict[str, str]]:
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
                    article_data = self.scrape_url(entry.link)
                    # Add RSS metadata
                    article_data['rss_title'] = getattr(entry, 'title', '')
                    article_data['rss_summary'] = getattr(entry, 'summary', '')
                    article_data['rss_published'] = getattr(entry, 'published', '')
                    articles.append(article_data)
                    
                    # Add delay between requests
                    time.sleep(self.delay)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error scraping RSS feed {rss_url}: {str(e)}")
            return []
    
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
