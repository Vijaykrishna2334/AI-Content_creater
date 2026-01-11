import os
import resend
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
                          from_email: Optional[str] = None) -> Dict[str, any]:
        """
        Send a content digest via email.
        
        Args:
            content: The content to send (HTML or plain text)
            subject: Email subject line
            to_emails: List of recipient email addresses
            from_email: Sender email address (optional)
            
        Returns:
            Response from Resend API
        """
        try:
            sender = from_email or self.from_email
            
            # Convert markdown to HTML if needed
            html_content = self._markdown_to_html(content)
            
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
                             to_emails: List[str] = None) -> Dict[str, any]:
        """
        Send individual article summaries via email.
        
        Args:
            articles: List of processed articles with summaries
            subject: Email subject line
            to_emails: List of recipient email addresses
            
        Returns:
            Response from Resend API
        """
        try:
            if not articles:
                return {"error": "No articles to send", "success": False}
            
            # Create email content
            email_content = self._format_articles_for_email(articles)
            
            # Use test email if no recipients provided
            recipients = to_emails or ["test@example.com"]
            
            return self.send_content_digest(
                content=email_content,
                subject=subject,
                to_emails=recipients
            )
            
        except Exception as e:
            logger.error(f"Error sending article summaries: {str(e)}")
            return {"error": str(e), "success": False}
    
    def send_weekly_digest(self, 
                          digest_content: str, 
                          to_emails: List[str] = None) -> Dict[str, any]:
        """
        Send a weekly digest email.
        
        Args:
            digest_content: The digest content
            to_emails: List of recipient email addresses
            
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
                to_emails=recipients
            )
            
        except Exception as e:
            logger.error(f"Error sending weekly digest: {str(e)}")
            return {"error": str(e), "success": False}
    
    def _format_articles_for_email(self, articles: List[Dict[str, str]]) -> str:
        """
        Format articles for email display.
        
        Args:
            articles: List of processed articles
            
        Returns:
            Formatted email content
        """
        email_content = f"""
        <h1>Content Digest - {datetime.now().strftime("%B %d, %Y")}</h1>
        <p><em>Your curated content summary</em></p>
        
        <div style="margin: 20px 0;">
        """
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', f'Article {i}')
            summary = article.get('summary', 'No summary available')
            url = article.get('url', '#')
            word_count = article.get('word_count', 0)
            
            email_content += f"""
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
        
        email_content += """
        </div>
        
        <hr style="margin: 30px 0;">
        <p style="color: #666; font-size: 12px;">
            This digest was generated automatically. 
            <a href="mailto:unsubscribe@yourdomain.com">Unsubscribe</a> | 
            <a href="https://yourdomain.com">Visit our website</a>
        </p>
        """
        
        return email_content
    
    def _markdown_to_html(self, markdown_content: str) -> str:
        """
        Convert markdown content to HTML for email with professional styling.
        
        Args:
            markdown_content: Markdown formatted content
            
        Returns:
            HTML formatted content with professional styling
        """
        import re
        
        # Start with the markdown content
        html = markdown_content
        
        # Add professional email styling
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Newsletter</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .newsletter-container {{
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                h2 {{
                    color: #34495e;
                    margin-top: 30px;
                    margin-bottom: 15px;
                    font-size: 1.4em;
                }}
                h3 {{
                    color: #2c3e50;
                    margin-top: 25px;
                    margin-bottom: 10px;
                    font-size: 1.2em;
                }}
                p {{
                    margin-bottom: 15px;
                    text-align: justify;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                .article-summary {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-left: 4px solid #3498db;
                    margin: 15px 0;
                    border-radius: 0 4px 4px 0;
                }}
                .source-link {{
                    font-style: italic;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
                .newsletter-meta {{
                    color: #7f8c8d;
                    font-style: italic;
                    margin-bottom: 30px;
                    padding: 10px;
                    background-color: #ecf0f1;
                    border-radius: 4px;
                }}
                ul, ol {{
                    margin: 15px 0;
                    padding-left: 25px;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                .footer {{
                    margin-top: 40px;
                    padding-top: 20px;
                    border-top: 1px solid #ecf0f1;
                    color: #7f8c8d;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="newsletter-container">
                {html}
            </div>
        </body>
        </html>
        """
        
        # Convert markdown to HTML
        html = styled_html
        
        # Headers - more precise replacement
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # Bold and italic - more precise replacement
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # Links
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        html = re.sub(link_pattern, r'<a href="\2">\1</a>', html)
        
        # Handle article summaries with special styling
        html = re.sub(r'### Article \d+: (.+?)(?=###|$)', 
                     lambda m: f'<div class="article-summary"><h3>{m.group(1)}</h3>', 
                     html, flags=re.DOTALL)
        
        # Close article summaries
        # Wrap up to two consecutive source lines into a single source-link container
        def _wrap_sources(m):
            block = m.group(0)
            # Find individual source links
            links = re.findall(r'(\*Source: \[.+?\]\(.+?\)\*)', block)
            # Join links with a line break
            inner = '<br>'.join(links)
            return f'<div class="source-link">{inner}</div></div>'

        html = re.sub(r'(?:\*Source: \[.+?\]\(.+?\)\*\s*){1,}', _wrap_sources, html)
        
        # Add newsletter meta styling
        html = re.sub(r'(\*Generated on .+?\*)', r'<div class="newsletter-meta">\1</div>', html)
        
        # Line breaks and paragraphs
        html = re.sub(r'\n\n+', '</p><p>', html)
        html = re.sub(r'^(.+)$', r'<p>\1</p>', html, flags=re.MULTILINE)
        
        # Lists
        html = re.sub(r'^[-*] (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^(\d+)\. (.+)$', r'<li>\2</li>', html, flags=re.MULTILINE)
        
        # Wrap consecutive list items in ul/ol
        html = re.sub(r'(<li>.*?</li>)(\s*<li>.*?</li>)+', 
                     lambda m: f'<ul>{m.group(0)}</ul>', html, flags=re.DOTALL)
        
        # Clean up empty paragraphs and fix structure
        html = re.sub(r'<p></p>', '', html)
        html = re.sub(r'<p>\s*</p>', '', html)
        html = re.sub(r'<p>(<h[1-6]>)', r'\1', html)
        html = re.sub(r'(</h[1-6]>)</p>', r'\1', html)
        html = re.sub(r'<p>(<ul>)', r'\1', html)
        html = re.sub(r'(</ul>)</p>', r'\1', html)
        html = re.sub(r'<p>(<ol>)', r'\1', html)
        html = re.sub(r'(</ol>)</p>', r'\1', html)
        
        # Add minimal footer (removed subscribe/unsubscribe elements)
        html = re.sub(r'</div>\s*</body>', 
                     r'<div class="footer"><p>This newsletter was generated automatically.</p></div></div></body>', 
                     html)
        
        return html
    
    def test_email_connection(self) -> bool:
        """
        Test the email connection by sending a test email.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            test_content = """
            <h2>Test Email</h2>
            <p>This is a test email to verify the Resend integration is working correctly.</p>
            <p>If you receive this email, the setup is successful!</p>
            """
            
            response = self.send_content_digest(
                content=test_content,
                subject="Test Email - Resend Integration",
                to_emails=["test@example.com"]
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
