/**
 * Main Content Script
 * Click with customizable hotkey to analyze German words
 * Different hotkey to send to Anki
 */

// Global state
let isExtensionEnabled = true;
// Get default API base URL from config
let API_BASE_URL = getEnvironmentConfig(getDefaultEnvironment()).backendUrl;

// Hotkey settings
let analyzeModifier = 'shiftKey';
let ankiModifier1 = 'ctrlKey';
let ankiModifier2 = 'shiftKey';

// Anki settings
let ANKI_URL = 'http://localhost:8765';
let ANKI_DECK = 'German';
let ANKI_NOTE_TYPE = 'Basic';

// Cache for analyzed sentences
const sentenceCache = new Map();
const CACHE_MAX_SIZE = 100;

// Track last analyzed word for Anki export
let lastAnalyzedWord = null;
let lastAnalyzedSentence = null;
let lastAnalysisResult = null;

// Prevent auto-clear immediately after highlighting
let justHighlighted = false;

/**
 * Initialize the content script
 */
async function init() {
  try {
    // Load settings from storage
    const settings = await chrome.storage.sync.get([
      'enabled',
      'backendUrl',
      'analyzeModifier',
      'ankiModifier1',
      'ankiModifier2',
      'ankiUrl',
      'ankiDeck',
      'ankiNoteType'
    ]);

    isExtensionEnabled = settings.enabled !== false;
    API_BASE_URL = settings.backendUrl || getEnvironmentConfig(getDefaultEnvironment()).backendUrl;

    // Load hotkey settings
    analyzeModifier = settings.analyzeModifier || 'shiftKey';
    ankiModifier1 = settings.ankiModifier1 || 'ctrlKey';
    ankiModifier2 = settings.ankiModifier2 || 'shiftKey';

    // Load Anki settings
    ANKI_URL = settings.ankiUrl || 'http://localhost:8765';
    ANKI_DECK = settings.ankiDeck || 'German';
    ANKI_NOTE_TYPE = settings.ankiNoteType || 'Basic';

    if (isExtensionEnabled) {
      attachEventListeners();
      console.log('German POS Highlighter initialized');
      console.log(`Analyze: ${analyzeModifier.replace('Key', '')}+Click`);
      console.log(`Send to Anki: ${ankiModifier1.replace('Key', '')}+${ankiModifier2.replace('Key', '')}+Click`);
    }
  } catch (error) {
    console.error('Error initializing German POS Highlighter:', error);
  }
}

/**
 * Attach event listeners to the document
 */
function attachEventListeners() {
  // Listen for clicks with modifier keys
  document.addEventListener('click', handleClick, true);

  // Listen for clicks to auto-clear highlights (separate listener with bubbling phase)
  document.addEventListener('click', handleAutoClear, false);

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'toggleHighlighting') {
      isExtensionEnabled = message.enabled;
      if (!isExtensionEnabled) {
        clearAllHighlights();
      }
    } else if (message.action === 'settingsUpdated') {
      // Reload settings
      init();
    }
  });
}

/**
 * Auto-clear highlights when clicking elsewhere
 */
function handleAutoClear(event) {
  if (!isExtensionEnabled) return;

  // Don't clear if we just highlighted (prevent immediate clear)
  if (justHighlighted) {
    justHighlighted = false;
    return;
  }

  // Check if clicking on a highlight or inside a highlight
  let element = event.target;
  let isHighlight = false;

  // Check if clicked element or any parent is a highlight
  while (element && element !== document) {
    if (element.classList && element.classList.contains('german-pos-highlight')) {
      isHighlight = true;
      break;
    }
    element = element.parentElement;
  }

  // Clear highlights if not clicking on a highlight
  if (!isHighlight) {
    if (window.Highlighter && typeof window.Highlighter.clearAllHighlights === 'function') {
      window.Highlighter.clearAllHighlights();
    }
  }
}

/**
 * Handle click events - check for analyze or Anki hotkey
 */
async function handleClick(event) {
  if (!isExtensionEnabled) return;

  const isAnalyzeHotkey = checkHotkey(event, [analyzeModifier]);
  const isAnkiHotkey = checkHotkey(event, [ankiModifier1, ankiModifier2]);

  if (isAnalyzeHotkey) {
    // Analyze word
    event.preventDefault();
    event.stopPropagation();
    await handleAnalyzeWord(event);
  } else if (isAnkiHotkey) {
    // Send to Anki
    event.preventDefault();
    event.stopPropagation();
    await handleSendToAnki(event);
  }
}

/**
 * Check if correct hotkey combination is pressed
 */
