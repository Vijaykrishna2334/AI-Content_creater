import os
import resend
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
from datetime import datetime
import markdown  # Add this import at the top

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- CONSISTENT NEWSLETTER TEMPLATE ---
NEWSLETTER_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>{newsletter_title}</title>
</head>
<body style="font-family: Arial, sans-serif; background: #f9f9f9; color: #222;">
  <div style="max-width: 700px; margin: 0 auto; background: #fff; padding: 32px; border-radius: 8px;">
    <h1 style="color: #2d3748;">{newsletter_title}</h1>
    <p style="color: #718096; font-size: 14px;">Generated on {date}</p>
    <hr style="margin: 24px 0;">
    <h2>Introduction</h2>
    <p>{introduction}</p>
    <h2>Key Themes and Topics</h2>
    <ul>
      {key_themes}
    </ul>
    <h2>Article Digest</h2>
    {articles}
    <h2>Overall Insights and Trends</h2>
    <p>{insights}</p>
    <h2>Conclusion</h2>
    <p>{conclusion}</p>
    <hr style="margin: 32px 0;">
    <p style="font-size: 13px; color: #888;">
      Stay Connected:<br>
      Twitter: <a href="https://twitter.com/yourmlnewsletter">@yourmlnewsletter</a> |
      LinkedIn: <a href="https://linkedin.com/company/yourmlnewsletter">@yourmlnewsletter</a> |
      Email: <a href="mailto:subscribe@yourmlnewsletter.com">subscribe@yourmlnewsletter.com</a>
    </p>
    <p style="font-size: 13px; color: #888;">
      Want to receive future issues? <a href="https://yourdomain.com/subscribe">Subscribe now!</a>
    </p>
  </div>
