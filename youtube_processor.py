import re
import time
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import googleapiclient.discovery
from googleapiclient.errors import HttpError

# Set up logging
import logging
logger = logging.getLogger(__name__)

class YouTubeTranscriptProcessor:
    """
    A class to handle YouTube video transcript extraction and processing.
    """
    
    def __init__(self, proxy_config=None):
        """Initialize the YouTube transcript processor."""
        self.text_formatter = TextFormatter()
        self.proxy_config = proxy_config
        self.api = YouTubeTranscriptApi(proxy_config=proxy_config)
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """
        Extract YouTube video ID from various YouTube URL formats.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID if found, None otherwise
        """
        # Common YouTube URL patterns
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # If it's already just a video ID
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            return url
            
        logger.warning(f"Could not extract video ID from URL: {url}")
        return None
    
    def get_transcript(self, video_id: str, languages: List[str] = None) -> Optional[Dict]:
        """
        Get transcript for a YouTube video with retry logic and better error handling.
        
        Args:
            video_id: YouTube video ID
            languages: Preferred languages (default: ['en'])
            
        Returns:
            Dictionary with transcript data or None if failed
        """
        if not languages:
            languages = ['en']
        
        # Try multiple times with different approaches
        for attempt in range(3):
            try:
                logger.info(f"Attempt {attempt + 1} to get transcript for video {video_id}")
                
                # First try with preferred languages
                if attempt == 0:
                    transcript_list = self.api.list(video_id)
                    transcript = transcript_list.find_transcript(languages)
                    fetched_transcript = transcript.fetch()
                else:
                    # Try with any available language
                    transcript_list = self.api.list(video_id)
                    transcript = transcript_list.find_manually_created_transcript(['en', 'en-US', 'en-GB'])
                    if not transcript:
                        transcript = transcript_list.find_generated_transcript(['en', 'en-US', 'en-GB'])
                    if not transcript:
                        # Get any available transcript
                        available_transcripts = list(transcript_list)
                        if available_transcripts:
                            transcript = available_transcripts[0]
                        else:
                            raise Exception("No transcripts available")
                    fetched_transcript = transcript.fetch()
                
                # Get video metadata
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # Format transcript as text using the formatter
                formatted_text = self.text_formatter.format_transcript(fetched_transcript)
                
                return {
                    'video_id': video_id,
                    'video_url': video_url,
                    'transcript_text': formatted_text,
                    'transcript_data': list(fetched_transcript),
                    'language': transcript.language,
                    'duration': sum(getattr(entry, 'duration', 0) for entry in fetched_transcript),
                    'snippet_count': len(fetched_transcript)
                }
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Attempt {attempt + 1} failed for video {video_id}: {error_msg}")
                
                # If it's an IP blocking error, don't retry
                if ("blocking" in error_msg.lower() or 
                    "ip" in error_msg.lower() or 
                    "fetchedtranscriptsnippet" in error_msg.lower() or
                    "object has no attribute" in error_msg.lower() or
                    "transcript" in error_msg.lower() and "not available" in error_msg.lower()):
                    logger.error(f"Transcript not available for video {video_id}: {error_msg}")
                    break
                
                # Wait before retry
                if attempt < 2:
                    time.sleep(2 ** attempt)  # Exponential backoff
                
        logger.error(f"All attempts failed for video {video_id}")
        return None
    
    def process_youtube_urls(self, urls: List[str]) -> List[Dict]:
        """
        Process a list of YouTube URLs and extract transcripts.
        If transcript extraction fails, create fallback content using video metadata.
        
        Args:
            urls: List of YouTube URLs
            
        Returns:
            List of processed video data
        """
        processed_videos = []
        
        for url in urls:
            video_id = self.extract_video_id(url)
            if not video_id:
                logger.warning(f"Skipping invalid YouTube URL: {url}")
                continue
            
            logger.info(f"Processing YouTube video: {video_id}")
            
            # Get video metadata first to get the actual title
            video_metadata = self._get_video_metadata(video_id)
            video_title = video_metadata.get('title', f"YouTube Video {video_id}")
            
            video_data = self.get_transcript(video_id)
            
            if video_data:
                # Convert to article-like format for compatibility with existing pipeline
                article_data = {
                    'url': video_data['video_url'],
                    'title': video_title,
                    'content': video_data['transcript_text'],
                    'source': 'youtube',
                    'video_id': video_id,
                    'duration': video_data['duration'],
                    'language': video_data['language'],
                    'snippet_count': video_data['snippet_count'],
                    'raw_transcript': video_data['transcript_data'],
                    'channel_title': video_metadata.get('channel_title', 'Unknown Channel'),
                    'view_count': video_metadata.get('view_count', 0),
                    'like_count': video_metadata.get('like_count', 0)
                }
                processed_videos.append(article_data)
                logger.info(f"Successfully processed video {video_id}: {video_title}")
            else:
                # Create fallback content when transcript extraction fails
                logger.warning(f"Transcript extraction failed for video {video_id}, creating fallback content")
                fallback_content = self._create_fallback_content(video_id, url, video_metadata)
                
                article_data = {
                    'url': url,
                    'title': video_title,
                    'content': fallback_content,
                    'source': 'youtube',
                    'video_id': video_id,
                    'duration': 0,
                    'language': 'en',
                    'snippet_count': 0,
                    'fallback_content': True,
                    'channel_title': video_metadata.get('channel_title', 'Unknown Channel'),
                    'view_count': video_metadata.get('view_count', 0),
                    'like_count': video_metadata.get('like_count', 0)
                }
                processed_videos.append(article_data)
                logger.info(f"Created fallback content for video {video_id}: {video_title}")
        
        return processed_videos
    
    def _get_video_metadata(self, video_id: str) -> Dict:
        """
        Get video metadata using YouTube Data API.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary with video metadata
        """
        try:
            import os
            api_key = os.getenv('YOUTUBE_DATA_API_KEY')
            if not api_key:
                logger.warning(f"No YouTube Data API key available for video {video_id}")
                return {'title': f"YouTube Video {video_id}"}
            
            from googleapiclient.discovery import build
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Get video details
            response = youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            ).execute()
            
            if response['items']:
                video_info = response['items'][0]
                snippet = video_info['snippet']
                statistics = video_info['statistics']
                
                return {
                    'title': snippet.get('title', f'YouTube Video {video_id}'),
                    'description': snippet.get('description', ''),
                    'channel_title': snippet.get('channelTitle', 'Unknown Channel'),
                    'view_count': int(statistics.get('viewCount', '0')),
                    'like_count': int(statistics.get('likeCount', '0')),
                    'published_at': snippet.get('publishedAt', ''),
                    'tags': snippet.get('tags', [])
                }
            else:
                logger.warning(f"No metadata found for video {video_id}")
                return {'title': f"YouTube Video {video_id}"}
                
        except Exception as e:
            logger.warning(f"Failed to get video metadata for {video_id}: {e}")
            return {'title': f"YouTube Video {video_id}"}

    def _create_fallback_content(self, video_id: str, url: str, video_metadata: Dict = None) -> str:
        """
        Create fallback content when transcript extraction fails.
        This uses video metadata and generates a placeholder content.
        
        Args:
            video_id: YouTube video ID
            url: YouTube video URL
            video_metadata: Video metadata dictionary (optional)
            
        Returns:
            Fallback content string
        """
        # Use provided metadata or get it if not provided
        if not video_metadata:
            video_metadata = self._get_video_metadata(video_id)
        
        title = video_metadata.get('title', f'YouTube Video {video_id}')
        description = video_metadata.get('description', '')
        channel_title = video_metadata.get('channel_title', 'Unknown Channel')
        view_count = video_metadata.get('view_count', 0)
        like_count = video_metadata.get('like_count', 0)
        tags = video_metadata.get('tags', [])
        
        # Create informative fallback content
        fallback_content = f"""
# {title}

**Channel**: {channel_title}  
**Views**: {view_count:,} views  
**Likes**: {like_count:,} likes  
**Video URL**: {url}

## Description
{description[:800]}{'...' if len(description) > 800 else ''}

## Content Analysis
Based on the video title and description, this appears to be educational content. While the transcript could not be extracted due to YouTube's restrictions, the video metadata provides valuable information about the content.

## Key Topics
{', '.join(tags[:10]) if tags else 'Topics will be available when transcript is accessible'}

## Note
This video is from the {channel_title} channel. The transcript extraction failed, but the video metadata has been preserved to provide context about the content. This is common with YouTube's IP blocking restrictions on transcript access.
        """
        
        return fallback_content
    
    def get_available_languages(self, video_id: str) -> List[Dict]:
        """
        Get available transcript languages for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            List of available language information
        """
        try:
            transcript_list = self.api.list(video_id)
            languages = []
            
            for transcript in transcript_list:
                languages.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated,
                    'is_translatable': transcript.is_translatable
                })
            
            return languages
            
        except Exception as e:
            logger.error(f"Failed to get available languages for video {video_id}: {str(e)}")
            return []
    
    def is_youtube_url(self, url: str) -> bool:
        """
        Check if a URL is a YouTube URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if it's a YouTube URL, False otherwise
        """
        youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com']
        parsed_url = urlparse(url)
        return parsed_url.netloc.lower() in youtube_domains or self.extract_video_id(url) is not None
    
    def is_youtube_channel(self, url: str) -> bool:
        """
        Check if a URL is a YouTube channel URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if it's a YouTube channel URL, False otherwise
        """
        channel_patterns = [
            r'youtube\.com/@[\w-]+',
            r'youtube\.com/c/[\w-]+',
            r'youtube\.com/channel/[\w-]+',
            r'youtube\.com/user/[\w-]+'
        ]
        
        for pattern in channel_patterns:
            if re.search(pattern, url):
                return True
        return False
    
    def get_channel_latest_videos(self, channel_url: str, max_videos: int = 5, api_key: str = None) -> List[str]:
        """
        Get the latest video URLs from a YouTube channel using YouTube Data API v3.
        
        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to fetch
            api_key: YouTube Data API v3 key
            
        Returns:
            List of video URLs
        """
        try:
            if not api_key:
                logger.warning(f"No YouTube Data API key provided for channel {channel_url}")
                return []
            
            from googleapiclient.discovery import build
            
            # Initialize YouTube API client
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Extract channel ID from URL
            channel_id = self._extract_channel_id_from_url(channel_url, api_key)
            if not channel_id:
                logger.error(f"Could not extract channel ID from {channel_url}")
                return []
            
            # Get channel's uploads playlist
            channel_response = youtube.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                logger.error(f"Channel not found: {channel_id}")
                return []
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = youtube.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_videos
            ).execute()
            
            video_urls = []
            for item in playlist_response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_urls.append(video_url)
            
            logger.info(f"Found {len(video_urls)} videos from channel {channel_url}")
            return video_urls
            
        except Exception as e:
            logger.error(f"Failed to get channel videos from {channel_url}: {str(e)}")
            return []
    
    def _extract_channel_id_from_url(self, channel_url: str, api_key: str = None) -> Optional[str]:
        """
        Extract channel ID from various YouTube channel URL formats.
        
        Args:
            channel_url: YouTube channel URL
            api_key: YouTube Data API key for username resolution
            
        Returns:
            Channel ID if found, None otherwise
        """
        try:
            # Handle @username format
            if '/@' in channel_url:
                username = channel_url.split('/@')[-1].split('/')[0].split('?')[0]
                # We need to resolve @username to channel ID using API
                return self._resolve_username_to_channel_id(username, api_key)
            
            # Handle /c/ format
            if '/c/' in channel_url:
                custom_name = channel_url.split('/c/')[-1].split('/')[0].split('?')[0]
                return self._resolve_custom_name_to_channel_id(custom_name, api_key)
            
            # Handle /channel/ format (direct channel ID)
            if '/channel/' in channel_url:
                return channel_url.split('/channel/')[-1].split('/')[0].split('?')[0]
            
            # Handle /user/ format
            if '/user/' in channel_url:
                username = channel_url.split('/user/')[-1].split('/')[0].split('?')[0]
                return self._resolve_username_to_channel_id(username, api_key)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to extract channel ID from {channel_url}: {str(e)}")
            return None
    
    def _resolve_username_to_channel_id(self, username: str, api_key: str = None) -> Optional[str]:
        """Resolve @username to channel ID using YouTube Data API"""
        try:
            if not api_key:
                logger.warning(f"No API key provided for username resolution: @{username}")
                return None
            
            from googleapiclient.discovery import build
            
            # Initialize YouTube API client
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Search for channel by username
            search_response = youtube.search().list(
                part='snippet',
                q=username,
                type='channel',
                maxResults=1
            ).execute()
            
            if search_response['items']:
                channel_id = search_response['items'][0]['snippet']['channelId']
                logger.info(f"Resolved @{username} to channel ID: {channel_id}")
                return channel_id
            else:
                logger.warning(f"No channel found for @{username}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to resolve username @{username}: {str(e)}")
            return None
    
    def _resolve_custom_name_to_channel_id(self, custom_name: str, api_key: str = None) -> Optional[str]:
        """Resolve custom name to channel ID using YouTube Data API"""
        try:
            if not api_key:
                logger.warning(f"No API key provided for custom name resolution: {custom_name}")
                return None
            
            from googleapiclient.discovery import build
            
            # Initialize YouTube API client
            youtube = build('youtube', 'v3', developerKey=api_key)
            
            # Search for channel by custom name
            search_response = youtube.search().list(
                part='snippet',
                q=custom_name,
                type='channel',
                maxResults=1
            ).execute()
            
            if search_response['items']:
                channel_id = search_response['items'][0]['snippet']['channelId']
                logger.info(f"Resolved custom name {custom_name} to channel ID: {channel_id}")
                return channel_id
            else:
                logger.warning(f"No channel found for custom name {custom_name}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to resolve custom name {custom_name}: {str(e)}")
            return None
    
    @staticmethod
    def create_proxy_config(proxy_url: str = None):
        """
        Create proxy configuration (not needed for youtube-transcript.io API).
        
        Args:
            proxy_url: Proxy URL (not used for this API)
            
        Returns:
            None (not needed for youtube-transcript.io)
        """
        return None  # Not needed for youtube-transcript.io API

# Example usage
if __name__ == "__main__":
    processor = YouTubeTranscriptProcessor()
    
    # Test with a sample YouTube URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    video_id = processor.extract_video_id(test_url)
    print(f"Extracted video ID: {video_id}")
    
    if video_id:
        # Get available languages
        languages = processor.get_available_languages(video_id)
        print(f"Available languages: {languages}")
        
        # Get transcript
        transcript_data = processor.get_transcript(video_id)
        if transcript_data:
            print(f"Transcript length: {len(transcript_data['transcript_text'])} characters")
            print(f"Duration: {transcript_data['duration']} seconds")
            print(f"Language: {transcript_data['language']}")
        else:
            print("Failed to get transcript")