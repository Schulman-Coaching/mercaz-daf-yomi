
# YouTube Transcript Extraction Script
# This script demonstrates how to extract transcripts from YouTube videos

import os
import csv
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import time

def extract_video_id(url):
    """
    Extract video ID from a YouTube URL
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:]
    elif parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query)['v'][0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
    return None

def extract_transcript(video_id):
    """
    Extract transcript for a single video
    """
    try:
        # Get available transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try to get English transcript first
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            # If English not available, get first available transcript
            transcript = transcript_list.find_transcript(['en-US', 'en-GB', 'auto'])

        # Fetch the transcript
        transcript_data = transcript.fetch()

        # Convert to plain text
        full_text = ""
        for entry in transcript_data:
            full_text += entry['text'] + " "

        return full_text.strip(), transcript_data

    except Exception as e:
        print(f"Error extracting transcript for {video_id}: {str(e)}")
        return None, None

def save_transcript(video_id, title, transcript_text, transcript_data):
    """
    Save transcript to a text file
    """
    # Create filename (sanitize title for filesystem)
    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"{safe_title}_{video_id}.txt"

    # Write to file
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Video: {title}\n")
        f.write(f"Video ID: {video_id}\n")
        f.write(f"URL: https://www.youtube.com/watch?v={video_id}\n")
        f.write("-" * 50 + "\n\n")
        f.write(transcript_text)

    return filename

def process_video_list(video_urls_and_titles):
    """
    Process a list of YouTube videos
    """
    results = []

    for url, title in video_urls_and_titles:
        print(f"Processing: {title}")

        # Extract video ID
        video_id = extract_video_id(url)
        if not video_id:
            print(f"  Error: Could not extract video ID from {url}")
            continue

        # Extract transcript
        transcript_text, transcript_data = extract_transcript(video_id)

        if transcript_text:
            # Save to file
            filename = save_transcript(video_id, title, transcript_text)
            results.append({
                'title': title,
                'video_id': video_id,
                'url': url,
                'transcript_file': filename,
                'transcript_length': len(transcript_text),
                'status': 'success'
            })
            print(f"  Success: Saved to {filename}")
        else:
            results.append({
                'title': title,
                'video_id': video_id,
                'url': url,
                'transcript_file': None,
                'transcript_length': 0,
                'status': 'failed'
            })
            print(f"  Failed: Could not extract transcript")

        # Rate limiting - wait 1 second between requests
        time.sleep(1)

    return results

# Example usage with the Daf Yomi videos
if __name__ == "__main__":
    # Sample video list (first 5 videos from the playlist)
    sample_videos = [
        ("https://youtube.com/watch?v=l_JBZsSR7Tk", "Daf Yomi Berachos Daf 2 by R' Eli Stefansky"),
        ("https://youtube.com/watch?v=TsChDzrEy9Q", "Daf Yomi Berachos Daf 3 by R' Eli Stefansky"),
        ("https://youtube.com/watch?v=USjIWAjcoMc", "Daf Yomi Berachos Daf 4 by R' Eli Stefansky"),
        ("https://youtube.com/watch?v=IdYMkJNAcYI", "Daf Yomi Berachos Daf 5 by R' Eli Stefansky"),
        ("https://youtube.com/watch?v=hVR6zjpsJUk", "Daf Yomi Berachos Daf 6 by R' Eli Stefansky")
    ]

    print("YouTube Transcript Extraction Demo")
    print("=" * 40)

    # Process the sample videos
    results = process_video_list(sample_videos)

    # Create summary CSV
    with open('transcript_extraction_results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['title', 'video_id', 'url', 'transcript_file', 'transcript_length', 'status'])
        writer.writeheader()
        writer.writerows(results)

    print("\nSummary:")
    print(f"Total videos processed: {len(results)}")
    print(f"Successful extractions: {len([r for r in results if r['status'] == 'success'])}")
    print(f"Failed extractions: {len([r for r in results if r['status'] == 'failed'])}")
    print("Results saved to: transcript_extraction_results.csv")
