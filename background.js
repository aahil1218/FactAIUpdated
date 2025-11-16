// background.js (Updated for Custom Local API)
const LOCAL_API_ENDPOINT = 'http://127.0.0.1:5000/api/detect-ai';
const MIN_TEXT_LENGTH = 150; 

// --- Core Scan Function (Calls Local Python API) ---
async function performCustomScan(text) {
    if (text.length < MIN_TEXT_LENGTH) {
        return { error: `Text too short (${text.length} chars). Needs at least ${MIN_TEXT_LENGTH}.` };
    }
    
    try {
        const response = await fetch(LOCAL_API_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: text })
        });
        
        if (!response.ok) {
            throw new Error(`API failed with status ${response.status}. Is the Flask server running on port 5000?`);
        }
        
        const data = await response.json();
        
        if (data.error) {
            return { error: data.error };
        }

        return {
            summary: {
                ai: data.ai_score / 100,
                human: data.human_score / 100 
            },
            suggestions: data.suggestions // Received from API
        };

    } catch (error) {
        console.error('Custom API Scan Error:', error);
        return { error: error.message };
    }
}

// --- Message Listeners ---

// 1. Handles messages from popup.js (Manual Scan)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "scanText") {
        performCustomScan(request.text).then(sendResponse);
        return true; 
    }
});

// 2. Handles messages from content.js (Real-Time Scan)
let scanTimeout = null;
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "realTimeScan") {
        // Debounce: Wait 3 seconds of pause in typing before running scan
        clearTimeout(scanTimeout);
        scanTimeout = setTimeout(() => {
            console.log("Running real-time scan...");
            performCustomScan(request.text).then(result => {
                // Send result back to the Content Script
                chrome.tabs.sendMessage(sender.tab.id, {
                    action: "displayRealTimeResult",
                    result: result
                });
            });
        }, 3000); 
    }
});