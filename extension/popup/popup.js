/**
 * Popup Script for German POS Highlighter
 * Handles user interactions in the extension popup
 */

// DOM elements
let enableToggle;
let statusText;
let environmentSelect;
let backendUrlInput;
let analyzeModifierSelect;
let ankiModifier1Select;
let ankiModifier2Select;
let ankiUrlInput;
let ankiDeckInput;
let ankiNoteTypeInput;
let testAnkiBtn;
let saveSettingsBtn;
let colorLegend;
let ankiStatusText;

/**
 * Initialize popup
 */
document.addEventListener('DOMContentLoaded', async () => {
  // Get DOM elements
  enableToggle = document.getElementById('enable-toggle');
  statusText = document.getElementById('status-text');
  environmentSelect = document.getElementById('environment-select');
  backendUrlInput = document.getElementById('backend-url');
  analyzeModifierSelect = document.getElementById('analyze-modifier');
  ankiModifier1Select = document.getElementById('anki-modifier1');
  ankiModifier2Select = document.getElementById('anki-modifier2');
  ankiUrlInput = document.getElementById('anki-url');
  ankiDeckInput = document.getElementById('anki-deck');
  ankiNoteTypeInput = document.getElementById('anki-note-type');
  testAnkiBtn = document.getElementById('test-anki');
  saveSettingsBtn = document.getElementById('save-settings');
  colorLegend = document.getElementById('color-legend');
  ankiStatusText = document.getElementById('anki-status');

  // Initialize tabs
  initializeTabs();

  // Load current settings
  await loadSettings();

  // Populate color legend
  populateColorLegend();

  // Attach event listeners
  enableToggle.addEventListener('change', handleToggleChange);
  environmentSelect.addEventListener('change', handleEnvironmentChange);
  testAnkiBtn.addEventListener('click', testAnkiConnection);
  saveSettingsBtn.addEventListener('click', handleSaveSettings);
});

/**
 * Initialize tab functionality
 */
function initializeTabs() {
  const tabButtons = document.querySelectorAll('.tab-btn');
  const tabPanes = document.querySelectorAll('.tab-pane');

  tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const targetTab = button.getAttribute('data-tab');

      // Remove active class from all buttons and panes
      tabButtons.forEach(btn => btn.classList.remove('active'));
      tabPanes.forEach(pane => pane.classList.remove('active'));

      // Add active class to clicked button and corresponding pane
      button.classList.add('active');
      document.getElementById(`${targetTab}-tab`).classList.add('active');
    });
  });
}

/**
 * Load settings from storage
 */
async function loadSettings() {
  try {
    const settings = await chrome.storage.sync.get([
      'enabled',
      'environment',
      'backendUrl',
      'analyzeModifier',
      'ankiModifier1',
      'ankiModifier2',
      'ankiUrl',
      'ankiDeck',
      'ankiNoteType'
    ]);

    // Set toggle state
    const isEnabled = settings.enabled !== false;
    enableToggle.checked = isEnabled;
    updateStatus(isEnabled);

    // Set environment and backend URL
    const environment = settings.environment || getDefaultEnvironment();
    environmentSelect.value = environment;

    // If no custom backendUrl saved, use environment default
    if (!settings.backendUrl) {
      const envConfig = getEnvironmentConfig(environment);
      backendUrlInput.value = envConfig.backendUrl;
    } else {
      backendUrlInput.value = settings.backendUrl;
    }

    // Update backend URL readonly state
    updateBackendUrlState();

    // Set hotkey modifiers
    analyzeModifierSelect.value = settings.analyzeModifier || 'shiftKey';
    ankiModifier1Select.value = settings.ankiModifier1 || 'ctrlKey';
    ankiModifier2Select.value = settings.ankiModifier2 || 'shiftKey';

    // Set Anki settings
    ankiUrlInput.value = settings.ankiUrl || 'http://localhost:8765';
    ankiDeckInput.value = settings.ankiDeck || 'German';
    ankiNoteTypeInput.value = settings.ankiNoteType || 'Basic';
  } catch (error) {
    console.error('Error loading settings:', error);
  }
}

/**
 * Handle environment change
 */
function handleEnvironmentChange() {
  const environment = environmentSelect.value;
  const envConfig = getEnvironmentConfig(environment);

  // Update backend URL from environment config
  backendUrlInput.value = envConfig.backendUrl;

  // Update readonly state
  updateBackendUrlState();
}

/**
 * Update backend URL input state based on environment
 */
function updateBackendUrlState() {
  const environment = environmentSelect.value;

  // Only allow editing for custom environment
  if (environment === 'custom') {
    backendUrlInput.removeAttribute('readonly');
    backendUrlInput.style.backgroundColor = '';
  } else {
    backendUrlInput.setAttribute('readonly', 'true');
    backendUrlInput.style.backgroundColor = '#f5f5f5';
  }
}

