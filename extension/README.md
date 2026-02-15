# German POS Highlighter - Chrome Extension

Chrome extension that highlights German parts of speech on hover using color-coded highlights.

## Features

- **Hover-based highlighting** - Simply hover over German text
- **Color-coded POS tags** - Different colors for nouns, verbs, adjectives, etc.
- **Separable verb support** - Correctly highlights both parts of separable verbs
- **Tooltips** - Shows lemma and POS category
- **Easy controls** - Toggle on/off with one click
- **Configurable** - Set custom backend URL

## Installation

### 1. Create Icons

Before loading the extension, you need to create the icon files:

```bash
cd icons

# Option 1: Use Python script (requires Pillow)
pip install pillow
python3 create_icons.py

# Option 2: Create manually
# See icons/README.md for instructions
```

### 2. Load Extension in Chrome

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right)
3. Click "Load unpacked"
4. Select this `extension` directory
5. The extension icon should appear in your toolbar

### 3. Start Backend Server

The extension requires the Python backend to be running:

```bash
cd ../backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

## Usage

### Basic Usage

1. **Navigate to German content** - Visit any website with German text
2. **Hover over words** - Move your mouse over German words
3. **See highlights** - Words are color-coded by part of speech
4. **Read tooltips** - Hover over highlights to see lemma and POS

### Extension Controls

Click the extension icon to access:

**Toggle Switch**
- Turn highlighting on/off
- Badge shows ON/OFF status

**Color Legend**
- See what each color represents
- Includes all major POS categories

**Settings**
- Configure backend URL
- Default: `http://localhost:8000`

## Architecture

### Files Overview

```
extension/
├── manifest.json           # Extension configuration (Manifest V3)
├── background.js           # Service worker for state management
├── content/               # Content scripts (injected into pages)
│   ├── content.js         # Main orchestrator
│   ├── text_extractor.js  # Extract text context from DOM
│   ├── highlighter.js     # Apply color highlights to DOM
│   └── content.css        # Highlight styles
├── popup/                # Extension popup UI
│   ├── popup.html        # UI structure
│   ├── popup.js          # UI logic
│   └── popup.css         # UI styles
├── config/
│   └── pos_colors.js     # POS → color mappings
└── icons/               # Extension icons
```

### How It Works

1. **Mouse Move Event** → Debounced (300ms)
2. **Extract Context** → TextExtractor gets sentence around cursor
3. **API Call** → Send context to backend for analysis
4. **Receive POS Tags** → Backend returns tokens with POS info
5. **Apply Highlights** → Highlighter wraps tokens in colored spans
6. **Show Tooltips** → Native browser tooltips on hover

### Content Scripts

#### content.js
Main orchestrator that:
- Listens for mouse move events
- Debounces hover events (300ms delay)
- Calls API to analyze text
- Coordinates highlighting

#### text_extractor.js
Handles text extraction:
- Gets word at cursor position
- Extracts sentence context (up to 300 chars)
- Handles German characters (ä, ö, ü, ß)
- Finds text boundaries

#### highlighter.js
DOM manipulation:
- Wraps tokens in `<span>` elements
- Applies color-coded backgrounds
- Adds tooltips with POS info
- Clears previous highlights

### State Management

**Local State** (content.js):
- `isExtensionEnabled` - Current toggle state
- `lastAnalyzedText` - Prevent re-analyzing same text
- `analysisCache` - Cache recent analyses (LRU, max 50)

**Chrome Storage** (chrome.storage.sync):
- `enabled` - Extension on/off state
- `backendUrl` - API endpoint URL

**Background Worker** (background.js):
- Updates badge (ON/OFF)
- Initializes default settings
- Handles messages between components

## Color Scheme

| POS | Color | Description |
|-----|-------|-------------|
| NOUN | 🟥 Light Pink | Nouns (Substantiv) |
| VERB | 🟩 Light Green | Verbs |
| VERB_PARTICLE | 🟩 Lighter Green | Separable verb particles |
| ADJ | 🟦 Light Blue | Adjectives (Adjektiv) |
| ADV | 🟨 Light Yellow | Adverbs |
| DET | 🟪 Light Purple | Determiners (Artikel) |
| PRON | 🟧 Peach | Pronouns (Pronomen) |
| ADP | 🟫 Dusty Rose | Prepositions (Präposition) |
| AUX | 🟦 Lavender | Auxiliary Verbs (Hilfsverb) |

