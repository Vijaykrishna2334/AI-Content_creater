import os
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

from scraper import WebScraper
from .groq_processor import GroqContentProcessor
from .email_sender import EmailSender
from db import upsert_user, insert_content

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NEWSLETTER_TEMPLATE = """
# {title}

*Generated on {date}*

---

## Introduction

{introduction}

---

## Key Themes and Topics

{key_themes}

---

## Article Digest

{articles}

---

## Overall Insights and Trends

{insights}

---

## Conclusion

{conclusion}

---

## Stay Connected

- Twitter: {twitter}
- LinkedIn: {linkedin}
- Email: {email}

---

## Subscribe

Want to receive future issues? Subscribe now!
"""

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
        self.processor = GroqContentProcessor(api_key=groq_api_key)
        self.email_sender = EmailSender(api_key=resend_api_key)
        
        if from_email:
            self.email_sender.from_email = from_email
    
    def process_urls(self, 
                    urls: List[str], 
                    email_recipients: List[str] = None,
                    digest_title: str = "Content Digest") -> Dict[str, any]:
        """
        Process a list of URLs through the complete pipeline.
        
        Args:
            urls: List of URLs to process
            email_recipients: List of email recipients
            digest_title: Title for the digest
            
        Returns:
            Dictionary containing results and status
        """
        try:
            logger.info(f"Starting content pipeline with {len(urls)} URLs")
            
            # Step 1: Scrape content from URLs
            logger.info("Step 1: Scraping content from URLs...")
            articles = self.scraper.scrape_multiple_urls(urls)
            logger.info(f"Scraped {len(articles)} articles")
            
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

            # Step 2.5: Save content to database
            user_id = None
            try:
                if email_recipients and len(email_recipients) > 0:
                    user = upsert_user(email=email_recipients[0])
                    user_id = user.get('id')
            except Exception as e:
                logger.warning(f"User upsert failed: {e}")

            saved = 0
            for art in processed_articles:
                try:
                    insert_content(
                        user_id=user_id,
                        source_url=art.get('url', ''),
                        title=art.get('title', ''),
                        raw_content=art.get('content', ''),
                        summary=art.get('summary', ''),
                    )
                    saved += 1
                except Exception as e:
                    logger.warning(f"Content save failed for {art.get('url','')}: {e}")
            
            logger.info(f"Saved {saved} articles to database")
            
            # Step 3: Create digest
            logger.info("Step 3: Creating content digest...")
            digest_content = self.processor.create_digest(processed_articles, digest_title)
            
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
                "saved_count": saved,
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
                         digest_title: str = "RSS Feed Digest") -> Dict[str, any]:
        """
        Process RSS feeds through the complete pipeline.
        
        Args:
            rss_urls: List of RSS feed URLs
            max_items_per_feed: Maximum items to process per feed
            email_recipients: List of email recipients
            digest_title: Title for the digest
            
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
            digest_content = self.processor.create_digest(processed_articles, digest_title)
            
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
                "saved_count": saved,
                "processed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RSS pipeline error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "articles": []
            }
    
    def process_mixed_sources(self, 
                             urls: List[str] = None,
                             rss_urls: List[str] = None,
                             max_rss_items: int = 5,
                             email_recipients: List[str] = None,
                             digest_title: str = "Mixed Content Digest") -> Dict[str, any]:
        """
        Process both URLs and RSS feeds in a single pipeline.
        
        Args:
            urls: List of URLs to process
            rss_urls: List of RSS feed URLs
            max_rss_items: Maximum items to process per RSS feed
            email_recipients: List of email recipients
            digest_title: Title for the digest
            
        Returns:
            Dictionary containing results and status
        """
        try:
            logger.info("Starting mixed content pipeline")
            
            all_articles = []
            
            # Process URLs if provided
            if urls:
                logger.info(f"Processing {len(urls)} URLs...")
                url_articles = self.scraper.scrape_multiple_urls(urls)
                all_articles.extend(url_articles)
                logger.info(f"Scraped {len(url_articles)} articles from URLs")
            
            # Process RSS feeds if provided
            if rss_urls:
                logger.info(f"Processing {len(rss_urls)} RSS feeds...")
                for rss_url in rss_urls:
                    rss_articles = self.scraper.scrape_rss_feed(rss_url, max_rss_items)
                    all_articles.extend(rss_articles)
                    logger.info(f"Scraped {len(rss_articles)} articles from {rss_url}")
            
            if not all_articles:
                return {
                    "success": False,
                    "error": "No articles were successfully scraped",
                    "articles": []
                }
            
            # Process all articles with Groq LLM
            logger.info("Processing all articles with Groq LLM...")
            processed_articles = self.processor.process_multiple_articles(all_articles)
            logger.info(f"Processed {len(processed_articles)} articles")

            # Persist content (associate to first recipient if any)
            user_id = None
            try:
                if email_recipients and len(email_recipients) > 0:
                    user = upsert_user(email=email_recipients[0])
                    user_id = user.get('id')
            except Exception as e:
                logger.warning(f"User upsert failed: {e}")

            saved = 0
            for art in processed_articles:
                try:
                    insert_content(
                        user_id=user_id,
                        source_url=art.get('url', ''),
                        title=art.get('title', ''),
                        raw_content=art.get('content', ''),
                        summary=art.get('summary', ''),
                    )
                    saved += 1
                except Exception as e:
                    logger.warning(f"Content save failed for {art.get('url','')}: {e}")
            
            # Create digest
            logger.info("Creating mixed content digest...")
            digest_content = self.processor.create_digest(processed_articles, digest_title)
            
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
