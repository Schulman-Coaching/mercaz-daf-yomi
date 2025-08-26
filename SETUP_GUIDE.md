# Setup and Installation Guide
## Enhanced YouTube Transcript Extraction System for Mercaz Daf Yomi

This guide provides step-by-step instructions for setting up and running the enhanced YouTube transcript extraction system.

## 📋 Prerequisites

### System Requirements
- **Python**: Version 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Internet Connection**: Required for YouTube API access
- **Disk Space**: At least 2GB free space for full channel extraction
- **Memory**: 4GB RAM recommended for large batch processing

### Required Accounts (Optional but Recommended)
- **Google Cloud Account**: For YouTube Data API v3 access
- **YouTube Account**: For manual verification of videos

## 🔧 Step-by-Step Installation

### Step 1: Python Installation

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer and check "Add Python to PATH"
3. Verify installation:
   ```cmd
   python --version
   pip --version
   ```

#### macOS
```bash
# Using Homebrew (recommended)
brew install python

# Or download from python.org
# Verify installation
python3 --version
pip3 --version
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip
python3 --version
pip3 --version
```

### Step 2: Download Project Files

1. **Download all project files** to a dedicated directory:
   ```
   Enhanced_YouTube_Extractor/
   ├── enhanced_youtube_extractor.py
   ├── channel_discovery.py
   ├── content_organizer.py
   ├── config.json
   ├── requirements.txt
   ├── README.md
   └── SETUP_GUIDE.md
   ```

2. **Navigate to project directory**:
   ```bash
   cd Enhanced_YouTube_Extractor
   ```

### Step 3: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt

# If you encounter permission errors on Linux/macOS:
pip install --user -r requirements.txt

# Or use virtual environment (recommended):
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: YouTube Data API Setup (Optional but Recommended)

#### 4.1 Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Create Project" or select existing project
3. Name your project (e.g., "YouTube Transcript Extractor")

#### 4.2 Enable YouTube Data API v3
1. In Google Cloud Console, go to "APIs & Services" > "Library"
2. Search for "YouTube Data API v3"
3. Click on it and press "Enable"

#### 4.3 Create API Credentials
1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "API Key"
3. Copy the generated API key
4. (Optional) Restrict the key to YouTube Data API v3 for security

#### 4.4 Configure API Key
Edit `config.json` and add your API key:
```json
{
  "youtube_api_key": "YOUR_API_KEY_HERE",
  "channel_handle": "@MercazDafYomi",
  ...
}
```

### Step 5: Configuration

#### 5.1 Basic Configuration
Edit `config.json` with your preferences:

```json
{
  "youtube_api_key": "YOUR_API_KEY_OR_LEAVE_EMPTY",
  "channel_handle": "@MercazDafYomi",
  "output_directory": "Mercaz_Daf_Yomi_Transcripts",
  "batch_size": 50,
  "rate_limit_seconds": 2,
  "max_retries": 3,
  "organize_by_tractate": true
}
```

#### 5.2 Configuration Options Explained

| Setting | Description | Recommended Value |
|---------|-------------|-------------------|
| `youtube_api_key` | Your YouTube Data API key | Get from Google Cloud |
| `batch_size` | Videos processed per batch | 50 (reduce if errors) |
| `rate_limit_seconds` | Delay between requests | 2 (increase if rate limited) |
| `max_retries` | Retry attempts per video | 3 |
| `organize_by_tractate` | Auto-organize by tractate | true |

## 🧪 Testing Your Setup

### Test 1: Basic Functionality
```bash
# Test with a small batch
python enhanced_youtube_extractor.py --max-videos 5 --channel-scan-only
```

Expected output:
```
Enhanced YouTube Transcript Extractor initialized
Found X videos in channel:
1. Daf Yomi Berachos Daf 2 by R' Eli Stefansky
   ID: l_JBZsSR7Tk
   Published: 2023-XX-XX
...
```

### Test 2: Transcript Extraction
```bash
# Extract transcripts from 3 videos
python enhanced_youtube_extractor.py --max-videos 3 --no-resume
```

Expected output:
```
Processing batch 1/1 (3 videos)
Processing video 1/3: Daf Yomi Berachos Daf 2...
Successfully processed: Daf Yomi Berachos Daf 2...
...
Extraction completed successfully!
```

### Test 3: Content Organization
```bash
# Test content organization
python content_organizer.py --create-structure
```

Expected output:
```
Creating directory structure...
Directory structure created in: Mercaz_Daf_Yomi_Transcripts
```

## 🚀 Running Your First Extraction

### Option 1: Small Test Run
```bash
# Extract 10 videos for testing
python enhanced_youtube_extractor.py --max-videos 10
```

### Option 2: Full Channel Extraction
```bash
# Extract all videos (may take several hours)
python enhanced_youtube_extractor.py
```

