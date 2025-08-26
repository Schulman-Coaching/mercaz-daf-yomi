#!/usr/bin/env python3
"""
Full Extraction Runner for Mercaz Daf Yomi Channel
Demonstrates complete workflow integration of all system components.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime

def print_banner():
    """Print system banner."""
    print("=" * 70)
    print("  ENHANCED YOUTUBE TRANSCRIPT EXTRACTION SYSTEM")
    print("  Mercaz Daf Yomi Channel - Complete Workflow")
    print("=" * 70)
    print()

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'youtube_transcript_api',
        'googleapiclient',
        'requests',
        'pathlib'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n❌ Missing dependencies: {', '.join(missing_modules)}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies satisfied\n")
    return True

def check_configuration():
    """Check configuration file."""
    print("🔧 Checking configuration...")
    
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"❌ Configuration file not found: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print(f"  ✅ Configuration loaded")
        print(f"  📁 Output directory: {config.get('output_directory', 'Not set')}")
        print(f"  📊 Batch size: {config.get('batch_size', 'Not set')}")
        print(f"  ⏱️  Rate limit: {config.get('rate_limit_seconds', 'Not set')} seconds")
        
        if config.get('youtube_api_key'):
            print(f"  🔑 YouTube API key: Configured")
        else:
            print(f"  ⚠️  YouTube API key: Not configured (optional)")
        
        print("✅ Configuration valid\n")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def run_channel_discovery(api_key=None, max_videos=None):
    """Run channel discovery phase."""
    print("🔍 Phase 1: Channel Discovery")
    print("-" * 30)
    
    if not api_key:
        print("⚠️  Skipping channel discovery (no API key provided)")
        print("   You can still extract transcripts without channel discovery\n")
        return True
    
    try:
        import subprocess
        
        cmd = ["python", "channel_discovery.py", "--api-key", api_key]
        if max_videos:
            cmd.extend(["--max-videos", str(max_videos)])
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Channel discovery completed successfully")
            print(result.stdout)
        else:
            print("⚠️  Channel discovery failed (continuing anyway)")
            print(result.stderr)
        
        print()
        return True
        
    except Exception as e:
        print(f"⚠️  Channel discovery error: {e}")
        print("Continuing with transcript extraction...\n")
        return True

def run_transcript_extraction(max_videos=None, resume=True):
    """Run transcript extraction phase."""
    print("📝 Phase 2: Transcript Extraction")
    print("-" * 35)
    
    try:
        import subprocess
        
        cmd = ["python", "enhanced_youtube_extractor.py"]
        if max_videos:
            cmd.extend(["--max-videos", str(max_videos)])
        if not resume:
            cmd.append("--no-resume")
        
        print(f"Running: {' '.join(cmd)}")
        print("This may take a while for large channels...\n")
        
        # Run with real-time output
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 universal_newlines=True, bufsize=1)
        
        for line in process.stdout:
            print(line.rstrip())
        
        process.wait()
        
        if process.returncode == 0:
            print("\n✅ Transcript extraction completed successfully")
        else:
            print(f"\n❌ Transcript extraction failed with code {process.returncode}")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Transcript extraction error: {e}")
        return False

def run_content_organization():
    """Run content organization phase."""
    print("📁 Phase 3: Content Organization")
    print("-" * 33)
    
    try:
        import subprocess
        
        cmd = ["python", "content_organizer.py", "--all"]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Content organization completed successfully")
            print(result.stdout)
        else:
            print("⚠️  Content organization had issues")
            print(result.stderr)
        
        print()
        return True
        
    except Exception as e:
        print(f"⚠️  Content organization error: {e}")
        return True  # Non-critical, continue

def generate_final_report():
    """Generate final extraction report."""
    print("📊 Phase 4: Final Report Generation")
    print("-" * 35)
    
    try:
        # Check output directory
        config_file = "config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        output_dir = Path(config.get('output_directory', 'Mercaz_Daf_Yomi_Transcripts'))
        
        if not output_dir.exists():
            print("⚠️  Output directory not found")
            return False
        
        # Count files
        transcript_files = list(output_dir.rglob('*.txt'))
        json_files = list(output_dir.rglob('*.json'))
        csv_files = list(output_dir.rglob('*.csv'))
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in transcript_files if f.exists())
        total_size_mb = total_size / (1024 * 1024)
        
        # Generate summary
        report_file = output_dir / f"FINAL_EXTRACTION_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("MERCAZ DAF YOMI - FINAL EXTRACTION REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Extraction completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Output directory: {output_dir}\n\n")
            
            f.write("FILE SUMMARY:\n")
            f.write("-" * 15 + "\n")
            f.write(f"Transcript files (.txt): {len(transcript_files)}\n")
            f.write(f"JSON files: {len(json_files)}\n")
            f.write(f"CSV files: {len(csv_files)}\n")
            f.write(f"Total content size: {total_size_mb:.1f} MB\n\n")
            
            f.write("DIRECTORY STRUCTURE:\n")
            f.write("-" * 20 + "\n")
            
            # List tractate directories
            for item in sorted(output_dir.iterdir()):
                if item.is_dir() and item.name not in ['Logs', 'Reports']:
                    series_count = len([f for f in item.rglob('*.txt')])
                    f.write(f"{item.name}: {series_count} files\n")
        
        print(f"✅ Final report generated: {report_file}")
        
        # Print summary to console
        print("\n📊 EXTRACTION SUMMARY:")
        print(f"   📄 Transcript files: {len(transcript_files)}")
        print(f"   💾 Total size: {total_size_mb:.1f} MB")
        print(f"   📁 Output directory: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Report generation error: {e}")
        return True  # Non-critical

def main():
    """Main workflow orchestrator."""
    parser = argparse.ArgumentParser(
        description="Complete workflow for Mercaz Daf Yomi transcript extraction"
    )
    
    parser.add_argument(
        '--max-videos', '-m',
        type=int,
        help='Maximum number of videos to process (for testing)'
    )
    
    parser.add_argument(
        '--skip-discovery',
        action='store_true',
        help='Skip channel discovery phase'
    )
    
    parser.add_argument(
        '--skip-organization',
        action='store_true',
        help='Skip content organization phase'
    )
    
    parser.add_argument(
        '--no-resume',
        action='store_true',
        help='Start fresh extraction (ignore previous progress)'
    )
    
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help='Run in test mode (max 10 videos, all phases)'
    )
    
    args = parser.parse_args()
    
    # Test mode overrides
    if args.test_mode:
        args.max_videos = 10
        print("🧪 Running in TEST MODE (max 10 videos)\n")
    
    print_banner()
    
    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)
    
    if not check_configuration():
        sys.exit(1)
    
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    api_key = config.get('youtube_api_key')
    
    print("🚀 Starting complete extraction workflow...\n")
    start_time = time.time()
    
    # Phase 1: Channel Discovery
    if not args.skip_discovery:
        if not run_channel_discovery(api_key, args.max_videos):
            print("❌ Channel discovery failed")
            sys.exit(1)
    else:
        print("⏭️  Skipping channel discovery phase\n")
    
    # Phase 2: Transcript Extraction
    if not run_transcript_extraction(args.max_videos, not args.no_resume):
        print("❌ Transcript extraction failed")
        sys.exit(1)
    
    # Phase 3: Content Organization
    if not args.skip_organization:
        run_content_organization()
    else:
        print("⏭️  Skipping content organization phase\n")
    
    # Phase 4: Final Report
    generate_final_report()
    
    # Completion
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 70)
    print("🎉 EXTRACTION WORKFLOW COMPLETED SUCCESSFULLY!")
    print(f"⏱️  Total time: {duration/60:.1f} minutes")
    print("=" * 70)
    
    # Next steps
    print("\n📋 NEXT STEPS:")
    print("1. Review the generated reports in the output directory")
    print("2. Check the master catalog CSV for complete video list")
    print("3. Browse organized transcripts by tractate")
    print("4. Set up regular extraction for new videos")
    
    if args.test_mode:
        print("\n🧪 Test mode completed. Review results before running full extraction.")

if __name__ == "__main__":
    main()