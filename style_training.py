"""
Style Training module for CreatorPulse
Handles user voice analysis and style profile creation
"""

import re
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StyleAnalyzer:
    def __init__(self):
        self.voice_characteristics = {
            'tone': ['formal', 'casual', 'professional', 'friendly', 'sarcastic', 'serious'],
            'formality': ['very_formal', 'formal', 'neutral', 'casual', 'very_casual'],
            'persona': ['first_person', 'third_person', 'editorial', 'conversational'],
            'humor_level': ['none', 'subtle', 'moderate', 'high'],
            'sentence_length': ['short', 'medium', 'long', 'varied'],
            'vocabulary': ['simple', 'moderate', 'complex', 'technical']
        }
    
    def analyze_newsletter(self, content: str) -> Dict[str, Any]:
        """Analyze a single newsletter for style characteristics"""
        analysis = {
            'word_count': len(content.split()),
            'sentence_count': len(re.findall(r'[.!?]+', content)),
            'avg_sentence_length': 0,
            'tone_indicators': {},
            'formality_score': 0,
            'persona_type': 'unknown',
            'humor_indicators': 0,
            'technical_terms': 0,
            'punctuation_style': {},
            'structure_patterns': {}
        }
        
        if analysis['sentence_count'] > 0:
            analysis['avg_sentence_length'] = analysis['word_count'] / analysis['sentence_count']
        
        # Analyze tone indicators
        tone_patterns = {
            'formal': [r'\b(however|therefore|furthermore|moreover|consequently)\b'],
            'casual': [r'\b(hey|hi|hello|yeah|ok|cool|awesome)\b'],
            'professional': [r'\b(analysis|research|data|findings|conclusion)\b'],
            'sarcastic': [r'\b(obviously|clearly|of course|surely)\b', r'[!]{2,}'],
            'friendly': [r'\b(you|your|we|our|us)\b', r'[!]']
        }
        
        for tone, patterns in tone_patterns.items():
            count = 0
            for pattern in patterns:
                count += len(re.findall(pattern, content, re.IGNORECASE))
            analysis['tone_indicators'][tone] = count
        
        # Analyze formality
        formal_words = len(re.findall(r'\b(utilize|facilitate|implement|establish|commence)\b', content, re.IGNORECASE))
        casual_words = len(re.findall(r'\b(use|help|do|start|begin)\b', content, re.IGNORECASE))
        analysis['formality_score'] = (formal_words - casual_words) / max(analysis['word_count'], 1)
        
        # Analyze persona
        first_person = len(re.findall(r'\b(I|me|my|mine|we|us|our)\b', content, re.IGNORECASE))
        third_person = len(re.findall(r'\b(he|she|they|them|their|it|its)\b', content, re.IGNORECASE))
        
        if first_person > third_person:
            analysis['persona_type'] = 'first_person'
        elif third_person > first_person:
            analysis['persona_type'] = 'third_person'
        else:
            analysis['persona_type'] = 'mixed'
        
        # Analyze humor
        humor_patterns = [
            r'[!]{2,}',  # Multiple exclamation marks
            r'\b(lol|haha|hehe|rofl|lmao)\b',  # Laughing expressions
            r'\b(joke|funny|hilarious|amusing)\b',  # Humor words
            r'[?]{2,}',  # Multiple question marks
        ]
        
        for pattern in humor_patterns:
            analysis['humor_indicators'] += len(re.findall(pattern, content, re.IGNORECASE))
        
        # Analyze technical terms
        technical_patterns = [
            r'\b(API|SDK|framework|algorithm|database|server|client)\b',
            r'\b(JavaScript|Python|React|Node|Docker|Kubernetes)\b',
            r'\b(API|URL|HTTP|HTTPS|JSON|XML|REST|GraphQL)\b'
        ]
        
        for pattern in technical_patterns:
            analysis['technical_terms'] += len(re.findall(pattern, content, re.IGNORECASE))
        
        # Analyze punctuation style
        analysis['punctuation_style'] = {
            'exclamation_ratio': len(re.findall(r'[!]', content)) / max(analysis['sentence_count'], 1),
            'question_ratio': len(re.findall(r'[?]', content)) / max(analysis['sentence_count'], 1),
            'ellipsis_count': len(re.findall(r'\.{3,}', content)),
            'dash_count': len(re.findall(r'[-—]', content))
        }
        
        # Analyze structure patterns
        analysis['structure_patterns'] = {
            'has_intro': bool(re.search(r'^(welcome|hello|hi|introduction)', content, re.IGNORECASE)),
            'has_conclusion': bool(re.search(r'(conclusion|summary|wrap|up|closing)', content, re.IGNORECASE)),
            'uses_bullets': bool(re.search(r'^[\s]*[-*•]', content, re.MULTILINE)),
            'uses_numbered_lists': bool(re.search(r'^\s*\d+\.', content, re.MULTILINE)),
            'uses_headers': bool(re.search(r'^#{1,6}\s+', content, re.MULTILINE))
        }
        
        return analysis
    
    def create_style_profile(self, newsletters: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a comprehensive style profile from multiple newsletters"""
        if len(newsletters) < 5:
            return {"error": "Need at least 5 newsletters for accurate style analysis"}
        
        analyses = []
        for newsletter in newsletters:
            content = newsletter.get('content', '')
            if content:
                analysis = self.analyze_newsletter(content)
                analyses.append(analysis)
        
        if not analyses:
            return {"error": "No valid newsletter content found"}
        
        # Aggregate analysis results
        profile = {
            'created_at': datetime.now().isoformat(),
            'newsletter_count': len(analyses),
            'avg_word_count': sum(a['word_count'] for a in analyses) / len(analyses),
            'avg_sentence_length': sum(a['avg_sentence_length'] for a in analyses) / len(analyses),
            'dominant_tone': self._get_dominant_tone(analyses),
            'formality_level': self._get_formality_level(analyses),
            'persona_type': self._get_dominant_persona(analyses),
            'humor_level': self._get_humor_level(analyses),
            'technical_level': self._get_technical_level(analyses),
            'punctuation_style': self._get_punctuation_style(analyses),
            'structure_preferences': self._get_structure_preferences(analyses),
            'voice_characteristics': self._extract_voice_characteristics(analyses),
            'writing_patterns': self._extract_writing_patterns(analyses)
        }
        
        return profile
    
    def _get_dominant_tone(self, analyses: List[Dict[str, Any]]) -> str:
        """Determine the dominant tone across all analyses"""
        tone_scores = {}
        for analysis in analyses:
            for tone, count in analysis['tone_indicators'].items():
                tone_scores[tone] = tone_scores.get(tone, 0) + count
        
        if not tone_scores:
            return 'neutral'
        
        return max(tone_scores.items(), key=lambda x: x[1])[0]
    
    def _get_formality_level(self, analyses: List[Dict[str, Any]]) -> str:
        """Determine the formality level"""
        avg_formality = sum(a['formality_score'] for a in analyses) / len(analyses)
        
        if avg_formality > 0.1:
            return 'formal'
        elif avg_formality < -0.1:
            return 'casual'
        else:
            return 'neutral'
    
    def _get_dominant_persona(self, analyses: List[Dict[str, Any]]) -> str:
        """Determine the dominant persona type"""
        persona_counts = {}
        for analysis in analyses:
            persona = analysis['persona_type']
            persona_counts[persona] = persona_counts.get(persona, 0) + 1
        
        return max(persona_counts.items(), key=lambda x: x[1])[0]
    
    def _get_humor_level(self, analyses: List[Dict[str, Any]]) -> str:
        """Determine the humor level"""
        avg_humor = sum(a['humor_indicators'] for a in analyses) / len(analyses)
        
        if avg_humor > 3:
            return 'high'
        elif avg_humor > 1:
            return 'moderate'
        elif avg_humor > 0:
            return 'subtle'
        else:
            return 'none'
    
    def _get_technical_level(self, analyses: List[Dict[str, Any]]) -> str:
        """Determine the technical level"""
        avg_technical = sum(a['technical_terms'] for a in analyses) / len(analyses)
        
        if avg_technical > 5:
            return 'high'
        elif avg_technical > 2:
            return 'moderate'
        else:
            return 'low'
    
    def _get_punctuation_style(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate punctuation style preferences"""
        return {
            'exclamation_ratio': sum(a['punctuation_style']['exclamation_ratio'] for a in analyses) / len(analyses),
            'question_ratio': sum(a['punctuation_style']['question_ratio'] for a in analyses) / len(analyses),
            'uses_ellipsis': any(a['punctuation_style']['ellipsis_count'] > 0 for a in analyses),
            'uses_dashes': any(a['punctuation_style']['dash_count'] > 0 for a in analyses)
        }
    
    def _get_structure_preferences(self, analyses: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Determine structure preferences"""
        return {
            'prefers_intro': sum(1 for a in analyses if a['structure_patterns']['has_intro']) / len(analyses) > 0.5,
            'prefers_conclusion': sum(1 for a in analyses if a['structure_patterns']['has_conclusion']) / len(analyses) > 0.5,
            'uses_bullets': sum(1 for a in analyses if a['structure_patterns']['uses_bullets']) / len(analyses) > 0.3,
            'uses_numbered_lists': sum(1 for a in analyses if a['structure_patterns']['uses_numbered_lists']) / len(analyses) > 0.3,
            'uses_headers': sum(1 for a in analyses if a['structure_patterns']['uses_headers']) / len(analyses) > 0.3
        }
    
    def _extract_voice_characteristics(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract unique voice characteristics"""
        return {
            'sentence_variety': 'high' if max(a['avg_sentence_length'] for a in analyses) - min(a['avg_sentence_length'] for a in analyses) > 10 else 'low',
            'word_choice': 'complex' if sum(a['technical_terms'] for a in analyses) / len(analyses) > 2 else 'simple',
            'engagement_style': 'interactive' if sum(a['punctuation_style']['question_ratio'] for a in analyses) / len(analyses) > 0.1 else 'informative'
        }
    
    def _extract_writing_patterns(self, analyses: List[Dict[str, Any]]) -> List[str]:
        """Extract common writing patterns"""
        patterns = []
        
        # Check for common patterns
        if any(a['structure_patterns']['uses_headers'] for a in analyses):
            patterns.append('uses_headers')
        if any(a['structure_patterns']['uses_bullets'] for a in analyses):
            patterns.append('uses_bullets')
        if any(a['punctuation_style']['ellipsis_count'] > 0 for a in analyses):
            patterns.append('uses_ellipsis')
        if any(a['humor_indicators'] > 0 for a in analyses):
            patterns.append('includes_humor')
        
        return patterns

def generate_style_prompt(style_profile: Dict[str, Any], content_type: str = "newsletter") -> str:
    """Generate a prompt that incorporates the user's style profile"""
    
    # Handle both predefined and trained styles
    if style_profile.get('style_type') == 'predefined':
        # For predefined styles, use the available fields
        tone = style_profile.get('tone', 'neutral')
        formality = style_profile.get('formality', 'neutral')
        persona = style_profile.get('persona', 'first_person')
        characteristics = style_profile.get('characteristics', [])
        
        # Build the style instruction for predefined styles
        style_instruction = f"""
        Write in the style of this creator:
        - Tone: {tone}
        - Formality: {formality}
        - Persona: {persona}
        - Style: {style_profile.get('style_name', 'Custom Style')}
        """
        
        # Add characteristics
        if characteristics:
            style_instruction += "\n- Characteristics:\n"
            for char in characteristics:
                style_instruction += f"  • {char}\n"
        
    else:
        # For trained styles, use the original field names
        tone = style_profile.get('dominant_tone', 'neutral')
        formality = style_profile.get('formality_level', 'neutral')
        persona = style_profile.get('persona_type', 'first_person')
        humor = style_profile.get('humor_level', 'none')
        technical = style_profile.get('technical_level', 'low')
        
        # Build the style instruction for trained styles
        style_instruction = f"""
        Write in the style of this creator:
        - Tone: {tone}
        - Formality: {formality}
        - Persona: {persona}
        - Humor level: {humor}
        - Technical level: {technical}
        """
        
        # Add specific characteristics for trained styles
        if style_profile.get('punctuation_style', {}).get('uses_ellipsis'):
            style_instruction += "\n- Use ellipsis (...) for dramatic effect"
        
        if style_profile.get('structure_preferences', {}).get('uses_headers'):
            style_instruction += "\n- Use clear headers and subheaders"
        
        if style_profile.get('structure_preferences', {}).get('uses_bullets'):
            style_instruction += "\n- Use bullet points for lists"
        
        if style_profile.get('voice_characteristics', {}).get('engagement_style') == 'interactive':
            style_instruction += "\n- Include questions to engage readers"
    
    return style_instruction
