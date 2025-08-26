# Enhanced YouTube Transcript Extraction System for Mercaz Daf Yomi

A comprehensive, production-ready system for extracting and organizing transcripts from the Mercaz Daf Yomi YouTube channel. Designed to handle 5,000+ videos with robust error handling, progress tracking, and automatic content organization.

## 🎯 Overview

This system extends the basic YouTube transcript extraction capabilities to provide:

- **Channel Discovery**: Automatic discovery of all videos from @MercazDafYomi channel
- **Bulk Processing**: Scalable processing of thousands of videos in manageable batches
- **Content Organization**: Automatic categorization by tractate and series type
- **Progress Tracking**: Resume capability and comprehensive logging
- **Error Handling**: Robust retry logic and comprehensive error reporting

## 📁 Project Structure

```
Enhanced_YouTube_Extractor/
├── enhanced_youtube_extractor.py    # Main extraction script
├── channel_discovery.py             # Channel analysis utility
├── content_organizer.py             # Content organization utility
├── config.json                      # Configuration file
├── requirements.txt                 # Python dependencies
├── README.md                        # This documentation
└── Mercaz_Daf_Yomi_Transcripts/    # Output directory (created automatically)
    ├── Berachos/
    │   ├── Daf_Yomi/
    │   ├── Shiurim/
    │   └── Lectures/
    ├── Shabbos/
    ├── [Other Tractates]/
    ├── Special_Series/
    ├── Logs/
    ├── Reports/
    ├── master_catalog.csv
    └── MASTER_INDEX.md
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project files
# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configuration

1. **Get YouTube Data API Key** (Optional but recommended):
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable YouTube Data API v3
   - Create credentials (API Key)

2. **Configure the system**:
   ```bash
   # Edit config.json
   {
     "youtube_api_key": "YOUR_API_KEY_HERE",
     "channel_handle": "@MercazDafYomi",
     "batch_size": 50,
     "rate_limit_seconds": 2
   }
   ```

### 3. Basic Usage

```bash
# Test with a small batch first
python enhanced_youtube_extractor.py --max-videos 10

# Run full extraction
python enhanced_youtube_extractor.py

# Resume interrupted extraction
python enhanced_youtube_extractor.py --resume

# Organize existing files
python content_organizer.py --all
```

## 📋 Detailed Usage

### Main Extraction Script

```bash
python enhanced_youtube_extractor.py [OPTIONS]

Options:
  --config, -c          Configuration file path (default: config.json)
  --max-videos, -m      Maximum number of videos to process (for testing)
  --no-resume          Start fresh extraction (ignore previous progress)
  --channel-scan-only  Only scan channel and list videos (no extraction)
  --batch-size         Override batch size from config
```

### Channel Discovery

```bash
python channel_discovery.py [OPTIONS]

Options:
  --api-key            YouTube Data API v3 key (required)
  --channel            Channel handle (default: @MercazDafYomi)
  --max-videos         Maximum videos to analyze
  --output-dir         Output directory for reports
```

### Content Organization

```bash
python content_organizer.py [OPTIONS]

Options:
  --base-dir           Base directory for transcripts
  --source-dir         Source directory to organize from
  --create-structure   Create directory structure
  --organize-files     Organize existing files
  --create-indexes     Create tractate indexes
  --generate-reports   Generate organization reports
  --all               Run all organization tasks
