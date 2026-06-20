// Configuration
const API_URL = 'https://igiari-backend.onrender.com/api/scan';
const MAX_CHARS = 4000;

// Example text from eval_002 (Straw Man fallacy) per spec
const EXAMPLE_TEXT = `COUNCILMEMBER A: I think we should pilot a four-day work week for city staff, just for six months, to see the data.
COUNCILMEMBER B: So you want to dismantle the entire structure of public service and let government grind to a halt?`;

// DOM elements
const textInput = document.getElementById('textInput');
const charCount = document.getElementById('charCount');
const scanButton = document.getElementById('scanButton');
const tryExampleButton = document.getElementById('tryExampleButton');
const resetButton = document.getElementById('resetButton');

const scanSection = document.getElementById('scanSection');
const resultsSection = document.getElementById('resultsSection');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');
const errorMessage = document.getElementById('errorMessage');
const noFallaciesState = document.getElementById('noFallaciesState');
const annotatedText = document.getElementById('annotatedText');
const findingsList = document.getElementById('findingsList');

// State
let currentText = '';
let currentFindings = [];

// Initialize
function init() {
    textInput.addEventListener('input', handleTextInput);
    scanButton.addEventListener('click', handleScan);
    tryExampleButton.addEventListener('click', handleTryExample);
    resetButton.addEventListener('click', handleReset);
    
    updateCharCount();
}

// Handle text input
function handleTextInput() {
    currentText = textInput.value;
    updateCharCount();
    updateScanButton();
}

// Update character counter
function updateCharCount() {
    const count = textInput.value.length;
    charCount.textContent = count;
    charCount.parentElement.classList.toggle('warning', count > MAX_CHARS * 0.9);
}

// Update scan button state
function updateScanButton() {
    const isEmpty = textInput.value.trim().length === 0;
    const isTooLong = textInput.value.length > MAX_CHARS;
    scanButton.disabled = isEmpty || isTooLong;
}

// Handle "Try an Example" button
function handleTryExample() {
    textInput.value = EXAMPLE_TEXT;
    handleTextInput();
    textInput.focus();
}

// Handle "Scan" button
async function handleScan() {
    const text = textInput.value.trim();
    
    if (!text) {
        showError('Please enter some text to scan.');
        return;
    }
    
    if (text.length > MAX_CHARS) {
        showError(`Text exceeds the ${MAX_CHARS.toLocaleString()} character limit. Please shorten your input.`);
        return;
    }
    
    // Show loading state
    hideError();
    showLoading();
    scanButton.disabled = true;
    
    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text }),
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            // Handle error responses from backend
            const errorDetail = data.detail || data.error || {};
            throw new Error(errorDetail.message || 'An error occurred while scanning.');
        }
        
        // Success - show results
        currentText = text;
        currentFindings = data.findings || [];
        showResults();
        
    } catch (error) {
        console.error('Scan error:', error);
        showError(error.message || 'Unable to connect to the server. Please try again.');
        scanButton.disabled = false;
    } finally {
        hideLoading();
    }
}

// Show loading state
function showLoading() {
    loadingState.classList.remove('hidden');
}

// Hide loading state
function hideLoading() {
    loadingState.classList.add('hidden');
}

// Show error
function showError(message) {
    errorMessage.textContent = message;
    errorState.classList.remove('hidden');
}

// Hide error
function hideError() {
    errorState.classList.add('hidden');
}

// Show results
function showResults() {
    // Hide scan section, show results section
    scanSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    if (currentFindings.length === 0) {
        // No fallacies found
        noFallaciesState.classList.remove('hidden');
        annotatedText.classList.add('hidden');
        findingsList.classList.add('hidden');
    } else {
        // Fallacies found
        noFallaciesState.classList.add('hidden');
        annotatedText.classList.remove('hidden');
        findingsList.classList.remove('hidden');
        
        renderAnnotatedText();
        renderFindingsList();
    }
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Render annotated text with highlights
function renderAnnotatedText() {
    // Sort findings by start_index (reverse order for correct insertion)
    const sortedFindings = [...currentFindings].sort((a, b) => b.start_index - a.start_index);
    
    let annotatedHTML = escapeHtml(currentText);
    
    // Insert highlights from end to start (so indices remain valid)
    sortedFindings.forEach((finding, index) => {
        const before = annotatedHTML.substring(0, finding.start_index);
        const span = annotatedHTML.substring(finding.start_index, finding.end_index);
        const after = annotatedHTML.substring(finding.end_index);
        
        const highlightHTML = `<span class="fallacy-highlight" data-finding-index="${index}">
            ${span}
            <span class="tooltip">
                <span class="tooltip-fallacy">${escapeHtml(finding.fallacy)}</span>
                <span class="tooltip-explanation">${escapeHtml(finding.explanation)}</span>
                <span class="tooltip-confidence">Confidence: ${escapeHtml(finding.confidence)}</span>
            </span>
        </span>`;
        
        annotatedHTML = before + highlightHTML + after;
    });
    
    annotatedText.innerHTML = annotatedHTML;
}

// Render findings list
function renderFindingsList() {
    findingsList.innerHTML = '';
    
    currentFindings.forEach((finding, index) => {
        const card = document.createElement('div');
        card.className = 'finding-card';
        
        card.innerHTML = `
            <div class="finding-header">
                <span class="finding-fallacy">${escapeHtml(finding.fallacy)}</span>
                <span class="finding-confidence">Confidence: ${escapeHtml(finding.confidence)}</span>
            </div>
            <div class="finding-category">${escapeHtml(finding.category)} › ${escapeHtml(finding.subcategory)}</div>
            <div class="finding-span">"${escapeHtml(finding.span)}"</div>
            <div class="finding-explanation">${escapeHtml(finding.explanation)}</div>
        `;
        
        findingsList.appendChild(card);
    });
}

// Handle reset/scan another
function handleReset() {
    // Reset state
    currentText = '';
    currentFindings = [];
    textInput.value = '';
    
    // Reset UI
    resultsSection.classList.add('hidden');
    scanSection.classList.remove('hidden');
    noFallaciesState.classList.add('hidden');
    hideError();
    updateCharCount();
    updateScanButton();
    
    // Focus input
    textInput.focus();
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
