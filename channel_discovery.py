#!/usr/bin/env python3
"""
Channel Discovery Utility for Mercaz Daf Yomi
Discovers and analyzes all videos from the channel using YouTube Data API v3.
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import argparse


class ChannelDiscovery:
    """Utility for discovering and analyzing YouTube channel content."""
    
    def __init__(self, api_key: str):
        """Initialize with YouTube Data API key."""
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.channel_data = {}
        self.playlists = []
        self.all_videos = []
    
    def get_channel_info(self, channel_handle: str) -> dict:
        """Get comprehensive channel information."""
        try:
            # Get channel by handle
            response = self.youtube.channels().list(
                part='id,snippet,statistics,contentDetails',
                forHandle=channel_handle.replace('@', '')
            ).execute()
            
            if not response['items']:
                print(f"Channel not found: {channel_handle}")
                return {}
            
            channel = response['items'][0]
            
            self.channel_data = {
                'id': channel['id'],
                'title': channel['snippet']['title'],
                'description': channel['snippet']['description'],
                'published_at': channel['snippet']['publishedAt'],
                'subscriber_count': int(channel['statistics'].get('subscriberCount', 0)),
                'video_count': int(channel['statistics'].get('videoCount', 0)),
                'view_count': int(channel['statistics'].get('viewCount', 0)),
                'uploads_playlist': channel['contentDetails']['relatedPlaylists']['uploads'],
                'thumbnail_url': channel['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                'country': channel['snippet'].get('country', ''),
                'custom_url': channel['snippet'].get('customUrl', '')
            }
            
            print(f"Channel: {self.channel_data['title']}")
            print(f"Subscribers: {self.channel_data['subscriber_count']:,}")
            print(f"Total Videos: {self.channel_data['video_count']:,}")
            print(f"Total Views: {self.channel_data['view_count']:,}")
            
            return self.channel_data
            
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return {}
    
    def get_all_playlists(self, channel_id: str) -> list:
        """Get all playlists from the channel."""
        playlists = []
        next_page_token = None
        
        try:
            while True:
                response = self.youtube.playlists().list(
                    part='id,snippet,contentDetails',
                    channelId=channel_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                
                for playlist in response['items']:
                    playlist_data = {
                        'id': playlist['id'],
                        'title': playlist['snippet']['title'],
                        'description': playlist['snippet']['description'],
                        'published_at': playlist['snippet']['publishedAt'],
                        'video_count': playlist['contentDetails']['itemCount'],
                        'thumbnail_url': playlist['snippet']['thumbnails'].get('medium', {}).get('url', '')
                    }
                    playlists.append(playlist_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            self.playlists = playlists
            print(f"Found {len(playlists)} playlists")
            return playlists
            
        except HttpError as e:
            print(f"Error fetching playlists: {e}")
            return []
    
    def get_all_videos(self, uploads_playlist_id: str, max_results: int = None) -> list:
        """Get all videos from the uploads playlist."""
        videos = []
        next_page_token = None
        video_count = 0
        
        try:
            while True:
                response = self.youtube.playlistItems().list(
                    part='snippet,contentDetails',
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                
                video_ids = []
                for item in response['items']:
                    if max_results and video_count >= max_results:
                        break
                    video_ids.append(item['contentDetails']['videoId'])
                    video_count += 1
                
                # Get detailed video information
                if video_ids:
                    video_details = self.youtube.videos().list(
                        part='snippet,contentDetails,statistics',
                        id=','.join(video_ids)
                    ).execute()
                    
                    for video in video_details['items']:
                        video_data = {
                            'video_id': video['id'],
                            'title': video['snippet']['title'],
                            'description': video['snippet']['description'],
                            'published_at': video['snippet']['publishedAt'],
                            'duration': video['contentDetails']['duration'],
                            'view_count': int(video['statistics'].get('viewCount', 0)),
                            'like_count': int(video['statistics'].get('likeCount', 0)),
                            'comment_count': int(video['statistics'].get('commentCount', 0)),
                            'thumbnail_url': video['snippet']['thumbnails'].get('medium', {}).get('url', ''),
                            'tags': video['snippet'].get('tags', []),
                            'category_id': video['snippet'].get('categoryId', ''),
                            'default_language': video['snippet'].get('defaultLanguage', ''),
                            'url': f"https://www.youtube.com/watch?v={video['id']}"
                        }
                        videos.append(video_data)
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token or (max_results and video_count >= max_results):
                    break
            
            self.all_videos = videos
            print(f"Found {len(videos)} videos")
            return videos
            
        except HttpError as e:
            print(f"Error fetching videos: {e}")
            return []
    
    def analyze_content(self) -> dict:
        """Analyze channel content patterns."""
        if not self.all_videos:
            return {}
        
        analysis = {
            'total_videos': len(self.all_videos),
            'date_range': {
                'earliest': min(v['published_at'] for v in self.all_videos),
                'latest': max(v['published_at'] for v in self.all_videos)
            },
            'tractate_breakdown': {},
            'series_patterns': {},
            'duration_stats': {},
            'view_stats': {},
            'upload_frequency': {}
        }
        
        # Analyze tractates
        tractate_patterns = {
            'Berachos': ['berachos', 'berakhot'],
            'Shabbos': ['shabbos', 'shabbat'],
            'Eruvin': ['eruvin'],
            'Pesachim': ['pesachim'],
            # Add more as needed
        }
        
        for video in self.all_videos:
            title_lower = video['title'].lower()
            
            # Tractate analysis
            for tractate, patterns in tractate_patterns.items():
                if any(pattern in title_lower for pattern in patterns):
                    analysis['tractate_breakdown'][tractate] = analysis['tractate_breakdown'].get(tractate, 0) + 1
                    break
            else:
                analysis['tractate_breakdown']['Other'] = analysis['tractate_breakdown'].get('Other', 0) + 1
            
            # Series pattern analysis
            if 'daf yomi' in title_lower:
                analysis['series_patterns']['Daf Yomi'] = analysis['series_patterns'].get('Daf Yomi', 0) + 1
            elif 'shiur' in title_lower:
                analysis['series_patterns']['Shiur'] = analysis['series_patterns'].get('Shiur', 0) + 1
            else:
                analysis['series_patterns']['Other'] = analysis['series_patterns'].get('Other', 0) + 1
        
        # Duration and view statistics
        durations = [self.parse_duration(v['duration']) for v in self.all_videos]
        views = [v['view_count'] for v in self.all_videos]
        
        analysis['duration_stats'] = {
            'average_seconds': sum(durations) / len(durations),
            'min_seconds': min(durations),
            'max_seconds': max(durations),
            'total_hours': sum(durations) / 3600
        }
        
        analysis['view_stats'] = {
            'total_views': sum(views),
            'average_views': sum(views) / len(views),
            'min_views': min(views),
            'max_views': max(views)
        }
        
        return analysis
    
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
    
    def save_discovery_report(self, output_dir: str = "channel_discovery"):
        """Save comprehensive discovery report."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save channel info
        with open(output_path / f"channel_info_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(self.channel_data, f, indent=2, ensure_ascii=False)
        
        # Save playlists
        with open(output_path / f"playlists_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(self.playlists, f, indent=2, ensure_ascii=False)
        
        # Save all videos as JSON
        with open(output_path / f"all_videos_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(self.all_videos, f, indent=2, ensure_ascii=False)
        
        # Save videos as CSV
        if self.all_videos:
            with open(output_path / f"all_videos_{timestamp}.csv", 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['video_id', 'title', 'published_at', 'duration', 'view_count', 
                             'like_count', 'comment_count', 'url']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for video in self.all_videos:
                    row = {field: video.get(field, '') for field in fieldnames}
                    writer.writerow(row)
        
        # Save analysis
        analysis = self.analyze_content()
        with open(output_path / f"content_analysis_{timestamp}.json", 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        # Save summary report
        with open(output_path / f"discovery_summary_{timestamp}.txt", 'w', encoding='utf-8') as f:
            f.write("MERCAZ DAF YOMI CHANNEL DISCOVERY REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Discovery Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Channel: {self.channel_data.get('title', 'Unknown')}\n")
            f.write(f"Channel ID: {self.channel_data.get('id', 'Unknown')}\n")
            f.write(f"Subscribers: {self.channel_data.get('subscriber_count', 0):,}\n")
            f.write(f"Total Videos Found: {len(self.all_videos)}\n")
            f.write(f"Total Playlists: {len(self.playlists)}\n\n")
            
            if analysis:
                f.write("CONTENT ANALYSIS:\n")
                f.write("-" * 20 + "\n")
                f.write(f"Date Range: {analysis['date_range']['earliest']} to {analysis['date_range']['latest']}\n")
                f.write(f"Total Content Hours: {analysis['duration_stats']['total_hours']:.1f}\n")
                f.write(f"Average Video Length: {analysis['duration_stats']['average_seconds']/60:.1f} minutes\n")
                f.write(f"Total Views: {analysis['view_stats']['total_views']:,}\n")
                f.write(f"Average Views per Video: {analysis['view_stats']['average_views']:,.0f}\n\n")
                
                f.write("TRACTATE BREAKDOWN:\n")
                f.write("-" * 20 + "\n")
                for tractate, count in sorted(analysis['tractate_breakdown'].items()):
                    f.write(f"{tractate}: {count} videos\n")
                
                f.write(f"\nSERIES PATTERNS:\n")
                f.write("-" * 20 + "\n")
                for series, count in sorted(analysis['series_patterns'].items()):
                    f.write(f"{series}: {count} videos\n")
        
        print(f"Discovery report saved to: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Discover and analyze Mercaz Daf Yomi channel")
    parser.add_argument('--api-key', required=True, help='YouTube Data API v3 key')
    parser.add_argument('--channel', default='@MercazDafYomi', help='Channel handle')
    parser.add_argument('--max-videos', type=int, help='Maximum videos to analyze')
    parser.add_argument('--output-dir', default='channel_discovery', help='Output directory')
    
    args = parser.parse_args()
    
    try:
        discovery = ChannelDiscovery(args.api_key)
        
        # Get channel info
        channel_info = discovery.get_channel_info(args.channel)
        if not channel_info:
            return
        
        # Get playlists
        discovery.get_all_playlists(channel_info['id'])
        
        # Get all videos
        discovery.get_all_videos(channel_info['uploads_playlist'], args.max_videos)
        
        # Save report
        discovery.save_discovery_report(args.output_dir)
        
        print("Channel discovery completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()