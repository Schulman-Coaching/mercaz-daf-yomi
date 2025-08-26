// Sample data
const sampleVideos = [
    {
        id: "l_JBZsSR7Tk",
        title: "Daf Yomi Berachos Daf 2 by R' Eli Stefansky",
        url: "https://youtube.com/watch?v=l_JBZsSR7Tk",
        duration: "52:30",
        thumbnail: "placeholder-thumbnail.jpg",
        transcript_preview: "Good morning Borah high oh no Vicky mohavie Gianna las mohjas heh it's an extremely Mirage how do you see maracas in English I'm so Marui gosh I'm so excited so emotional that I forgot the word we this is a tremendous milestone building a building just for that fee I mean we believe it's one of a kind..."
    },
    {
        id: "TsChDzrEy9Q",
        title: "Daf Yomi Berachos Daf 3 by R' Eli Stefansky",
        url: "https://youtube.com/watch?v=TsChDzrEy9Q",
        duration: "48:15",
        thumbnail: "placeholder-thumbnail.jpg",
        transcript_preview: "If you miss today's shiur this is always a night shiur at 9:20 same place I do want to mention before we start we could have not have done this without you sure Aaron price and Gary Ben will share both over here until two o'clock in the morning before I begin..."
    },
    {
        id: "USjIWAjcoMc",
        title: "Daf Yomi Berachos Daf 4 by R' Eli Stefansky",
        url: "https://youtube.com/watch?v=USjIWAjcoMc",
        duration: "45:42",
        thumbnail: "placeholder-thumbnail.jpg",
        transcript_preview: "Welcome to today's Daf Yomi shiur. Today we continue our study of Massechet Berachos, focusing on the fundamental principles of prayer timing and the obligations of reciting the Shema..."
    },
    {
        id: "IdYMkJNAcYI",
        title: "Daf Yomi Berachos Daf 5 by R' Eli Stefansky",
        url: "https://youtube.com/watch?v=IdYMkJNAcYI",
        duration: "51:18",
        thumbnail: "placeholder-thumbnail.jpg",
        transcript_preview: "Today we explore the deeper concepts of kavannah in prayer and the importance of proper intention during the recitation of blessings. The Gemara discusses various opinions..."
    },
    {
        id: "hVR6zjpsJUk",
        title: "Daf Yomi Berachos Daf 6 by R' Eli Stefansky",
        url: "https://youtube.com/watch?v=hVR6zjpsJUk",
        duration: "49:33",
        thumbnail: "placeholder-thumbnail.jpg",
        transcript_preview: "In this shiur, we examine the concept of tefillin and their relationship to prayer. The discussion includes practical applications and the various halachic considerations..."
    }
];

// Application state
let videoQueue = [];
let extractionResults = [];
let isExtracting = false;

// DOM elements
const elements = {
    youtubeUrl: document.getElementById('youtube-url'),
    addVideoBtn: document.getElementById('add-video-btn'),
    loadExamplesBtn: document.getElementById('load-examples-btn'),
    videoList: document.getElementById('video-list'),
    selectAllBtn: document.getElementById('select-all-btn'),
    clearQueueBtn: document.getElementById('clear-queue-btn'),
    extractBtn: document.getElementById('extract-btn'),
    progressSection: document.getElementById('progress-section'),
    resultsSection: document.getElementById('results-section'),
    overallProgress: document.getElementById('overall-progress'),
    currentVideoProgress: document.getElementById('current-video-progress'),
    resultsList: document.getElementById('results-list'),
    downloadAllBtn: document.getElementById('download-all-btn'),
    exportFormat: document.getElementById('export-format')
};

