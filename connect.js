// content.js
if (window.location.hostname === 'docs.google.com') {
    console.log("AI Writing Assistant Content Script loaded on Google Docs.");
    
    const POLLING_INTERVAL = 2000; // Check for changes every 2 seconds
    const MIN_TEXT_LENGTH = 150;   
    let lastSentText = '';

    // Function to reliably extract text from the complex Google Docs editor DOM
    function getDocumentText() {
        // '.kix-lineview' is the common class for text lines in GDocs
        const textElements = document.querySelectorAll('.kix-lineview');
        let documentText = '';
        
        textElements.forEach(el => {
            // innerText is cleaner than textContent in this context
            documentText += el.innerText + '\n';
        });
        
        return documentText.trim();
    }

    function checkAndSendText() {
        const currentText = getDocumentText();

        if (currentText.length > MIN_TEXT_LENGTH && currentText !== lastSentText) {
            console.log("Text changed. Sending to background for real-time scan.");
            lastSentText = currentText;

            // Send the text to the background script for API processing
            chrome.runtime.sendMessage({
                action: "realTimeScan",
                text: currentText
            });
        }
    }

    // Start the continuous polling loop
    setInterval(checkAndSendText, POLLING_INTERVAL);
}

// Listener for results coming back from the background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "displayRealTimeResult") {
        const result = request.result;
        
        if (result.error) {
            console.error("Real-Time Scan Error:", result.error);
            // Use a non-intrusive notification for errors
            chrome.notifications.create({
                type: 'basic',
                iconUrl: 'icons/icon48.png',
                title: `AI Assistant Error: Server Offline?`,
                message: `Check Python API. Error: ${result.error.substring(0, 100)}`
            });
            return;
        }

        const aiScore = (result.summary.ai * 100).toFixed(1);
        const humanScore = (result.summary.human * 100).toFixed(1);
        const suggestionsText = result.suggestions.join(' | ');
        
        // Display results using the browser notification API
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon48.png',
            title: `AI Score: ${aiScore}% | Human Score: ${humanScore}%`,
            message: `Suggestions: ${suggestionsText}`
        });
    }
});