</body>
</html>
"""

class EmailSender:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Resend email sender.
        
        Args:
            api_key: Resend API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv('RESEND_API_KEY')
        if not self.api_key:
            raise ValueError("Resend API key is required. Set RESEND_API_KEY environment variable or pass it directly.")
        
        resend.api_key = self.api_key
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@yourdomain.com')
        self.sandbox_from = 'onboarding@resend.dev'
    
    def send_content_digest(self, 
                          content: str, 
                          subject: str, 
                          to_emails: List[str],
                          from_email: Optional[str] = None,
                          template_data: Optional[Dict[str, str]] = None) -> Dict[str, any]:
        """
        Send a content digest via email using the consistent template.
        
        Args:
            content: The main article digest (HTML or Markdown)
            subject: Email subject line
            to_emails: List of recipient email addresses
            from_email: Sender email address (optional)
            template_data: Optional dict for template fields (see below)
            
        Returns:
            Response from Resend API
        """
        try:
            sender = from_email or self.from_email

            # Use template for consistent format
            html_content = self._render_newsletter_template(content, template_data)

            params = {
                "from": sender,
                "to": to_emails,
                "subject": subject,
                "html": html_content,
            }

            logger.info(f"Sending email to {len(to_emails)} recipients: {', '.join(to_emails)}")

            try:
                response = resend.Emails.send(params)
            except Exception as e:
                # If domain not verified, retry with sandbox sender
                msg = str(e)
                if 'domain is not verified' in msg.lower() or 'verify your domain' in msg.lower():
                    logger.warning("Sender domain not verified; retrying with Resend sandbox sender.")
                    params["from"] = self.sandbox_from
                    response = resend.Emails.send(params)
                else:
                    raise

            logger.info(f"Email sent successfully. ID: {response.get('id', 'unknown')}")
            return response

        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {"error": str(e), "success": False}
    
    def send_article_summaries(self, 
                             articles: List[Dict[str, str]], 
                             subject: str = "Daily Content Digest",
                             to_emails: List[str] = None,
                             template_data: Optional[Dict[str, str]] = None) -> Dict[str, any]:
        """
        Send individual article summaries via email using the consistent template.
        
        Args:
            articles: List of processed articles with summaries
            subject: Email subject line
            to_emails: List of recipient email addresses
            template_data: Optional dict for template fields (see below)
            
        Returns:
            Response from Resend API
        """
        try:
            if not articles:
                return {"error": "No articles to send", "success": False}
            
            # Format articles for the template
            articles_html = self._format_articles_for_template(articles)

            # Use test email if no recipients provided
            recipients = to_emails or ["test@example.com"]

            # Fill in template data if not provided
            if not template_data:
                template_data = {}
            template_data.setdefault("articles", articles_html)

            return self.send_content_digest(
                content=articles_html,
                subject=subject,
                to_emails=recipients,
                template_data=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending article summaries: {str(e)}")
            return {"error": str(e), "success": False}
    
    def send_weekly_digest(self, 
                          digest_content: str, 
                          to_emails: List[str] = None,
                          template_data: Optional[Dict[str, str]] = None) -> Dict[str, any]:
        """
        Send a weekly digest email using the consistent template.
        
        Args:
            digest_content: The digest content
            to_emails: List of recipient email addresses
            template_data: Optional dict for template fields (see below)
            
        Returns:
            Response from Resend API
        """
        try:
            # Generate subject with current date
            current_date = datetime.now().strftime("%B %d, %Y")
            subject = f"Weekly Content Digest - {current_date}"
            
            # Use test email if no recipients provided
            recipients = to_emails or ["test@example.com"]

            return self.send_content_digest(
                content=digest_content,
                subject=subject,
                to_emails=recipients,
                template_data=template_data
            )
            
        except Exception as e:
            logger.error(f"Error sending weekly digest: {str(e)}")
            return {"error": str(e), "success": False}
    
    def _render_newsletter_template(self, articles_html: str, template_data: Optional[Dict[str, str]]) -> str:
        """
        Render the newsletter HTML using the consistent template.
        """
        now = datetime.now()
        if template_data is None:
            template_data = {}

        # Convert all markdown fields to HTML
        def md(text):
            return markdown.markdown(text or "")

        data = {
            "newsletter_title": template_data.get("newsletter_title", "Your Machine Learning Newsletter"),
            "date": now.strftime("%Y-%m-%d at %H:%M:%S"),
            "introduction": md(template_data.get("introduction", "Welcome to this edition of your newsletter!")),
            "key_themes": md(template_data.get("key_themes", "* AI\n* Machine Learning\n* Industry News")),
            "articles": md(articles_html),
            "insights": md(template_data.get("insights", "Stay tuned for more insights in future issues.")),
            "conclusion": md(template_data.get("conclusion", "Thank you for reading!")),
        }
        return NEWSLETTER_HTML_TEMPLATE.format(**data)
    
    def _format_articles_for_template(self, articles: List[Dict[str, str]]) -> str:
        """
        Format articles as HTML for the newsletter template.
        
        Args:
            articles: List of processed articles
            
        Returns:
            Formatted HTML for the articles section
        """
        articles_html = ""
        for i, article in enumerate(articles, 1):
            title = article.get('title', f'Article {i}')
            summary = article.get('summary', 'No summary available')
            url = article.get('url', '#')
            word_count = article.get('word_count', 0)
            articles_html += f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h3 style="margin-top: 0; color: #333;">
                    <a href="{url}" style="color: #0066cc; text-decoration: none;">{title}</a>
                </h3>
                <p style="color: #666; font-size: 12px;">{word_count} words | <a href="{url}">Read original</a></p>
                <div style="margin-top: 10px;">
                    {summary}
                </div>
            </div>
            """
        return articles_html
    
    def test_email_connection(self) -> bool:
        """
        Test the email connection by sending a test email.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            test_content = "<p>This is a test email to verify the Resend integration is working correctly.</p>"
            template_data = {
                "newsletter_title": "Test Email",
                "introduction": "This is a test introduction.",
                "key_themes": "<li>Test</li>",
                "insights": "Test insights.",
                "conclusion": "Test conclusion."
            }
            response = self.send_content_digest(
                content=test_content,
                subject="Test Email - Resend Integration",
                to_emails=["test@example.com"],
                template_data=template_data
            )
            return "error" not in response
        except Exception as e:
            logger.error(f"Email connection test failed: {str(e)}")
            return False

# Example usage
if __name__ == "__main__":
    try:
        sender = EmailSender()
        
        # Test email connection
        if sender.test_email_connection():
            print("Email connection test successful!")
        else:
            print("Email connection test failed.")
            
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set your RESEND_API_KEY environment variable.")
