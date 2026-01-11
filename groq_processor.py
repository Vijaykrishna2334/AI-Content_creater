import os
from typing import List, Dict, Optional
import logging
from dotenv import load_dotenv
import requests
import re

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
            logger.error("Groq API key is required. Set GROQ_API_KEY environment variable or pass it directly.")
            raise ValueError("Groq API key is required. Set GROQ_API_KEY environment variable or pass it directly.")
        
        # Debug: Log API key status
        logger.info(f"GroqContentProcessor initialized with API key: {bool(self.api_key)}")
        
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
            
            # Check if this is a YouTube video transcript
            is_youtube = article.get('source') == 'youtube' or 'youtube' in url.lower()
            
            if is_youtube:
                prompt = f"""
                Please create a comprehensive summary of this YouTube video transcript. 
                The summary should be informative and detailed, helping readers understand the key concepts, findings, and insights discussed in the video.
                
                Title: {title}
                URL: {url}
                
                Video Transcript:
                {content[:4000]}  # Allow more content for YouTube videos
                
                Please provide a detailed summary that includes:
                1. **Main Topic**: What is this video about?
                2. **Key Concepts**: What are the main concepts, techniques, or technologies discussed?
                3. **Important Findings**: What discoveries, results, or insights are presented?
                4. **Technical Details**: What specific technical information or methodologies are explained?
                5. **Implications**: What does this mean for the field or future research?
                6. **Key Takeaways**: What are the most important points viewers should remember?
                
                Make the summary informative and engaging, providing enough detail for readers to understand the video's content without watching it. Aim for 200-300 words.
                """
            else:
                prompt = f"""
                Please summarize the following article in a clear, comprehensive manner. 
                Focus on the main points and key insights. Provide enough detail to be informative.
                
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
                # Use more tokens for YouTube videos to allow detailed summaries
                max_tokens = 1000 if is_youtube else 600
                summary = self._chat_completion(prompt, temperature=0.3, max_tokens=max_tokens)
            except Exception as llm_err:
                logger.warning(f"LLM summary failed, using local fallback: {llm_err}")
                text = content[:2000]
                words = text.split()
                short = ' '.join(words[:100]) + ('...' if len(words) > 100 else '')
                
                # Add source attribution with better formatting for YouTube videos
                # Avoid duplicating source lines if the short text already contains a source
                if '*Source:' in short or '[Source:' in short or re.search(r"\[.+?\]\(.+?\)", short):
                    summary = short
                else:
                    if is_youtube:
                        # For YouTube videos, show channel and video title when source not present
                        channel_title = article.get('channel_title', 'YouTube')
                        summary = f"{short}\n\n*Source: [{title}]({url}) - {channel_title}*"
                    else:
                        summary = f"{short}\n\n*Source: [{title}]({url})*"
            
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
    
    def create_digest(self, articles: List[Dict[str, str]], digest_title: str = "Content Digest", writing_style: str = "professional") -> str:
        """
        Create a comprehensive digest from multiple articles using specified writing style.
        
        Args:
            articles: List of processed articles
            digest_title: Title for the digest
            writing_style: Writing style to use (professional, casual, technical, or custom)
            
        Returns:
            Formatted digest content
        """
        try:
            if not articles:
                return f"# {digest_title}\n\nNo articles to process."
            
            # Import writing style manager
            from writing_styles import writing_style_manager
            
            # Get current date and time
            current_time = __import__('time').strftime('%Y-%m-%d at %H:%M:%S')
            current_date = __import__('time').strftime('%B %d, %Y')
            
            # Prepare content for digest generation
            articles_text = ""
            for i, article in enumerate(articles, 1):
                title = article.get('title', f'Article {i}')
                url = article.get('url', '')
                # Use the processed summary if available, otherwise use raw content
                summary = article.get('summary', '')
                if summary and len(summary) > 50:
                    content = summary
                else:
                    content = article.get('content', '')[:1000]  # Limit content
                
                articles_text += f"\n\n--- Article {i} ---\nTitle: {title}\nURL: {url}\nContent: {content}\n"
            
            # Debug: Log the writing style being used
            logger.info(f"Creating digest with writing style: '{writing_style}'")
            
            # Get style-specific prompt
            try:
                style_prompt = writing_style_manager.get_style_prompt(writing_style, articles_text)
                logger.info(f"Successfully generated style prompt for '{writing_style}'")
                prompt = f"""
                {style_prompt}
                
                Newsletter Title: {digest_title}
                Date: {current_date}
                
                Articles to include:
                {articles_text}
                
                Please create a digest following the specified writing style and format requirements.
                """
            except (ValueError, Exception) as e:
                # Fallback to default professional style with enhanced instructions
                logger.warning(f"Style prompt generation failed: {e}. Using fallback style for '{writing_style}'.")
                
                # Create style-specific instructions based on writing_style
                if writing_style == 'casual':
                    style_instruction = """
                    CRITICAL: Write in a CASUAL, FRIENDLY, and ENGAGING style:
                    
                    **TONE REQUIREMENTS:**
                    - Use conversational language with personal touches
                    - Include questions to engage readers (e.g., "What do you think?", "Have you seen this?")
                    - Use contractions (don't, can't, won't, it's, you're)
                    - Keep it approachable and community-focused
                    - Add personality and warmth
                    - Use informal greetings and expressions
                    - Write as if talking to a friend
                    
                    **EXAMPLE CASUAL PHRASES TO USE:**
                    - "Hey there!", "Check this out!", "This is pretty cool!"
                    - "You won't believe what happened..."
                    - "Here's something that caught my attention..."
                    - "What's really interesting about this is..."
                    """
                elif writing_style == 'technical':
                    style_instruction = """
                    CRITICAL: You MUST write in a TECHNICAL, DETAILED, and EDUCATIONAL style. This is NOT casual or conversational.
                    
                    **MANDATORY TECHNICAL TONE REQUIREMENTS:**
                    - Use formal technical terminology and concepts
                    - Provide detailed explanations and analysis
                    - Include technical details, methodologies, and specifications
                    - Focus on educational content and comprehensive coverage
                    - Use precise, technical language
                    - Explain complex concepts thoroughly
                    - Reference technical standards and frameworks
                    - NO casual language like "Well", "Okay", "You see"
                    - NO conversational phrases
                    - NO contractions (don't, can't, won't)
                    
                    **REQUIRED TECHNICAL PHRASES TO USE:**
                    - "The implementation utilizes..."
                    - "From a technical perspective..."
                    - "The underlying architecture demonstrates..."
                    - "This approach leverages advanced algorithms..."
                    - "The system architecture incorporates..."
                    - "The methodology employs..."
                    - "Technical analysis reveals..."
                    - "The framework implements..."
                    - "The algorithm demonstrates..."
                    - "From an engineering standpoint..."
                    
                    **FORBIDDEN PHRASES (DO NOT USE):**
                    - "There is one thing that I really want"
                    - "Well, just copy it then, right?"
                    - "You see, these virtual characters"
                    - "Okay, why?"
                    - Any casual or conversational language
                    """
                else:  # professional or default
                    style_instruction = """
                    CRITICAL: Write in a PROFESSIONAL, FORMAL, and BUSINESS-FOCUSED style:
                    
                    **TONE REQUIREMENTS:**
                    - Use formal language and structured approach
                    - Focus on data-driven insights and business impact
                    - Use executive summary format with clear sections
                    - Maintain professional terminology
                    - Keep it objective and authoritative
                    - Emphasize business value and ROI
                    - Use corporate communication style
                    
                    **EXAMPLE PROFESSIONAL PHRASES TO USE:**
                    - "This development represents a significant advancement..."
                    - "The implications for the industry are substantial..."
                    - "From a business perspective, this innovation..."
                    - "The strategic importance of this technology..."
                    - "Organizations should consider the following implications..."
                    """
                
                prompt = f"""
                IMPORTANT: You MUST write in the {writing_style.upper()} style. This is NOT optional.
                
                {style_instruction}
                
                Newsletter Title: {digest_title}
                Date: {current_date}
                
                Articles to include:
                {articles_text}
                
                CREATE A COMPLETE EMAIL NEWSLETTER with this structure:
                
                **GREETING** (2-3 sentences):
                A warm, welcoming introduction that sets the tone for the newsletter
                
                **ARTICLE SUMMARIES**:
                For each article, create a detailed section with:
                - ### [Article Title]
                - A comprehensive summary (150-250 words) that fully explains:
                  * What the article is about
                  * Key points and findings
                  * Why it matters
                  * Important details readers should know
                - *Source: [Title](URL)*
                
                **CLOSING** (2-3 sentences):
                A friendly sign-off thanking readers and encouraging engagement
                
                CRITICAL REQUIREMENTS:
                - Write in {writing_style} style throughout
                - NO generic filler text
                - NO meta-commentary like "Summary:" or "Technical analysis reveals:"
                - Make summaries substantive and informative (150-250 words each)
                - Include all important details from the original content
                - Make it feel like a real email someone would enjoy receiving
                """
            
            try:
                digest = self._chat_completion(
                    prompt,
                    system_prompt=f"""You are a professional newsletter editor creating engaging email newsletters. 

CRITICAL FORMATTING RULES:
1. Create a complete email newsletter with proper structure:
   - Start with a friendly greeting
   - Add a brief introduction paragraph
   - Present each article with detailed, substantive summaries (150-250 words each)
   - End with a warm closing
2. DO NOT add prefixes like "Technical analysis reveals:" or "Summary:" to article sections
3. Write naturally without meta-commentary about the summary
4. Use proper markdown headings (###) for article titles
5. Make each summary informative and engaging - readers should understand the full story
6. Include source links at the end of each article
7. Use the {writing_style} writing style consistently throughout

REMEMBER: This is an email newsletter people will receive. Make it professional, readable, and valuable.""",
                    temperature=0.35,
                    max_tokens=3000,  # Increased from 1500 to allow longer, more complete content
                )
                
                # Remove any unwanted prefixes that might have been added
                digest = digest.replace("Technical analysis reveals: ", "")
                digest = digest.replace("Summary: ", "")
                digest = digest.replace("Strategic analysis indicates: ", "")
                digest = digest.replace("Check this out: ", "")
                
                # Format the final digest with proper email structure
                formatted_digest = f"""# {digest_title}

*Generated on {current_time}*

---

{digest}

---

*Thank you for reading! Stay tuned for more updates.*
"""
                
                # Normalize repeated source lines
                formatted_digest = self._normalize_source_lines(formatted_digest)
                return formatted_digest
                
            except Exception as llm_err:
                logger.warning(f"LLM digest failed, building simple digest locally: {llm_err}")
                return self._create_fallback_digest(articles, digest_title, current_time, writing_style)
            
        except Exception as e:
            logger.error(f"Error creating digest: {str(e)}")
            return f"# {digest_title}\n\n*Error creating digest: {str(e)}*"
    
    def _create_fallback_digest(self, articles: List[Dict[str, str]], digest_title: str, current_time: str, writing_style: str = "professional") -> str:
        """
        Create a fallback digest when LLM processing fails, using proper writing style.
        
        Args:
            articles: List of processed articles
            digest_title: Title for the digest
            current_time: Current timestamp
            writing_style: Writing style to apply (professional, casual, technical)
            
        Returns:
            Formatted digest content
        """
        current_date = __import__('time').strftime('%B %d, %Y')
        
        # Get style-specific formatting
        style_config = self._get_fallback_style_config(writing_style)
        
        lines = [
            f"# {digest_title}",
            f"*{current_date}*",
            "",
            "## Latest News & Updates",
            ""
        ]
        
        for i, article in enumerate(articles, 1):
            title = article.get('title', f'Article {i}')
            url = article.get('url', '')
            summary = article.get('summary', '')
            
            lines.append(f"### {title}")
            lines.append("")
            
            # Use actual summary if available, otherwise create a style-appropriate excerpt
            if summary and 'Error generating summary' not in summary:
                # Apply style formatting to existing summary
                formatted_summary = self._apply_style_formatting(summary, writing_style)
                lines.append(formatted_summary)
            else:
                # Create a style-appropriate excerpt from content
                content = article.get('content', '')
                if content:
                    excerpt = self._create_style_excerpt(content, writing_style, title, url)
                    lines.append(excerpt)
                else:
                    lines.append(style_config['no_content_message'])
            
            lines.extend([
                "",
                f"*Source: [{title}]({url})*",
                ""
            ])
        
        return "\n".join(lines)
    
    def _get_fallback_style_config(self, writing_style: str) -> Dict[str, str]:
        """Get style configuration for fallback digest generation."""
        configs = {
            "professional": {
                "no_content_message": "Content summary not available. Please visit the source for detailed information.",
                "intro_phrase": "This development represents a significant advancement in the field.",
                "analysis_phrase": "From a business perspective, this innovation demonstrates",
                "conclusion_phrase": "Organizations should consider the strategic implications of this development."
            },
            "casual": {
                "no_content_message": "Content summary not available. Check out the source for more details!",
                "intro_phrase": "This is pretty exciting stuff!",
                "analysis_phrase": "What's really interesting about this is",
                "conclusion_phrase": "This could be a game-changer for the community."
            },
            "technical": {
                "no_content_message": "Technical content summary not available. Please refer to the source for implementation details.",
                "intro_phrase": "The implementation utilizes advanced algorithms to",
                "analysis_phrase": "From a technical perspective, this approach leverages",
                "conclusion_phrase": "The underlying architecture demonstrates significant technical advancement."
            }
        }
        return configs.get(writing_style, configs["professional"])
    
    def _apply_style_formatting(self, summary: str, writing_style: str) -> str:
        """Apply writing style formatting to an existing summary."""
        if writing_style == "casual":
            # Make it more conversational
            if not summary.startswith(("Hey", "Check", "This", "What")):
                summary = f"Check this out: {summary}"
        elif writing_style == "technical":
            # Make it more technical
            if not any(phrase in summary.lower() for phrase in ["implementation", "algorithm", "architecture", "methodology"]):
                summary = f"Technical analysis reveals: {summary}"
        elif writing_style == "professional":
            # Make it more business-focused
            if not any(phrase in summary.lower() for phrase in ["business", "strategic", "organization", "industry"]):
                summary = f"Strategic analysis indicates: {summary}"
        
        return summary
    
    def _create_style_excerpt(self, content: str, writing_style: str, title: str, url: str) -> str:
        """Create a style-appropriate excerpt from content."""
        words = content.split()
        config = self._get_fallback_style_config(writing_style)
        
        # Take more words for technical content, fewer for casual
        word_limit = 100 if writing_style == "technical" else 75 if writing_style == "professional" else 50
        excerpt = ' '.join(words[:word_limit]) + ('...' if len(words) > word_limit else '')
        
        # Add style-specific introduction
        if writing_style == "casual":
            return f"Hey there! {excerpt}"
        elif writing_style == "technical":
            return f"Technical implementation details: {excerpt}"
        else:  # professional
            return f"Business analysis: {excerpt}"

    def _normalize_source_lines(self, text: str) -> str:
        """Collapse repeated identical '*Source: ...*' lines.

        If the same source line appears 3 or more times consecutively, reduce it to exactly 2 occurrences
        (the newsletter format expects two source lines). This also converts any runs of 2+ identical
        consecutive source lines into exactly 2 to avoid accidental duplicates.
        """
        try:
            # Normalize Windows and Unix newlines to \n for consistent processing
            normalized = text.replace('\r\n', '\n')

            # First, process each article block separately to ensure we don't end up
            # with more than two source lines per article. An article block starts
            # with a heading like '### Article N:' and continues until the next
            # article heading or end of document.
            article_block_re = re.compile(r"(### Article \d+: .*?)(?=\n### Article \d+: |\Z)", flags=re.DOTALL)

            def _dedupe_block(m: re.Match) -> str:
                block = m.group(1)
                # Find all source lines in this block and capture title+url
                source_pattern = re.compile(r"\*Source:\s*\[([^\]]+)\]\(([^\)]+)\)(?:\s*-\s*[^\n\*]+)?\*")
                matches = source_pattern.findall(block)

                if not matches:
                    # No well-formed markdown source links; fall back to removing any raw '*Source:' lines
                    if "*Source:" not in block:
                        return block
                    # Remove and return block with no source lines
                    block_without_sources = re.sub(r"\n?\*Source: [^\n]+\*\n?", "\n", block)
                    return block_without_sources

                # Build canonical mapping by URL -> first title seen
                url_to_title = {}
                url_order = []
                for title, url in matches:
                    if url not in url_to_title:
                        url_to_title[url] = title
                        url_order.append(url)

                # Remove all existing source lines from the block
                block_without_sources = re.sub(r"\n?\*Source: [^\n]+\*\n?", "\n", block)
                block_without_sources = block_without_sources.rstrip('\n') + '\n\n'

                # Append only one source line per unique URL
                appended_lines = []
                for url in url_order:
                    title = url_to_title[url]
                    appended_lines.append(f"*Source: [{title}]({url})*")
                    break  # Only add one source line

                block_fixed = block_without_sources + "\n".join(appended_lines) + "\n\n"
                return block_fixed

            normalized = article_block_re.sub(_dedupe_block, normalized)

            # After per-block deduplication, collapse any remaining consecutive
            # repeated source lines (e.g., produced by LLM) into exactly one line.
            pattern2 = re.compile(r"(\*Source: .+?\*\n)(?:\1)+", flags=re.M)
            normalized = pattern2.sub(lambda m: m.group(1), normalized)
            
            # Additional general deduplication for any remaining duplicate source lines
            # This handles cases where the article block pattern didn't match
            lines = normalized.split('\n')
            result_lines = []
            i = 0
            
            while i < len(lines):
                line = lines[i]
                if line.strip().startswith('*Source:') and line.strip().endswith('*'):
                    # Found a source line, check if the next line is a duplicate
                    if i + 1 < len(lines) and lines[i + 1].strip() == line.strip():
                        # Skip the duplicate
                        i += 1
                        continue
                result_lines.append(line)
                i += 1
            
            normalized = '\n'.join(result_lines)

            # Restore CRLF if original text used it
            if '\r\n' in text:
                normalized = normalized.replace('\n', '\r\n')

            return normalized
        except Exception:
            # In case of any unexpected failure, return the original text
            return text
    
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
        # Surface explicit 401 errors for easier debugging
        if resp.status_code == 401:
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            logger.error(f"Groq HTTP 401 Unauthorized: {body}")
            raise ValueError("Groq API returned 401 Unauthorized - check GROQ_API_KEY environment variable and ensure the key is valid.")

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

        try:
            resp.raise_for_status()
        except requests.HTTPError as http_err:
            # Log response body for easier debugging
            try:
                body = resp.json()
            except Exception:
                body = resp.text
            logger.error(f"Groq HTTP error {resp.status_code}: {body}")
            raise

        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    
    def process_single_article_with_prompt(self, article: Dict[str, str], custom_prompt: str) -> Dict[str, str]:
        """
        Process a single article with Groq LLM using a custom prompt.
        
        Args:
            article: Dictionary containing article data
            custom_prompt: Custom prompt to use for processing
            
        Returns:
            Dictionary with processed article data including custom summary
        """
        try:
            # Create a summary using custom prompt
            summary = self.summarize_article_with_prompt(article, custom_prompt)
            
            # Return the article with added summary
            processed_article = article.copy()
            processed_article['summary'] = summary
            
            return processed_article
            
        except Exception as e:
            logger.error(f"Error processing article with custom prompt: {str(e)}")
            # Fallback to standard processing
            return self.process_multiple_articles([article])[0] if article else article
    
    def summarize_article_with_prompt(self, article: Dict[str, str], custom_prompt: str, max_length: int = 1000) -> str:
        """
        Summarize a single article using Groq LLM with a custom prompt.
        
        Args:
            article: Dictionary containing article data (title, content, etc.)
            custom_prompt: Custom prompt to use for summarization
            max_length: Maximum length of the summary
            
        Returns:
            String containing the summary
        """
        try:
            # Prepare the content for the LLM
            title = article.get('title', 'Untitled')
            content = article.get('content', '')
            url = article.get('url', '')
            
            # Create the full prompt with detailed instructions
            full_prompt = f"""
{custom_prompt}

**Article Title**: {title}
**Article URL**: {url}
**Article Content**:
{content}

Please provide a comprehensive analysis and summary based on the custom prompt above. For each section:

1. Provide at least 3 detailed sentences that thoroughly explain the concepts
2. Use specific examples and references from the content
3. Connect ideas between different sections
4. Explain implications and applications
5. For technical content:
   - Break down complex concepts into understandable components
   - Provide real-world examples and applications
   - Explain the significance and broader impact
6. For each key takeaway:
   - Explain the reasoning behind it
   - Provide supporting evidence
   - Describe practical applications

Make all explanations thorough and interconnected, avoiding single-line statements.
"""
            
            # Call Groq API
            if self.client is not None:
                # Use SDK
                response = self.client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": full_prompt
                        }
                    ],
                    model=self.model,
                    max_tokens=max_length,
                    temperature=0.7
                )
                summary = response.choices[0].message.content
            else:
                # Use HTTP requests
                summary = self._make_groq_request(full_prompt, max_length)
            
            if not summary:
                return f"Unable to generate summary for: {title}"
            
            return summary.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing article with custom prompt: {str(e)}")
            return f"Error generating summary: {str(e)}"

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