function checkHotkey(event, modifiers) {
  // Filter out empty modifiers
  modifiers = modifiers.filter(m => m && m !== '');

  if (modifiers.length === 0) return false;

  // Check all required modifiers are pressed
  for (const modifier of modifiers) {
    if (!event[modifier]) {
      return false;
    }
  }

  // Check no extra modifiers are pressed
  const allModifiers = ['shiftKey', 'ctrlKey', 'altKey', 'metaKey'];
  for (const modifier of allModifiers) {
    if (!modifiers.includes(modifier) && event[modifier]) {
      return false;
    }
  }

  return true;
}

/**
 * Handle analyze word action
 */
async function handleAnalyzeWord(event) {
  try {
    // Get the clicked position
    const range = document.caretRangeFromPoint(event.clientX, event.clientY);
    if (!range) return;

    // Extract the word at click position
    const word = getWordAtPosition(range);
    if (!word) {
      console.log('No word found at click position');
      return;
    }

    console.log(`Analyzing word: "${word}"`);

    // Extract the full sentence containing this word
    const sentence = getFullSentence(range);
    if (!sentence) {
      console.log('Could not extract sentence');
      return;
    }

    console.log(`Sentence: "${sentence}"`);

    // Check cache first
    let analysis = sentenceCache.get(sentence);

    if (!analysis) {
      // Analyze the sentence
      const wordPosition = sentence.indexOf(word);
      analysis = await analyzeText({
        text: sentence,
        target_word: word,
        target_position: wordPosition
      });

      if (analysis) {
        // Cache the analysis
        addToCache(sentence, analysis);
        console.log(`Cached analysis for sentence (${analysis.tokens.length} tokens)`);
      } else {
        console.error('Analysis failed');
        return;
      }
    } else {
      console.log('Using cached analysis');
    }

    // Store for Anki export
    lastAnalyzedWord = word;
    lastAnalyzedSentence = sentence;
    lastAnalysisResult = analysis;

    // Clear previous highlights
    clearAllHighlights();

    // Find the container element
    const container = getTextContainer(range);
    if (container) {
      // Apply highlights (only for the clicked word and its separable parts)
      window.Highlighter.applyHighlights(container, analysis, sentence, word);
      // Set flag to prevent immediate auto-clear
      justHighlighted = true;
    }

    console.log(`✓ Word highlighted. Use ${ankiModifier1.replace('Key', '')}+${ankiModifier2.replace('Key', '')}+Click to send to Anki`);
  } catch (error) {
    console.error('Error analyzing word:', error);
  }
}

/**
 * Handle send to Anki action
 */
async function handleSendToAnki(event) {
  try {
    // Get the clicked word
    const range = document.caretRangeFromPoint(event.clientX, event.clientY);
    if (!range) return;

    const word = getWordAtPosition(range);
    if (!word) {
      console.log('No word found to send to Anki');
      return;
    }

    // If we don't have analysis for this word, analyze it first
    if (!lastAnalyzedWord || lastAnalyzedWord !== word) {
      console.log('Analyzing word before sending to Anki...');
      await handleAnalyzeWord(event);
    }

    if (!lastAnalysisResult) {
      console.error('No analysis available for this word');
      return;
    }

    // Find the token for this word
    const token = lastAnalysisResult.tokens.find(t =>
      t.text.toLowerCase() === word.toLowerCase()
    );

    if (!token) {
      console.error('Token not found in analysis');
      return;
    }

    // Send to Anki
    console.log(`Sending "${word}" to Anki...`);
    await sendToAnki(word, token, lastAnalyzedSentence);
  } catch (error) {
    console.error('Error sending to Anki:', error);
  }
}

/**
 * Send word to Anki
 */
async function sendToAnki(word, token, sentence) {
  try {
    // Prepare card fields
    const front = word;
    const back = buildBackField(token, sentence);

    // Create note
    const response = await fetch(ANKI_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'addNote',
        version: 6,
        params: {
          note: {
            deckName: ANKI_DECK,
            modelName: ANKI_NOTE_TYPE,
            fields: {
              Front: front,
              Back: back
            },
            options: {
              allowDuplicate: false
            },
            tags: ['german-pos-highlighter']
          }
        }
      })
    });

    if (!response.ok) {
      throw new Error('Anki request failed');
    }

    const data = await response.json();

    if (data.error) {
      console.error('Anki error:', data.error);
      alert(`Anki error: ${data.error}\n\nMake sure:\n1. Anki is running\n2. AnkiConnect is installed\n3. Deck "${ANKI_DECK}" exists\n4. Note type "${ANKI_NOTE_TYPE}" has Front/Back fields`);
    } else {
      console.log(`✓ Card added to Anki (ID: ${data.result})`);

      // Visual feedback
      showNotification(`✓ Added "${word}" to Anki`);
    }
  } catch (error) {
    console.error('Failed to send to Anki:', error);
    alert(`Failed to connect to Anki.\n\nMake sure Anki is running with AnkiConnect installed.`);
  }
}