/**
 * Handle toggle change
 */
async function handleToggleChange(event) {
  const enabled = event.target.checked;

  try {
    // Save to storage
    await chrome.storage.sync.set({ enabled });

    // Update status text
    updateStatus(enabled);

    // Notify content scripts
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0]) {
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'toggleHighlighting',
        enabled: enabled
      }).catch(err => {
        console.log('Could not send message to content script:', err.message);
      });
    }
  } catch (error) {
    console.error('Error handling toggle change:', error);
  }
}

/**
 * Test Anki connection
 */
async function testAnkiConnection() {
  const ankiUrl = ankiUrlInput.value.trim();

  testAnkiBtn.textContent = 'Testing...';
  testAnkiBtn.disabled = true;

  try {
    const response = await fetch(ankiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'version',
        version: 6
      })
    });

    if (response.ok) {
      const data = await response.json();
      if (data.result) {
        ankiStatusText.textContent = `✓ Connected to AnkiConnect v${data.result}`;
        ankiStatusText.style.color = '#4CAF50';
      } else {
        ankiStatusText.textContent = '✗ AnkiConnect error: ' + (data.error || 'Unknown error');
        ankiStatusText.style.color = '#F44336';
      }
    } else {
      ankiStatusText.textContent = '✗ Cannot connect to Anki. Make sure Anki is running with AnkiConnect installed.';
      ankiStatusText.style.color = '#F44336';
    }
  } catch (error) {
    ankiStatusText.textContent = '✗ Connection failed. Is Anki running?';
    ankiStatusText.style.color = '#F44336';
  } finally {
    testAnkiBtn.textContent = 'Test Anki Connection';
    testAnkiBtn.disabled = false;
  }
}

/**
 * Handle save settings
 */
async function handleSaveSettings() {
  const backendUrl = backendUrlInput.value.trim();
  const ankiUrl = ankiUrlInput.value.trim();
  const ankiDeck = ankiDeckInput.value.trim();
  const ankiNoteType = ankiNoteTypeInput.value.trim();

  // Validate URLs
  try {
    new URL(backendUrl);
    new URL(ankiUrl);
  } catch {
    alert('Please enter valid URLs');
    return;
  }

  // Validate fields
  if (!ankiDeck || !ankiNoteType) {
    alert('Please fill in all Anki settings');
    return;
  }

  try {
    // Save all settings
    await chrome.storage.sync.set({
      environment: environmentSelect.value,
      backendUrl,
      analyzeModifier: analyzeModifierSelect.value,
      ankiModifier1: ankiModifier1Select.value,
      ankiModifier2: ankiModifier2Select.value,
      ankiUrl,
      ankiDeck,
      ankiNoteType
    });

    // Notify content scripts
    const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tabs[0]) {
      chrome.tabs.sendMessage(tabs[0].id, {
        action: 'settingsUpdated'
      }).catch(err => {
        console.log('Could not send message to content script:', err.message);
      });
    }

    // Show feedback
    saveSettingsBtn.textContent = 'Saved!';
    saveSettingsBtn.style.background = '#4CAF50';
    setTimeout(() => {
      saveSettingsBtn.textContent = 'Save All Settings';
      saveSettingsBtn.style.background = '#667eea';
    }, 2000);
  } catch (error) {
    alert('Error saving settings: ' + error.message);
  }
}

/**
 * Update status text
 */
function updateStatus(enabled) {
  if (enabled) {
    statusText.textContent = 'Active';
    statusText.classList.remove('disabled');
  } else {
    statusText.textContent = 'Disabled';
    statusText.classList.add('disabled');
  }
}

/**
 * Populate color legend
 */
function populateColorLegend() {
  // Clear existing items
  colorLegend.innerHTML = '';

  // Main POS categories to show (most common ones)
  const mainCategories = [
    'NOUN', 'VERB', 'VERB_PARTICLE', 'ADJ', 'ADV', 'DET',
    'PRON', 'ADP', 'CONJ', 'AUX', 'NUM', 'PROPN'
  ];

  // Create legend items
  mainCategories.forEach(pos => {
    const color = window.POS_COLORS[pos];
    const label = window.POS_LABELS[pos] || pos;

    if (color) {
      const item = document.createElement('div');
      item.className = 'legend-item';

      const colorBox = document.createElement('span');
      colorBox.className = 'color-box';
      colorBox.style.backgroundColor = color;
      colorBox.style.opacity = '0.5';

      const posLabel = document.createElement('span');
      posLabel.className = 'pos-label';
      posLabel.textContent = label;

      item.appendChild(colorBox);
      item.appendChild(posLabel);
      colorLegend.appendChild(item);
    }
  });
}