### Option 3: Resume Interrupted Extraction
```bash
# Resume from where you left off
python enhanced_youtube_extractor.py
```

## 📁 Understanding the Output

After successful extraction, you'll find:

```
Mercaz_Daf_Yomi_Transcripts/
├── Berachos/
│   └── Daf_Yomi/
│       ├── Daf_Yomi_Berachos_Daf_2_l_JBZsSR7Tk.txt
│       └── ...
├── Shabbos/
├── Logs/
│   └── extraction_20231201_143022.log
├── Reports/
│   └── content_inventory_20231201_143500.json
├── master_catalog.csv
└── MASTER_INDEX.md
```

## 🔧 Troubleshooting Common Issues

### Issue 1: "ModuleNotFoundError"
**Problem**: Missing Python packages
**Solution**:
```bash
pip install -r requirements.txt
# Or install specific package:
pip install youtube-transcript-api
```

### Issue 2: "No transcript available"
**Problem**: Some videos don't have transcripts
**Solution**: This is normal. Check the failed videos report in logs.

### Issue 3: "API quota exceeded"
**Problem**: YouTube Data API daily limit reached
**Solution**:
- Wait 24 hours for quota reset
- Run without API key (transcript extraction still works)
- Reduce batch size

### Issue 4: "Rate limited"
**Problem**: Too many requests too quickly
**Solution**:
```json
{
  "rate_limit_seconds": 5,
  "batch_size": 25
}
```

### Issue 5: "Permission denied" (Linux/macOS)
**Problem**: File permission issues
**Solution**:
```bash
# Use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🔍 Monitoring Progress

### Check Logs
```bash
# View latest log file
tail -f Mercaz_Daf_Yomi_Transcripts/Logs/extraction_*.log
```

### Check Progress File
```bash
# View current progress
cat extraction_progress.json
```

### Monitor Output Directory
```bash
# Count extracted files
find Mercaz_Daf_Yomi_Transcripts -name "*.txt" | wc -l
```

## 🛠️ Advanced Configuration

### Custom Tractate Patterns
Add custom patterns to `config.json`:
```json
{
  "tractate_patterns": {
    "Custom_Series": ["custom", "special"],
    "Berachos": ["berachos", "berakhot", "brachot"]
  }
}
```

### Performance Tuning
For faster processing:
```json
{
  "batch_size": 100,
  "rate_limit_seconds": 1,
  "max_retries": 2
}
```

For more reliable processing:
```json
{
  "batch_size": 25,
  "rate_limit_seconds": 3,
  "max_retries": 5
}
```

## 📊 Usage Patterns

### Daily Extraction (New Videos)
```bash
# Check for new videos and extract
python enhanced_youtube_extractor.py --max-videos 50
```

### Weekly Full Sync
```bash
# Full channel sync
python enhanced_youtube_extractor.py
python content_organizer.py --all
```

### Monthly Organization
```bash
# Reorganize and generate reports
python content_organizer.py --organize-files --generate-reports
```

## 🔒 Security Best Practices

### API Key Security
1. **Never commit API keys to version control**
2. **Use environment variables**:
   ```bash
   export YOUTUBE_API_KEY="your_key_here"
   ```
3. **Restrict API key permissions** in Google Cloud Console

### File Permissions
```bash
# Set appropriate permissions
chmod 600 config.json  # Only owner can read/write
chmod 755 *.py         # Scripts executable by owner
```

## 📞 Getting Help

### Check System Status
```bash
# Verify Python installation
python --version

# Check installed packages
pip list | grep youtube

# Test basic functionality
python -c "from youtube_transcript_api import YouTubeTranscriptApi; print('OK')"
```

### Common Commands Reference
```bash
# Full extraction
python enhanced_youtube_extractor.py

# Test run
python enhanced_youtube_extractor.py --max-videos 5

# Channel analysis only
python enhanced_youtube_extractor.py --channel-scan-only

# Resume extraction
python enhanced_youtube_extractor.py

# Organize content
python content_organizer.py --all

# Channel discovery
python channel_discovery.py --api-key YOUR_KEY
```

## 🎯 Next Steps

After successful setup:

1. **Start with a test run** (5-10 videos)
2. **Review the output** and logs
3. **Adjust configuration** as needed
4. **Run full extraction** when satisfied
5. **Set up regular monitoring** for new videos

## 📋 Maintenance

### Regular Tasks
- **Weekly**: Check for new videos
- **Monthly**: Reorganize content and generate reports
- **Quarterly**: Update dependencies and review logs

### Updates
```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Check for YouTube API changes
# Review logs for new error patterns
```

---

**Congratulations!** You now have a fully functional enhanced YouTube transcript extraction system for the Mercaz Daf Yomi channel.