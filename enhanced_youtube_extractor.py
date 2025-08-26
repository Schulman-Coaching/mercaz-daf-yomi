#!/usr/bin/env python3
"""
Enhanced YouTube Transcript Extraction System for Mercaz Daf Yomi Channel
Supports bulk processing of 5,000+ videos with comprehensive features.
"""

import os
import csv
import json
import time
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import re

# Third-party imports
from youtube_transcript_api import YouTubeTranscriptApi
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import requests

class MercazDafYomiExtractor:
    """Enhanced YouTube transcript extractor for Mercaz Daf Yomi channel."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the extractor with configuration."""
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.youtube_service = None
        self.progress_file = "extraction_progress.json"
        self.master_catalog = []
        self.failed_videos = []
        
        # Initialize YouTube Data API if key provided
        if self.config.get('youtube_api_key'):
            try:
                self.youtube_service = build('youtube', 'v3', 
                                           developerKey=self.config['youtube_api_key'])
                self.logger.info("YouTube Data API v3 initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize YouTube API: {e}")
    
    def load_config(self, config_file: str) -> Dict:
        """Load configuration from JSON file."""
        default_config = {
            "youtube_api_key": "",
            "channel_handle": "@MercazDafYomi",
            "channel_id": "",
            "output_directory": "Mercaz_Daf_Yomi_Transcripts",
            "batch_size": 50,
            "rate_limit_seconds": 2,
            "max_retries": 3,
            "resume_on_restart": True,
            "organize_by_tractate": True,
            "tractate_patterns": {
                "Berachos": ["berachos", "berakhot"],
                "Shabbos": ["shabbos", "shabbat"],
                "Eruvin": ["eruvin"],
                "Pesachim": ["pesachim"],
                "Shekalim": ["shekalim"],
                "Yoma": ["yoma"],
                "Sukkah": ["sukkah"],
                "Beitzah": ["beitzah", "beitza"],
                "Rosh_Hashanah": ["rosh hashanah", "rosh_hashanah"],
                "Taanis": ["taanis", "taanit"],
                "Megillah": ["megillah"],
                "Moed_Katan": ["moed katan", "moed_katan"],
                "Chagigah": ["chagigah"],
                "Yevamos": ["yevamos", "yevamot"],
                "Kesubos": ["kesubos", "ketubbot"],
                "Nedarim": ["nedarim"],
                "Nazir": ["nazir"],
                "Sotah": ["sotah"],
                "Gittin": ["gittin"],
                "Kiddushin": ["kiddushin"],
                "Bava_Kamma": ["bava kamma", "bava_kamma"],
                "Bava_Metzia": ["bava metzia", "bava_metzia"],
                "Bava_Basra": ["bava basra", "bava_basra"],
                "Sanhedrin": ["sanhedrin"],
                "Makkos": ["makkos", "makkot"],
                "Shevuos": ["shevuos", "shevuot"],
                "Avodah_Zarah": ["avodah zarah", "avodah_zarah"],
                "Horayos": ["horayos", "horayot"],
                "Zevachim": ["zevachim"],
                "Menachos": ["menachos", "menachot"],
                "Chullin": ["chullin"],
                "Bechorot": ["bechorot", "bechoros"],
                "Arachin": ["arachin"],
                "Temurah": ["temurah"],
                "Kerisos": ["kerisos", "keritot"],
                "Meilah": ["meilah"],
                "Kinnim": ["kinnim"],
                "Tamid": ["tamid"],
                "Midos": ["midos", "midot"],
                "Niddah": ["niddah"]
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load config file {config_file}: {e}")
            print("Using default configuration")
        
        return default_config
    
    def setup_logging(self):
        """Setup comprehensive logging."""
        log_dir = Path(self.config['output_directory']) / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Enhanced YouTube Transcript Extractor initialized")
        self.logger.info(f"Output directory: {self.config['output_directory']}")
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def get_channel_videos(self, channel_handle: str = None, max_results: int = None) -> List[Dict]:
        """Get all videos from the Mercaz Daf Yomi channel using YouTube Data API."""
        if not self.youtube_service:
            self.logger.error("YouTube Data API not initialized. Cannot fetch channel videos.")
            return []
        
        channel_handle = channel_handle or self.config['channel_handle']
        videos = []
        
        try:
            # First, get channel ID from handle
            if not self.config.get('channel_id'):
                channel_response = self.youtube_service.channels().list(
                    part='id,snippet',
                    forHandle=channel_handle.replace('@', '')
                ).execute()
                
                if not channel_response['items']:
                    self.logger.error(f"Channel not found: {channel_handle}")
                    return []
                
                channel_id = channel_response['items'][0]['id']
                self.config['channel_id'] = channel_id
                self.logger.info(f"Found channel ID: {channel_id}")
            else:
                channel_id = self.config['channel_id']
            
            # Get all playlists from the channel
            playlists_response = self.youtube_service.playlists().list(
                part='id,snippet',
                channelId=channel_id,
                maxResults=50
            ).execute()
            
            # Get videos from uploads playlist (main channel videos)
            channel_response = self.youtube_service.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Fetch all videos from uploads playlist
            next_page_token = None
            video_count = 0
            
            while True:
                playlist_response = self.youtube_service.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                
                for item in playlist_response['items']:
                    if max_results and video_count >= max_results:
                        break
                    
                    video_data = {
                        'video_id': item['contentDetails']['videoId'],
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'published_at': item['snippet']['publishedAt'],
                        'thumbnail_url': item['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                        'url': f"https://www.youtube.com/watch?v={item['contentDetails']['videoId']}"
                    }
                    
                    videos.append(video_data)
                    video_count += 1
                
                next_page_token = playlist_response.get('nextPageToken')
                if not next_page_token or (max_results and video_count >= max_results):
                    break
                
                # Rate limiting
                time.sleep(0.1)
            
            self.logger.info(f"Found {len(videos)} videos from channel {channel_handle}")
            return videos
            
        except HttpError as e:
            self.logger.error(f"YouTube API error: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error fetching channel videos: {e}")
            return []
    
    def classify_video(self, title: str, description: str = "") -> Tuple[str, str]:
        """Classify video by tractate and series type."""
        title_lower = title.lower()
        description_lower = description.lower()
        combined_text = f"{title_lower} {description_lower}"
        
        # Check for tractate patterns
        for tractate, patterns in self.config['tractate_patterns'].items():
            for pattern in patterns:
                if pattern in combined_text:
                    # Determine series type
                    if 'daf yomi' in combined_text:
                        series_type = 'Daf_Yomi'
                    elif 'shiur' in combined_text:
                        series_type = 'Shiurim'
                    elif 'lecture' in combined_text:
                        series_type = 'Lectures'
                    else:
                        series_type = 'General'
                    
                    return tractate, series_type
        
        # Default classification
        if 'daf yomi' in combined_text:
            return 'Unclassified', 'Daf_Yomi'
        elif any(word in combined_text for word in ['special', 'event', 'announcement']):
            return 'Special_Series', 'Events'
        else:
            return 'Unclassified', 'General'
    
    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """Get detailed video metadata using YouTube Data API."""
        if not self.youtube_service:
            return None
        
        try:
            response = self.youtube_service.videos().list(
                part='snippet,contentDetails,statistics',
                id=video_id
            ).execute()
            
            if not response['items']:
                return None
            
            item = response['items'][0]
            
            # Parse duration
            duration_str = item['contentDetails']['duration']
            duration_seconds = self.parse_duration(duration_str)
            
            metadata = {
                'video_id': video_id,
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'duration': duration_str,
                'duration_seconds': duration_seconds,
                'view_count': int(item['statistics'].get('viewCount', 0)),
                'like_count': int(item['statistics'].get('likeCount', 0)),
                'comment_count': int(item['statistics'].get('commentCount', 0)),
                'thumbnail_url': item['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                'channel_title': item['snippet']['channelTitle'],
                'tags': item['snippet'].get('tags', [])
            }
            
            return metadata
            
        except Exception as e:
            self.logger.warning(f"Could not fetch metadata for {video_id}: {e}")
            return None
    
    def parse_duration(self, duration_str: str) -> int:
        """Parse ISO 8601 duration to seconds."""
        import re
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration_str)
        
        if not match:
            return 0
        
        hours = int(match.group(1) or 0)
        minutes = int(match.group(2) or 0)
        seconds = int(match.group(3) or 0)
        
        return hours * 3600 + minutes * 60 + seconds
    
    def extract_transcript(self, video_id: str) -> Tuple[Optional[str], Optional[List], Dict]:
        """Extract transcript with comprehensive error handling and metadata."""
        result = {
            'success': False,
            'transcript_type': None,
            'language': None,
            'error': None,
            'word_count': 0,
            'duration_covered': 0
        }
        
        try:
            # Get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Priority order for transcript languages
            language_priorities = ['en', 'en-US', 'en-GB', 'he', 'iw']
            transcript = None
            
            # Try to get preferred language transcript
            for lang in language_priorities:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    result['language'] = lang
                    break
                except:
                    continue
            
            # If no preferred language found, get first available
            if not transcript:
                try:
                    available_transcripts = list(transcript_list)
                    if available_transcripts:
                        transcript = available_transcripts[0]
                        result['language'] = transcript.language_code
                except:
                    pass
            
            if not transcript:
                result['error'] = "No transcripts available"
                return None, None, result
            
            # Determine transcript type
            result['transcript_type'] = 'manual' if not transcript.is_generated else 'auto-generated'
            
            # Fetch the transcript data
            transcript_data = transcript.fetch()
            
            if not transcript_data:
                result['error'] = "Empty transcript data"
                return None, None, result
            
            # Convert to plain text
            full_text = ""
            for entry in transcript_data:
                full_text += entry['text'] + " "
            
            full_text = full_text.strip()
            
            # Update result metadata
            result['success'] = True
            result['word_count'] = len(full_text.split())
            result['duration_covered'] = transcript_data[-1]['start'] + transcript_data[-1]['duration'] if transcript_data else 0
            
            return full_text, transcript_data, result
            
        except Exception as e:
            result['error'] = str(e)
            self.logger.warning(f"Error extracting transcript for {video_id}: {e}")
            return None, None, result
    
    def save_transcript(self, video_data: Dict, transcript_text: str, 
                       transcript_data: List, metadata: Dict) -> str:
        """Save transcript to organized file structure."""
        # Classify video
        tractate, series_type = self.classify_video(
            video_data['title'], 
            video_data.get('description', '')
        )
        
        # Create directory structure
        base_dir = Path(self.config['output_directory'])
        if self.config['organize_by_tractate']:
            output_dir = base_dir / tractate / series_type
        else:
            output_dir = base_dir / "All_Transcripts"
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create safe filename
        safe_title = re.sub(r'[^\w\s-]', '', video_data['title'])
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        filename = f"{safe_title}_{video_data['video_id']}.txt"
        filepath = output_dir / filename
        
        # Write transcript file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Title: {video_data['title']}\n")
            f.write(f"Video ID: {video_data['video_id']}\n")
            f.write(f"URL: {video_data['url']}\n")
            f.write(f"Published: {video_data.get('published_at', 'Unknown')}\n")
            f.write(f"Tractate: {tractate}\n")
            f.write(f"Series: {series_type}\n")
            f.write(f"Transcript Type: {metadata.get('transcript_type', 'Unknown')}\n")
            f.write(f"Language: {metadata.get('language', 'Unknown')}\n")
            f.write(f"Word Count: {metadata.get('word_count', 0)}\n")
            f.write(f"Duration Covered: {metadata.get('duration_covered', 0):.1f} seconds\n")
            f.write("-" * 80 + "\n\n")
            f.write(transcript_text)
            
            # Add structured data section
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("STRUCTURED TRANSCRIPT DATA (JSON)\n")
            f.write("=" * 80 + "\n")
            f.write(json.dumps(transcript_data, indent=2, ensure_ascii=False))
        
        return str(filepath)
    
    def load_progress(self) -> Dict:
        """Load extraction progress from file."""
        if not os.path.exists(self.progress_file):
            return {
                'completed_videos': [],
                'failed_videos': [],
                'last_batch': 0,
                'total_processed': 0,
                'start_time': None
            }
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load progress file: {e}")
            return {
                'completed_videos': [],
                'failed_videos': [],
                'last_batch': 0,
                'total_processed': 0,
                'start_time': None
            }
    
    def save_progress(self, progress: Dict):
        """Save extraction progress to file."""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Could not save progress: {e}")
    
    def process_video_batch(self, videos: List[Dict], batch_num: int, 
                           total_batches: int, progress: Dict) -> List[Dict]:
        """Process a batch of videos with comprehensive error handling."""
        batch_results = []
        
        self.logger.info(f"Processing batch {batch_num}/{total_batches} ({len(videos)} videos)")
        
        for i, video_data in enumerate(videos):
            video_id = video_data['video_id']
            
            # Skip if already processed
            if video_id in progress['completed_videos']:
                self.logger.info(f"Skipping already processed video: {video_data['title']}")
                continue
            
            self.logger.info(f"Processing video {i+1}/{len(videos)}: {video_data['title']}")
            
            # Get additional metadata if available
            if self.youtube_service:
                detailed_metadata = self.get_video_metadata(video_id)
                if detailed_metadata:
                    video_data.update(detailed_metadata)
            
            # Extract transcript with retries
            transcript_text = None
            transcript_data = None
            extraction_metadata = None
            
            for attempt in range(self.config['max_retries']):
                try:
                    transcript_text, transcript_data, extraction_metadata = self.extract_transcript(video_id)
                    if extraction_metadata['success']:
                        break
                    else:
                        self.logger.warning(f"Attempt {attempt + 1} failed for {video_id}: {extraction_metadata['error']}")
                except Exception as e:
                    self.logger.warning(f"Attempt {attempt + 1} failed for {video_id}: {e}")
                
                if attempt < self.config['max_retries'] - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            # Process result
            if transcript_text and extraction_metadata['success']:
                try:
                    # Save transcript
                    filepath = self.save_transcript(video_data, transcript_text, 
                                                  transcript_data, extraction_metadata)
                    
                    # Create result record
                    result = {
                        'video_id': video_id,
                        'title': video_data['title'],
                        'url': video_data['url'],
                        'published_at': video_data.get('published_at'),
                        'duration': video_data.get('duration'),
                        'view_count': video_data.get('view_count', 0),
                        'transcript_file': filepath,
                        'transcript_type': extraction_metadata['transcript_type'],
                        'language': extraction_metadata['language'],
                        'word_count': extraction_metadata['word_count'],
                        'duration_covered': extraction_metadata['duration_covered'],
                        'tractate': self.classify_video(video_data['title'], 
                                                      video_data.get('description', ''))[0],
                        'series_type': self.classify_video(video_data['title'], 
                                                         video_data.get('description', ''))[1],
                        'status': 'success',
                        'processed_at': datetime.now().isoformat()
                    }
                    
                    batch_results.append(result)
                    progress['completed_videos'].append(video_id)
                    progress['total_processed'] += 1
                    
                    self.logger.info(f"Successfully processed: {video_data['title']}")
                    
                except Exception as e:
                    self.logger.error(f"Error saving transcript for {video_id}: {e}")
                    self.failed_videos.append({
                        'video_id': video_id,
                        'title': video_data['title'],
                        'error': f"Save error: {str(e)}",
                        'timestamp': datetime.now().isoformat()
                    })
            else:
                # Record failure
                error_msg = extraction_metadata['error'] if extraction_metadata else "Unknown error"
                self.failed_videos.append({
                    'video_id': video_id,
                    'title': video_data['title'],
                    'error': error_msg,
                    'timestamp': datetime.now().isoformat()
                })
                progress['failed_videos'].append(video_id)
                self.logger.warning(f"Failed to process: {video_data['title']} - {error_msg}")
            
            # Rate limiting
            time.sleep(self.config['rate_limit_seconds'])
        
        # Save progress after each batch
        progress['last_batch'] = batch_num
        self.save_progress(progress)
        
        return batch_results
    
    def generate_master_catalog(self, all_results: List[Dict]):
        """Generate comprehensive master catalog CSV."""
        catalog_file = Path(self.config['output_directory']) / "master_catalog.csv"
        
        fieldnames = [
            'video_id', 'title', 'url', 'published_at', 'duration', 'view_count',
            'transcript_file', 'transcript_type', 'language', 'word_count',
            'duration_covered', 'tractate', 'series_type', 'status', 'processed_at'
        ]
        
        with open(catalog_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_results)
        
        self.logger.info(f"Master catalog saved to: {catalog_file}")
        
        # Generate summary statistics
        self.generate_summary_report(all_results)
    
    def generate_summary_report(self, all_results: List[Dict]):
        """Generate comprehensive summary report."""
        report_file = Path(self.config['output_directory']) / "extraction_summary.txt"
        
        # Calculate statistics
        total_videos = len(all_results)
        successful = len([r for r in all_results if r['status'] == 'success'])
        failed = len(self.failed_videos)
        
        # Tractate breakdown
        tractate_counts = {}
        for result in all_results:
            tractate = result.get('tractate', 'Unknown')
            tractate_counts[tractate] = tractate_counts.get(tractate, 0) + 1
        
        # Language breakdown
        language_counts = {}
        for result in all_results:
            lang = result.get('language', 'Unknown')
            language_counts[lang] = language_counts.get(lang, 0) + 1
        
        # Total word count
        total_words = sum(r.get('word_count', 0) for r in all_results)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("MERCAZ DAF YOMI TRANSCRIPT EXTRACTION SUMMARY\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Extraction completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total videos processed: {total_videos}\n")
            f.write(f"Successful extractions: {successful}\n")
            f.write(f"Failed extractions: {failed}\n")
            f.write(f"Success rate: {(successful/total_videos*100):.1f}%\n\n")
            
            f.write("TRACTATE BREAKDOWN:\n")
            f.write("-" * 30 + "\n")
            for tractate, count in sorted(tractate_counts.items()):
                f.write(f"{tractate}: {count} videos\n")
            
            f.write(f"\nLANGUAGE BREAKDOWN:\n")
            f.write("-" * 30 + "\n")
            for lang, count in sorted(language_counts.items()):
                f.write(f"{lang}: {count} videos\n")
            
            f.write(f"\nCONTENT STATISTICS:\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total words extracted: {total_words:,}\n")
            f.write(f"Average words per video: {total_words//total_videos if total_videos > 0 else 0:,}\n")
            
            if self.failed_videos:
                f.write(f"\nFAILED VIDEOS:\n")
                f.write("-" * 30 + "\n")
                for failed in self.failed_videos:
                    f.write(f"- {failed['title']} ({failed['video_id']}): {failed['error']}\n")
        
        self.logger.info(f"Summary report saved to: {report_file}")
    
    def run_extraction(self, max_videos: int = None, resume: bool = True):
        """Run the complete extraction process."""
        self.logger.info("Starting enhanced YouTube transcript extraction")
        
        # Load progress if resuming
        progress = self.load_progress() if resume else {
            'completed_videos': [],
            'failed_videos': [],
            'last_batch': 0,
            'total_processed': 0,
            'start_time': datetime.now().isoformat()
        }
        
        if not progress.get('start_time'):
            progress['start_time'] = datetime.now().isoformat()
        
        # Get all videos from channel
        self.logger.info("Fetching videos from Mercaz Daf Yomi channel...")
        all_videos = self.get_channel_videos(max_results=max_videos)
        
        if not all_videos:
            self.logger.error("No videos found. Check channel configuration.")
            return
        
        # Filter out already processed videos if resuming
        if resume and progress['completed_videos']:
            remaining_videos = [v for v in all_videos 
                              if v['video_id'] not in progress['completed_videos']]
            self.logger.info(f"Resuming extraction. {len(remaining_videos)} videos remaining.")
        else:
            remaining_videos = all_videos
        
        if not remaining_videos:
            self.logger.info("All videos already processed!")
            return
        
        # Process in batches
        batch_size = self.config['batch_size']
        total_batches = (len(remaining_videos) + batch_size - 1) // batch_size
        all_results = []
        
        for i in range(0, len(remaining_videos), batch_size):
            batch_num = (i // batch_size) + 1
            
            # Skip batches if resuming
            if resume and batch_num <= progress.get('last_batch', 0):
                continue
            
            batch_videos = remaining_videos[i:i + batch_size]
            batch_results = self.process_video_batch(
                batch_videos, batch_num, total_batches, progress
            )
            all_results.extend(batch_results)
            
            self.logger.info(f"Completed batch {batch_num}/{total_batches}")
            
            # Optional pause between batches
            if batch_num < total_batches:
                time.sleep(5)
        
        # Generate final reports
        self.logger.info("Generating final reports...")
        self.generate_master_catalog(all_results)
        
        # Clean up progress file
        if os.path.exists(self.progress_file):
            os.rename(self.progress_file, 
                     f"{self.progress_file}.completed_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        self.logger.info("Extraction completed successfully!")
        self.logger.info(f"Results saved to: {self.config['output_directory']}")


def main():
    """Main entry point with command line interface."""
    parser = argparse.ArgumentParser(
        description="Enhanced YouTube Transcript Extractor for Mercaz Daf Yomi"
    )
    
    parser.add_argument(
        '--config', '-c',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    
    parser.add_argument(
        '--max-videos', '-m',
        type=int,
        help='Maximum number of videos to process (for testing)'
    )
    
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Start fresh extraction (ignore previous progress)'
    )
    
    parser.add_argument(
        '--channel-scan-only',
        action='store_true',
        help='Only scan channel and list videos (no extraction)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        help='Override batch size from config'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize extractor
        extractor = MercazDafYomiExtractor(args.config)
        
        # Override config with command line arguments
        if args.batch_size:
            extractor.config['batch_size'] = args.batch_size
        
        if args.channel_scan_only:
            # Just scan and list videos
            videos = extractor.get_channel_videos(max_results=args.max_videos)
            print(f"\nFound {len(videos)} videos in channel:")
            print("-" * 60)
            for i, video in enumerate(videos[:20], 1):  # Show first 20
                print(f"{i:3d}. {video['title']}")
                print(f"     ID: {video['video_id']}")
                print(f"     Published: {video.get('published_at', 'Unknown')}")
                print()
            
            if len(videos) > 20:
                print(f"... and {len(videos) - 20} more videos")
            
            return
        
        # Run full extraction
        extractor.run_extraction(
            max_videos=args.max_videos,
            resume=not args.no_resume
        )
        
    except KeyboardInterrupt:
        print("\nExtraction interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()