```

## ⚙️ Configuration Options

### config.json Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `youtube_api_key` | YouTube Data API v3 key | "" |
| `channel_handle` | Target channel handle | "@MercazDafYomi" |
| `output_directory` | Base output directory | "Mercaz_Daf_Yomi_Transcripts" |
| `batch_size` | Videos per batch | 50 |
| `rate_limit_seconds` | Delay between requests | 2 |
| `max_retries` | Retry attempts per video | 3 |
| `organize_by_tractate` | Auto-organize by tractate | true |

### Tractate Classification

The system automatically classifies videos into tractates based on title patterns:

- **Berachos**: berachos, berakhot, brachot
- **Shabbos**: shabbos, shabbat
- **Eruvin**: eruvin
- **Pesachim**: pesachim
- And all other Talmudic tractates...

## 📊 Features

### 1. Channel Discovery
- Discovers all videos from the channel using YouTube Data API v3
- Analyzes content patterns and generates comprehensive reports
- Identifies playlists and series organization

### 2. Bulk Processing
- Processes videos in configurable batches (default: 50)
- Implements rate limiting to respect YouTube's API limits
- Supports resume functionality for interrupted extractions

### 3. Content Organization
- Automatically categorizes videos by tractate and series type
- Creates organized directory structure
- Generates tractate-specific indexes and master catalog

### 4. Progress Tracking
- Saves progress after each batch
- Comprehensive logging with timestamps
- Resume capability from last successful batch

### 5. Error Handling
- Retry logic with exponential backoff
- Comprehensive error logging
- Graceful handling of missing transcripts

### 6. Quality Validation
- Verifies transcript extraction success
- Tracks transcript type (manual vs auto-generated)
- Validates content organization

## 📈 Output Files

### Generated Reports
- `master_catalog.csv` - Complete catalog of all processed videos
- `extraction_summary.txt` - Summary statistics and tractate breakdown
- `MASTER_INDEX.md` - Comprehensive content index
- Individual tractate indexes (`Tractate_INDEX.md`)

### Transcript Files
- Individual transcript files: `Title_VideoID.txt`
- Structured data included in each file
- JSON metadata for programmatic access

### Log Files
- Detailed extraction logs with timestamps
- Progress tracking files
- Error reports and failed video lists

## 🔧 Advanced Usage

### Custom Tractate Patterns

Edit `config.json` to add custom classification patterns:

```json
{
  "tractate_patterns": {
    "Custom_Tractate": ["pattern1", "pattern2"],
    "Special_Series": ["special", "event"]
  }
}
```

### Batch Processing Strategy

For large-scale extraction:

1. **Test Run**: Start with `--max-videos 10`
2. **Small Batch**: Process 100-200 videos first
3. **Full Extraction**: Run complete extraction
4. **Organization**: Use content organizer to structure files

### API Rate Limiting

The system implements several rate limiting strategies:

- 2-second delay between transcript requests (configurable)
- Exponential backoff for failed requests
- Batch processing to manage API quotas
- Optional YouTube Data API integration for metadata

## 🚨 Error Handling

### Common Issues and Solutions

1. **"No transcript available"**
   - Some videos may not have captions enabled
   - Check video manually on YouTube
   - These are logged in failed videos report

2. **Rate limiting errors**
   - Increase `rate_limit_seconds` in config
   - Reduce `batch_size`
   - The system will automatically retry with backoff

3. **API quota exceeded**
   - YouTube Data API has daily quotas
   - Use without API key for transcript-only extraction
   - Consider spreading extraction across multiple days

4. **Network timeouts**
   - System automatically retries failed requests
   - Check internet connection
   - Increase `max_retries` if needed

## 📋 Legal and Ethical Considerations

### ✅ Allowed Uses
- Personal study and research
- Educational purposes under fair use
- Accessibility improvements
- Academic research

### ❌ Restrictions
- Do not redistribute complete transcripts without permission
- Respect copyright and intellectual property rights
- Follow YouTube's Terms of Service
- Contact content creators for extensive commercial use

### 🔒 Best Practices
1. **Contact the Creator**: Reach out to R' Eli Stefansky for permission
2. **Respect Rate Limits**: Don't overwhelm the servers
3. **Personal Use**: Keep transcripts for personal study
4. **Attribution**: Properly attribute content when referencing

## 🛠️ Development

### System Requirements
- Python 3.8+
- Internet connection
- 2GB+ free disk space (for full channel extraction)

### Dependencies
- `youtube-transcript-api`: Core transcript extraction
- `google-api-python-client`: YouTube Data API integration
- `requests`: HTTP handling
- `pathlib`: File system operations

### Testing
```bash
# Test with small batch
python enhanced_youtube_extractor.py --max-videos 5 --no-resume

# Test channel discovery
python channel_discovery.py --api-key YOUR_KEY --max-videos 10

# Test content organization
python content_organizer.py --create-structure
```

## 📞 Support

### Troubleshooting Steps
1. Check configuration file syntax
2. Verify internet connection
3. Test with small batch first
4. Check log files for detailed errors
5. Ensure sufficient disk space

### Getting Help
- Review log files in `Logs/` directory
- Check GitHub issues for similar problems
- Verify YouTube Data API setup if using

## 🔄 Updates and Maintenance

### Regular Maintenance
- Monitor extraction logs for new error patterns
- Update tractate patterns as needed
- Verify YouTube API changes don't break functionality
- Clean up old log files periodically

### Version History
- **v1.0**: Initial enhanced extraction system
- Comprehensive channel discovery
- Automatic content organization
- Production-ready error handling

## 📄 License

This project is for educational and research purposes. Please respect copyright laws and YouTube's Terms of Service when using this system.

---

**Note**: This system is designed to work with publicly available transcript data from YouTube. Always ensure you have appropriate permissions for your intended use case.