See popup for complete legend.

## Customization

### Change Colors

Edit `config/pos_colors.js`:

```javascript
const POS_COLORS = {
  'NOUN': '#YOUR_COLOR',  // Change to your preferred color
  'VERB': '#YOUR_COLOR',
  // ...
};
```

### Change Backend URL

Two ways:
1. **Via Popup**: Click extension icon → Settings → Enter new URL → Save
2. **Via Code**: Edit default in `background.js`:
   ```javascript
   backendUrl: 'http://your-server:8000'
   ```

### Adjust Debounce Delay

Edit `content.js`:

```javascript
debounceTimer = setTimeout(() => {
  processHover(event);
}, 300);  // Change this value (milliseconds)
```

## Debugging

### Enable Developer Console

1. Right-click extension icon → "Inspect popup" (for popup debugging)
2. Open any webpage → F12 → Console (for content script debugging)
3. Go to `chrome://extensions/` → Extension details → "Inspect views: service worker" (for background debugging)

### Common Issues

**No highlights appearing:**
```javascript
// Check in console:
// 1. Is extension enabled?
console.log(isExtensionEnabled);

// 2. Is backend reachable?
fetch('http://localhost:8000/api/v1/health')
  .then(r => r.json())
  .then(console.log);

// 3. Any errors?
// Look for red errors in console
```

**CORS errors:**
```
Access to fetch at 'http://localhost:8000' has been blocked by CORS
```
→ Check backend CORS configuration allows `chrome-extension://*`

**Extension icon greyed out:**
→ Extension is disabled or has errors. Check `chrome://extensions/` for details

### Logging

Add debug logging to content.js:

```javascript
const DEBUG = true;

function log(...args) {
  if (DEBUG) console.log('[German POS]', ...args);
}
```

## Performance

### Optimizations Implemented

1. **Debouncing** - 300ms delay before processing hover
2. **Caching** - Recent analyses cached (max 50 entries)
3. **Smart highlighting** - Only re-highlight if text changed
4. **Passive listeners** - Mouse events use `{passive: true}`

### Performance Tips

- **Reduce debounce delay** for faster response (trade-off: more API calls)
- **Increase cache size** if analyzing same texts repeatedly
- **Disable on heavy pages** if performance degrades

## Security

### Permissions

The extension requests minimal permissions:

- `activeTab` - Access current tab when clicked
- `storage` - Save user preferences
- `host_permissions` - Connect to backend (localhost only)

### Content Security Policy

Manifest V3 enforces strict CSP:
- No inline scripts
- No eval()
- No remote code execution

All code must be in extension package.

## Publishing

To publish to Chrome Web Store:

1. **Create production icons** - Replace placeholders with professional graphics
2. **Update manifest** - Set appropriate version, description
3. **Create ZIP**:
   ```bash
   zip -r german-pos-highlighter.zip extension/
   ```
4. **Upload to Chrome Web Store** - https://chrome.google.com/webstore/devconsole

### Store Listing Requirements

- **Icon**: 128x128 (already in icons/)
- **Screenshots**: 1280x800 or 640x400
- **Promotional images**: 440x280 (optional)
- **Privacy policy**: If collecting data

## Future Enhancements

Potential features to add:

- [ ] **Keyboard shortcut** - Toggle highlighting with Ctrl+Shift+G
- [ ] **Right-click menu** - Analyze selected text
- [ ] **Options page** - More extensive settings
- [ ] **Custom colors** - Let users pick their own color scheme
- [ ] **Export** - Save highlighted text as HTML/PDF
- [ ] **Statistics** - Track learning progress
- [ ] **Flashcard mode** - Create flashcards from analyzed text

## Contributing

To contribute:

1. Fork the repository
2. Make your changes
3. Test thoroughly
4. Submit pull request

## License

MIT