/**
 * Build the back field for Anki card
 */
function buildBackField(token, sentence) {
  let back = '';

  // Add lemma (dictionary form)
  back += `<b>Lemma:</b> ${token.lemma}<br>`;

  // Add POS
  const posLabel = window.POS_LABELS?.[token.pos] || token.pos;
  back += `<b>Part of Speech:</b> ${posLabel}<br>`;

  // Add separable verb info
  if (token.is_separable && token.separable_parts) {
    back += `<b>Separable Verb:</b> ${token.separable_parts.join(' ... ')}<br>`;
  }

  // Add example sentence
  back += `<br><b>Example:</b><br><i>${sentence}</i>`;

  return back;
}

/**
 * Show temporary notification
 */
function showNotification(message) {
  const notification = document.createElement('div');
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: #4CAF50;
    color: white;
    padding: 15px 20px;
    border-radius: 5px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    z-index: 100000;
    font-family: Arial, sans-serif;
    font-size: 14px;
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.remove();
  }, 3000);
}

/**
 * Get word at a specific position
 */
function getWordAtPosition(range) {
  const node = range.startContainer;
  if (node.nodeType !== Node.TEXT_NODE) return null;

  const text = node.textContent;
  const offset = range.startOffset;

  // German word pattern
  const wordPattern = /[a-zA-ZäöüÄÖÜß]+/g;
  let match;

  while ((match = wordPattern.exec(text)) !== null) {
    const start = match.index;
    const end = match.index + match[0].length;

    if (offset >= start && offset <= end) {
      return match[0];
    }
  }

  return null;
}

/**
 * Get the full sentence containing the range
 */
function getFullSentence(range) {
  const node = range.startContainer;
  if (!node) return null;

  let container = node.nodeType === Node.TEXT_NODE ? node.parentElement : node;

  while (container && !isTextContainer(container)) {
    container = container.parentElement;
  }

  if (!container) return null;

  const fullText = container.textContent;
  const cursorPosition = getCursorPositionInContainer(range, container);
  const sentence = extractSentence(fullText, cursorPosition);

  return sentence || fullText;
}

function isTextContainer(element) {
  const tag = element.tagName.toLowerCase();
  return ['p', 'div', 'span', 'article', 'section', 'li', 'td', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag);
}

function getCursorPositionInContainer(range, container) {
  const preRange = document.createRange();
  preRange.selectNodeContents(container);
  preRange.setEnd(range.startContainer, range.startOffset);
  return preRange.toString().length;
}

function extractSentence(text, position) {
  let sentenceStart = 0;
  let sentenceEnd = text.length;

  // Break only on sentence endings (periods, exclamation marks, question marks)
  const boundaries = /[.!?]/;

  // Find sentence start (work backwards from position)
  for (let i = position - 1; i >= 0; i--) {
    if (boundaries.test(text[i])) {
      sentenceStart = i + 1;
      break;
    }
  }

  // Find sentence end (work forwards from position)
  for (let i = position; i < text.length; i++) {
    if (boundaries.test(text[i])) {
      sentenceEnd = i + 1;
      break;
    }
  }

  return text.substring(sentenceStart, sentenceEnd).trim();
}

/**
 * Call the backend API to analyze text
 */
async function analyzeText(context) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/analyze`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(context)
    });

    if (!response.ok) {
      console.error(`API error: ${response.status}`);
      return null;
    }

    return await response.json();
  } catch (error) {
    console.error('Error calling API:', error);
    return null;
  }
}

function getTextContainer(range) {
  let node = range.startContainer;

  if (node.nodeType === Node.TEXT_NODE) {
    node = node.parentElement;
  }

  while (node && node !== document.body) {
    const tag = node.tagName.toLowerCase();
    if (['p', 'div', 'span', 'article', 'section', 'li', 'td', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(tag)) {
      return node;
    }
    node = node.parentElement;
  }

  return document.body;
}

function addToCache(sentence, analysis) {
  if (sentenceCache.size >= CACHE_MAX_SIZE) {
    const firstKey = sentenceCache.keys().next().value;
    sentenceCache.delete(firstKey);
  }
  sentenceCache.set(sentence, analysis);
}

function clearAllHighlights() {
  if (window.Highlighter) {
    window.Highlighter.clearAllHighlights();
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
