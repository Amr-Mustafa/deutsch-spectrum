/**
 * Background Service Worker for German POS Highlighter
 * Manages extension state and badge
 */

// Import configuration (using importScripts for service workers)
importScripts('config/config.js');

// Initialize on install
chrome.runtime.onInstalled.addListener(() => {
  console.log('German POS Highlighter installed');

  // Get default environment configuration
  const defaultEnv = getDefaultEnvironment();
  const envConfig = getEnvironmentConfig(defaultEnv);

  // Set default values
  chrome.storage.sync.set({
    enabled: true,
    environment: defaultEnv,
    backendUrl: envConfig.backendUrl
  });

  // Set initial badge
  updateBadge(true);
});

// Listen for storage changes to update badge
chrome.storage.onChanged.addListener((changes, namespace) => {
  if (namespace === 'sync' && changes.enabled) {
    updateBadge(changes.enabled.newValue);
  }
});

/**
 * Update extension badge based on enabled state
 */
function updateBadge(enabled) {
  chrome.action.setBadgeText({
    text: enabled ? 'ON' : 'OFF'
  });

  chrome.action.setBadgeBackgroundColor({
    color: enabled ? '#4CAF50' : '#F44336'
  });
}

// Listen for messages from content scripts or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getSettings') {
    chrome.storage.sync.get(['enabled', 'backendUrl'], (settings) => {
      sendResponse(settings);
    });
    return true; // Keep channel open for async response
  }
});
