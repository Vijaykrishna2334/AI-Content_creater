import os
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
import requests

try:
    # Optional SDK import; we can fall back to raw HTTP if this fails
    from groq import Groq  # type: ignore
except Exception:  # pragma: no cover
    Groq = None  # Fallback to requests

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GroqContentProcessor:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Groq content processor.
        
        Args:
            api_key: Groq API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass it directly.")
        
        # Try SDK first; if it fails due to httpx/proxies mismatch, fall back to raw HTTP
        self.client = None
        if Groq is not None:
            try:
                self.client = Groq(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Groq SDK unavailable ({e}); falling back to HTTP requests.")
        # Allow overriding via env; default to a supported Groq model
        self.model = os.getenv('GROQ_MODEL', 'llama-3.1-8b-instant')
    
    def summarize_article(self, article: Dict[str, str], max_length: int = 500) -> str:
        """
        Summarize a single article using Groq LLM.
        
        Args:
            article: Dictionary containing article data (title, content, etc.)
            max_length: Maximum length of the summary
            
        Returns:
            Summarized content
        """
        try:
            content = article.get('content', '')
            title = article.get('title', 'Untitled')
            url = article.get('url', '')
            
            if not content or len(content.strip()) < 50:
                return f"**{title}**\n\n*Content too short or unavailable for summarization.*\n\n[Read more]({url})"
            
            prompt = f"""
            Please summarize the following article in a clear, concise manner. 
            Focus on the main points and key insights. Keep it under {max_length} words.
            
            Title: {title}
            URL: {url}
            
            Content:
            {content[:3000]}  # Limit content to avoid token limits
            
            Please provide a well-structured summary with:
            1. Main topic/key points
            2. Important details
            3. Key takeaways
            """
            
            try:
                summary = self._chat_completion(prompt, temperature=0.3, max_tokens=600)
            except Exception as llm_err:
                logger.warning(f"LLM summary failed, using local fallback: {llm_err}")
                text = content[:2000]
                words = text.split()
                short = ' '.join(words[:100]) + ('...' if len(words) > 100 else '')
                summary = f"{short}\n\n*Source: [{title}]({url})*"
            
            # Add source attribution
            summary += f"\n\n*Source: [{title}]({url})*"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing article {article.get('url', 'unknown')}: {str(e)}")
            return f"**{article.get('title', 'Untitled')}**\n\n*Error generating summary: {str(e)}*\n\n[Read more]({article.get('url', '')})"
    
    def process_multiple_articles(self, articles: List[Dict[str, str]], max_length: int = 500) -> List[Dict[str, str]]:
        """
        Process and summarize multiple articles.
        
        Args:
            articles: List of article dictionaries
            max_length: Maximum length of each summary
            
        Returns:
            List of processed articles with summaries
        """
        processed_articles = []
        
        for i, article in enumerate(articles):
            logger.info(f"Processing article {i+1}/{len(articles)}: {article.get('title', 'Untitled')}")
            
            summary = self.summarize_article(article, max_length)
            
            processed_article = article.copy()
            processed_article['summary'] = summary
            processed_article['processed_at'] = logger.info(f"Article processed at {__import__('time').strftime('%Y-%m-%d %H:%M:%S')}")
            
            processed_articles.append(processed_article)
        
        return processed_articles
    
    def create_digest(self, articles: List[Dict[str, str]], digest_title: str = "Content Digest") -> str:
        """
        Create a comprehensive digest from multiple articles.
        
        Args:
            articles: List of processed articles
            digest_title: Title for the digest
            
        Returns:
            Formatted digest content
        """
        try:
            if not articles:
                return f"# {digest_title}\n\nNo articles to process."
            
            # Prepare content for digest generation
            articles_text = ""
            for i, article in enumerate(articles, 1):
                title = article.get('title', f'Article {i}')
                content = article.get('content', '')[:1000]  # Limit content
                url = article.get('url', '')
                articles_text += f"\n\n--- Article {i} ---\nTitle: {title}\nURL: {url}\nContent: {content}\n"
            
            prompt = f"""
            Create a comprehensive digest from the following articles. 
            The digest should be well-structured and engaging.
            
            Title: {digest_title}
            
            Articles:
            {articles_text}
            
            Please create a digest that includes:
            1. An engaging introduction
            2. Key themes and topics covered
            3. Brief summaries of each article (2-3 sentences each)
            4. Overall insights and trends
            5. A conclusion with key takeaways
            
            Format it in markdown and make it engaging for email distribution.
            """
            
            try:
                digest = self._chat_completion(
                    prompt,
                    system_prompt="You are a skilled content curator and writer who creates engaging, well-structured digests from multiple articles. Use markdown formatting effectively.",
                    temperature=0.35,
                    max_tokens=1000,
                )
                digest = f"# {digest_title}\n\n*Generated on {__import__('time').strftime('%Y-%m-%d at %H:%M:%S')}*\n\n{digest}"
                return digest
            except Exception as llm_err:
                logger.warning(f"LLM digest failed, building simple digest locally: {llm_err}")
                lines = [f"# {digest_title}", "", f"*Generated on {__import__('time').strftime('%Y-%m-%d at %H:%M:%S')}*", "", "## Highlights"]
                for i, a in enumerate(articles, 1):
                    title = a.get('title', f'Article {i}')
                    url = a.get('url', '')
                    summary = a.get('summary')
                    if not summary or 'Error generating summary' in summary:
                        text = (a.get('content') or '')
                        words = text.split()
                        summary = ' '.join(words[:80]) + ('...' if len(words) > 80 else '')
                    lines.append(f"- [{title}]({url}) — {summary}")
                return "\n".join(lines)
            
        except Exception as e:
            logger.error(f"Error creating digest: {str(e)}")
            return f"# {digest_title}\n\n*Error creating digest: {str(e)}*"
    
    def extract_key_insights(self, articles: List[Dict[str, str]]) -> str:
        """
        Extract key insights and trends from multiple articles.
        
        Args:
            articles: List of processed articles
            
        Returns:
            Formatted insights
        """
        try:
            if not articles:
                return "No articles to analyze."
            
            # Combine all content
            combined_content = ""
            for article in articles:
                title = article.get('title', '')
                content = article.get('content', '')[:800]
                combined_content += f"\n\nTitle: {title}\nContent: {content}\n"
            
            prompt = f"""
            Analyze the following articles and extract key insights, trends, and patterns.
            Focus on:
            1. Common themes across articles
            2. Emerging trends or patterns
            3. Key insights and takeaways
            4. Important developments or news
            5. Actionable information
            
            Articles:
            {combined_content}
            
            Provide a structured analysis with clear headings and bullet points.
            """
            
            insights = self._chat_completion(prompt, system_prompt="You are an expert analyst who identifies patterns, trends, and key insights from multiple articles. Provide clear, actionable analysis.", temperature=0.3, max_tokens=800)
            return f"# Key Insights & Trends\n\n{insights}"
            
        except Exception as e:
            logger.error(f"Error extracting insights: {str(e)}")
            return f"# Key Insights & Trends\n\n*Error analyzing articles: {str(e)}*"

    def _chat_completion(self, user_prompt: str, system_prompt: str = "You are a helpful assistant that creates clear, concise summaries of articles. Focus on the main points and provide actionable insights.", temperature: float = 0.3, max_tokens: int = 800) -> str:
        """
        Create a chat completion using the Groq SDK when available, otherwise via raw HTTP.
        This avoids crashes from httpx Client("proxies") incompatibilities.
        """
        try:
            if self.client is not None:
                response = self.client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    model=self.model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content.strip()
        except Exception as sdk_err:
            logger.warning(f"Groq SDK call failed ({sdk_err}); using HTTP fallback.")

        # HTTP fallback
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code == 400:
            # Capture error detail and retry with a shorter prompt (common cause: context too large)
            try:
                detail = resp.json()
            except Exception:
                detail = {"error": resp.text}
            logger.warning(f"Groq HTTP 400: {detail}")
            shortened = user_prompt[:1500]
            payload["messages"][1]["content"] = shortened
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()

# Example usage
if __name__ == "__main__":
    # This is just for testing - you'll need to set GROQ_API_KEY environment variable
    try:
        processor = GroqContentProcessor()
        
        # Example article
        sample_article = {
            'title': 'Sample Article',
            'content': 'This is a sample article content for testing the summarization functionality.',
            'url': 'https://example.com'
        }
        
        summary = processor.summarize_article(sample_article)
        print("Summary:", summary)
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your GROQ_API_KEY environment variable.")
