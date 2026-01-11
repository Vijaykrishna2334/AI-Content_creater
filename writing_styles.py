"""
Writing Styles Configuration for Newsletter Generation
"""

from typing import Dict, List, Optional
import json
import os

class WritingStyleManager:
    """Manages different writing styles for newsletter generation."""
    
    def __init__(self):
        self.styles = self._load_default_styles()
        self.custom_styles = {}
    
    def _load_default_styles(self) -> Dict[str, Dict]:
        """Load the default writing styles."""
        return {
            "professional": {
                "name": "Professional Newsletter",
                "description": "Formal, structured, and business-focused style suitable for corporate newsletters",
                "characteristics": [
                    "Formal tone and language",
                    "Structured sections with clear headers",
                    "Executive summary format",
                    "Data-driven insights",
                    "Professional terminology"
                ],
                "prompt_template": """
                Create a professional newsletter in the following style:
                
                **TONE**: Formal, authoritative, and business-focused
                **STRUCTURE**: Executive summary, key findings, detailed analysis, conclusions
                **LANGUAGE**: Professional terminology, data-driven insights, clear and concise
                **FORMAT**: Corporate newsletter with executive summary and detailed sections
                
                Focus on:
                - Business impact and ROI
                - Data-driven insights and metrics
                - Professional analysis and recommendations
                - Executive-level summaries
                - Industry trends and implications
                - ALWAYS include source links for each article using format: *Source: [Article Title](URL)*
                
                Content to process:
                {content}
                """,
                "digest_template": """
                # {title}
                *{date}*
                
                ## Latest News & Updates
                {content}
                """
            },
            
            "casual": {
                "name": "Casual & Engaging",
                "description": "Friendly, conversational, and engaging style perfect for community newsletters",
                "characteristics": [
                    "Conversational tone",
                    "Engaging and friendly language",
                    "Personal touch and storytelling",
                    "Community-focused content",
                    "Easy to read and digest"
                ],
                "prompt_template": """
                Create an engaging newsletter in the following style:
                
                **TONE**: Friendly, conversational, and engaging
                **STRUCTURE**: Welcome message, highlights, stories, community insights
                **LANGUAGE**: Conversational, accessible, with personal touches
                **FORMAT**: Community newsletter with engaging stories and insights
                
                Focus on:
                - Personal stories and experiences
                - Community highlights and achievements
                - Engaging and relatable content
                - Easy-to-understand explanations
                - Friendly and welcoming tone
                - ALWAYS include source links for each article using format: *Source: [Article Title](URL)*
                
                Content to process:
                {content}
                """,
                "digest_template": """
                # {title} 🚀
                *{date}*
                
                ## Latest News & Updates
                {content}
                """
            },
            
            "technical": {
                "name": "Technical Deep Dive",
                "description": "Detailed, technical, and educational style for technical audiences and developers",
                "characteristics": [
                    "Technical terminology and concepts",
                    "Detailed explanations and analysis",
                    "Code examples and technical details",
                    "Educational focus",
                    "Comprehensive coverage"
                ],
                "prompt_template": """
                Create a technical newsletter in the following style:
                
                **TONE**: Technical, detailed, and educational
                **STRUCTURE**: Technical overview, deep dives, code examples, implementation details
                **LANGUAGE**: Technical terminology, detailed explanations, educational focus
                **FORMAT**: Technical newsletter with code examples and detailed analysis
                
                Focus on:
                - Technical concepts and implementations
                - Code examples and snippets
                - Detailed technical analysis
                - Educational content and tutorials
                - Developer-focused insights
                - ALWAYS include source links for each article using format: *Source: [Article Title](URL)*
                
                Content to process:
                {content}
                """,
                "digest_template": """
                # {title}
                *{date}*
                
                ## Latest News & Updates
                {content}
                """
            }
        }
    
    def get_available_styles(self) -> List[Dict[str, str]]:
        """Get list of available writing styles."""
        styles = []
        
        # Add default styles
        for style_id, style_data in self.styles.items():
            styles.append({
                "id": style_id,
                "name": style_data["name"],
                "description": style_data["description"]
            })
        
        # Add custom styles
        for style_id, style_data in self.custom_styles.items():
            styles.append({
                "id": style_id,
                "name": style_data["name"],
                "description": style_data["description"],
                "custom": True
            })
        
        return styles
    
    def get_style_prompt(self, style_id: str, content: str) -> str:
        """Get the prompt template for a specific writing style."""
        style_data = self.styles.get(style_id) or self.custom_styles.get(style_id)
        if not style_data:
            raise ValueError(f"Writing style '{style_id}' not found")
        
        return style_data["prompt_template"].format(content=content)
    
    def get_style_digest_template(self, style_id: str) -> str:
        """Get the digest template for a specific writing style."""
        style_data = self.styles.get(style_id) or self.custom_styles.get(style_id)
        if not style_data:
            raise ValueError(f"Writing style '{style_id}' not found")
        
        return style_data["digest_template"]
    
    def create_custom_style_from_document(self, 
                                        document_content: str, 
                                        style_name: str,
                                        style_description: str) -> str:
        """Create a custom writing style based on a training document."""
        # Analyze the document to extract writing patterns
        analysis = self._analyze_document_style(document_content)
        
        # Generate custom style configuration
        custom_style = {
            "name": style_name,
            "description": style_description,
            "characteristics": analysis["characteristics"],
            "prompt_template": self._generate_custom_prompt_template(analysis),
            "digest_template": self._generate_custom_digest_template(analysis)
        }
        
        # Generate unique style ID
        style_id = f"custom_{len(self.custom_styles) + 1}"
        self.custom_styles[style_id] = custom_style
        
        return style_id
    
    def _analyze_document_style(self, document_content: str) -> Dict:
        """Analyze a document to extract writing style characteristics."""
        # Simple analysis - in production, you'd use more sophisticated NLP
        content_lower = document_content.lower()
        
        characteristics = []
        
        # Analyze tone
        if any(word in content_lower for word in ["professional", "business", "corporate", "executive"]):
            characteristics.append("Professional and formal tone")
        elif any(word in content_lower for word in ["hey", "hi", "hello", "thanks", "awesome", "great"]):
            characteristics.append("Casual and friendly tone")
        elif any(word in content_lower for word in ["technical", "code", "implementation", "algorithm"]):
            characteristics.append("Technical and detailed tone")
        
        # Analyze structure
        if "##" in document_content or "###" in document_content:
            characteristics.append("Structured with clear headers")
        
        # Analyze language patterns
        if any(word in content_lower for word in ["data", "analysis", "metrics", "roi"]):
            characteristics.append("Data-driven insights")
        
        if any(word in content_lower for word in ["story", "experience", "personal", "community"]):
            characteristics.append("Storytelling and personal touch")
        
        if any(word in content_lower for word in ["code", "function", "class", "method", "api"]):
            characteristics.append("Technical implementation details")
        
        return {
            "characteristics": characteristics,
            "tone": "professional" if "professional" in characteristics[0].lower() else 
                   "casual" if "casual" in characteristics[0].lower() else "technical",
            "structure": "structured" if "structured" in characteristics else "narrative"
        }
    
    def _generate_custom_prompt_template(self, analysis: Dict) -> str:
        """Generate a custom prompt template based on document analysis."""
        tone = analysis["tone"]
        characteristics = analysis["characteristics"]
        
        base_template = f"""
        Create a newsletter in the following custom style:
        
        **TONE**: {tone.title()}
        **CHARACTERISTICS**: {', '.join(characteristics)}
        **STRUCTURE**: Based on the training document style
        **LANGUAGE**: Matching the training document patterns
        
        Focus on:
        - Maintaining the same tone and style as the training document
        - Using similar language patterns and terminology
        - Following the same structural approach
        - Preserving the unique voice and characteristics
        - ALWAYS include source links for each article using format: *Source: [Article Title](URL)*
        
        Content to process:
        {{content}}
        """
        
        return base_template
    
    def _generate_custom_digest_template(self, analysis: Dict) -> str:
        """Generate a custom digest template based on document analysis."""
        # For now, return a flexible template that can adapt
        return """
        # {title}
        
        **{date}** | **Custom Style Newsletter**
        
        {content}
        
        ---
        *Generated using custom writing style*
        """
    
    def save_custom_styles(self, filepath: str = "custom_styles.json"):
        """Save custom styles to a file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.custom_styles, f, indent=2, ensure_ascii=False)
    
    def load_custom_styles(self, filepath: str = "custom_styles.json"):
        """Load custom styles from a file."""
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                self.custom_styles = json.load(f)

# Global instance
writing_style_manager = WritingStyleManager()