// Utility functions
function extractVideoId(url) {
    const regex = /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/;
    const match = url.match(regex);
    return match ? match[1] : null;
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function generateMockTranscript(baseText, wordCount = 500) {
    const words = baseText.split(' ');
    const result = [];
    
    for (let i = 0; i < wordCount; i++) {
        result.push(words[i % words.length]);
    }
    
    return result.join(' ');
}

// Video queue management
function addVideoToQueue(videoData) {
    // Check if video already exists
    if (videoQueue.find(v => v.id === videoData.id)) {
        alert('Video already in queue');
        return;
    }
    
    videoQueue.push({
        ...videoData,
        selected: true,
        status: 'pending'
    });
    
    renderVideoList();
    updateExtractButton();
}

function removeVideoFromQueue(videoId) {
    videoQueue = videoQueue.filter(v => v.id !== videoId);
    renderVideoList();
    updateExtractButton();
}

function toggleVideoSelection(videoId) {
    const video = videoQueue.find(v => v.id === videoId);
    if (video) {
        video.selected = !video.selected;
        updateExtractButton();
    }
}

function selectAllVideos() {
    videoQueue.forEach(video => {
        video.selected = true;
    });
    renderVideoList();
    updateExtractButton();
}

function clearQueue() {
    videoQueue = [];
    renderVideoList();
    updateExtractButton();
}

function updateExtractButton() {
    const selectedCount = videoQueue.filter(v => v.selected).length;
    elements.extractBtn.disabled = selectedCount === 0 || isExtracting;
    elements.extractBtn.textContent = selectedCount > 0 ? 
        `Extract Transcripts (${selectedCount} selected)` : 
        'Extract Transcripts';
}

// UI rendering
function renderVideoList() {
    if (videoQueue.length === 0) {
        elements.videoList.innerHTML = `
            <div class="empty-state">
                <p>No videos added yet. Add videos using the form above or load examples.</p>
            </div>
        `;
        return;
    }
    
    elements.videoList.innerHTML = videoQueue.map(video => `
        <div class="video-item">
            <input type="checkbox" class="video-item__checkbox" 
                   ${video.selected ? 'checked' : ''} 
                   onchange="toggleVideoSelection('${video.id}')"
                   ${isExtracting ? 'disabled' : ''}>
            <div class="video-item__thumbnail">
                📹 ${video.duration}
            </div>
            <div class="video-item__content">
                <div class="video-item__title">${video.title}</div>
                <div class="video-item__url">${video.url}</div>
                <div class="video-item__duration">Duration: ${video.duration}</div>
            </div>
            <div class="video-item__status">
                <span class="status status--${getStatusClass(video.status)}">${video.status}</span>
            </div>
            <button class="video-item__remove" onclick="removeVideoFromQueue('${video.id}')" 
                    ${isExtracting ? 'disabled' : ''}>
                ✕
            </button>
        </div>
    `).join('');
}

function getStatusClass(status) {
    switch (status) {
        case 'pending': return 'info';
        case 'processing': return 'warning';
        case 'complete': return 'success';
        case 'error': return 'error';
        default: return 'info';
    }
}

function renderResults() {
    if (extractionResults.length === 0) {
        elements.resultsList.innerHTML = '<div class="empty-state"><p>No results yet.</p></div>';
        return;
    }
    
    elements.resultsList.innerHTML = extractionResults.map(result => `
        <div class="result-item">
            <div class="result-item__header">
                <h4 class="result-item__title">${result.title}</h4>
                <button class="result-item__download" onclick="downloadTranscript('${result.id}')">
                    Download
                </button>
            </div>
            <div class="result-item__preview">${result.transcript_preview}</div>
            <div class="result-item__stats">
                <span>Word Count: ${result.wordCount}</span>
                <span>Duration: ${result.duration}</span>
                <span>Quality: ${result.quality}</span>
            </div>
        </div>
    `).join('');
}

// Extraction simulation
async function startExtraction() {
    if (isExtracting) return;
    
    isExtracting = true;
    const selectedVideos = videoQueue.filter(v => v.selected);
    
    // Show progress section
    elements.progressSection.classList.remove('hidden');
    elements.progressSection.classList.add('fade-in');
    
    // Reset results
    extractionResults = [];
    elements.resultsSection.classList.add('hidden');
    
    // Update UI
    updateExtractButton();
    renderVideoList();
    
    try {
        for (let i = 0; i < selectedVideos.length; i++) {
            const video = selectedVideos[i];
            
            // Update overall progress
            updateOverallProgress(i, selectedVideos.length);
            
            // Update current video progress
            updateCurrentVideoProgress(video.title, 'Connecting...');
            
            // Mark video as processing
            video.status = 'processing';
            renderVideoList();
            
            // Simulate extraction stages
            await simulateExtractionStages(video);
            
            // Mark as complete
            video.status = 'complete';
            renderVideoList();
            
            // Add to results
            const transcript = generateMockTranscript(video.transcript_preview, 800);
            extractionResults.push({
                ...video,
                transcript: transcript,
                wordCount: transcript.split(' ').length,
                quality: 'Auto-generated'
            });
        }
        
        // Complete extraction
        updateOverallProgress(selectedVideos.length, selectedVideos.length);
        updateCurrentVideoProgress('', 'All extractions complete!');
        
        // Show results
        setTimeout(() => {
            elements.resultsSection.classList.remove('hidden');
            elements.resultsSection.classList.add('fade-in');
            renderResults();
        }, 1000);
        
    } catch (error) {
        console.error('Extraction error:', error);
        alert('An error occurred during extraction. Please try again.');
    } finally {
        isExtracting = false;
        updateExtractButton();
        renderVideoList();
    }
}

async function simulateExtractionStages(video) {
    const stages = [
        { text: 'Connecting to YouTube...', duration: 1000 },
        { text: 'Fetching video metadata...', duration: 800 },
        { text: 'Extracting transcript...', duration: 1500 },
        { text: 'Processing text...', duration: 700 },
        { text: 'Finalizing...', duration: 500 }
    ];
    
    for (let i = 0; i < stages.length; i++) {
        const stage = stages[i];
        updateCurrentVideoProgress(video.title, stage.text);
        updateCurrentVideoProgressBar((i + 1) / stages.length * 100);
        await sleep(stage.duration);
    }
}

function updateOverallProgress(current, total) {
    const percentage = (current / total) * 100;
    elements.overallProgress.querySelector('.progress-fill').style.width = `${percentage}%`;
    elements.overallProgress.querySelector('.progress-text').textContent = `${current} / ${total} videos processed`;
}

function updateCurrentVideoProgress(title, status) {
    elements.currentVideoProgress.querySelector('.progress-text').textContent = title ? `${title}: ${status}` : status;
}

function updateCurrentVideoProgressBar(percentage) {
    elements.currentVideoProgress.querySelector('.progress-fill').style.width = `${percentage}%`;
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Download functions
function downloadTranscript(videoId) {
    const result = extractionResults.find(r => r.id === videoId);
    if (!result) return;
    
    const format = elements.exportFormat.value;
    let content, filename, mimeType;
    
    switch (format) {
        case 'txt':
            content = result.transcript;
            filename = `${result.title.replace(/[^a-zA-Z0-9]/g, '_')}.txt`;
            mimeType = 'text/plain';
            break;
        case 'csv':
            content = `Title,URL,Duration,Word Count,Transcript\n"${result.title}","${result.url}","${result.duration}","${result.wordCount}","${result.transcript.replace(/"/g, '""')}"`;
            filename = `${result.title.replace(/[^a-zA-Z0-9]/g, '_')}.csv`;
            mimeType = 'text/csv';
            break;
        case 'json':
            content = JSON.stringify({
                title: result.title,
                url: result.url,
                duration: result.duration,
                wordCount: result.wordCount,
                transcript: result.transcript
            }, null, 2);
            filename = `${result.title.replace(/[^a-zA-Z0-9]/g, '_')}.json`;
            mimeType = 'application/json';
            break;
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

function downloadAllTranscripts() {
    const format = elements.exportFormat.value;
    let content, filename, mimeType;
    
    switch (format) {
        case 'txt':
            content = extractionResults.map(result => 
                `=== ${result.title} ===\n${result.transcript}\n\n`
            ).join('');
            filename = 'all_transcripts.txt';
            mimeType = 'text/plain';
            break;
        case 'csv':
            const csvHeader = 'Title,URL,Duration,Word Count,Transcript\n';
            const csvRows = extractionResults.map(result => 
                `"${result.title}","${result.url}","${result.duration}","${result.wordCount}","${result.transcript.replace(/"/g, '""')}"`
            ).join('\n');
            content = csvHeader + csvRows;
            filename = 'all_transcripts.csv';
            mimeType = 'text/csv';
            break;
        case 'json':
            content = JSON.stringify(extractionResults.map(result => ({
                title: result.title,
                url: result.url,
                duration: result.duration,
                wordCount: result.wordCount,
                transcript: result.transcript
            })), null, 2);
            filename = 'all_transcripts.json';
            mimeType = 'application/json';
            break;
    }
    
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Event listeners
elements.addVideoBtn.addEventListener('click', () => {
    const url = elements.youtubeUrl.value.trim();
    if (!url) {
        alert('Please enter a YouTube URL');
        return;
    }
    
    const videoId = extractVideoId(url);
    if (!videoId) {
        alert('Please enter a valid YouTube URL');
        return;
    }
    
    // Create mock video data
    const videoData = {
        id: videoId,
        title: `YouTube Video ${videoId}`,
        url: url,
        duration: formatDuration(Math.floor(Math.random() * 3600) + 300),
        transcript_preview: "This is a sample transcript preview. In a real application, this would be extracted from the actual video content..."
    };
    
    addVideoToQueue(videoData);
    elements.youtubeUrl.value = '';
});

elements.loadExamplesBtn.addEventListener('click', () => {
    sampleVideos.forEach(video => {
        if (!videoQueue.find(v => v.id === video.id)) {
            addVideoToQueue(video);
        }
    });
});

elements.selectAllBtn.addEventListener('click', selectAllVideos);
elements.clearQueueBtn.addEventListener('click', clearQueue);
elements.extractBtn.addEventListener('click', startExtraction);
elements.downloadAllBtn.addEventListener('click', downloadAllTranscripts);

// Allow Enter key to add video
elements.youtubeUrl.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        elements.addVideoBtn.click();
    }
});

// Global functions for inline event handlers
window.toggleVideoSelection = toggleVideoSelection;
window.removeVideoFromQueue = removeVideoFromQueue;
window.downloadTranscript = downloadTranscript;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    renderVideoList();
    updateExtractButton();
});