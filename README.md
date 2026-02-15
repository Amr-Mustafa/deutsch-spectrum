# DeutschSpectrum 🌈

A Chrome extension for German language learning with color-coded grammar analysis, verb-preposition detection, and built-in Anki support.

## For End Users

**Simple Installation (Coming Soon):**
1. Install from Chrome Web Store
2. Start using immediately - no setup required!

The extension will be available on the Chrome Web Store soon.

## Features

- 🎨 **Color-coded highlighting** for different parts of speech (nouns, verbs, adjectives, etc.)
- 🔍 **Shift+Click to analyze** - Click any German word to see detailed analysis
- 🎯 **Separable verb detection** - Correctly identifies and links separable verb parts (e.g., "aufstehen" → "steht...auf")
- 📚 **Verb-preposition patterns** - Highlights verbs with their required prepositions and cases
- 💡 **Reflexive verbs** - Recognizes "sich" constructions
- 📇 **Anki integration** - Send words directly to Anki with Ctrl+Shift+Click
- ⚡ **Fast and accurate** - Uses spaCy's advanced German NLP model (cloud-hosted)
- 🎛️ **Easy toggle** - Enable/disable highlighting with one click

## For Developers

Want to deploy your own version or contribute?

### Quick Setup (5 minutes)

#### 1. Deploy Backend to Railway (Free)

```bash
# Clone or fork this repo
git clone YOUR_REPO_URL
cd langlearn

# Push to your GitHub
git remote set-url origin YOUR_GITHUB_REPO
git push

# Then:
# 1. Go to https://railway.app
# 2. Sign in with GitHub
# 3. New Project → Deploy from GitHub repo
# 4. Select your repo
# 5. Set root directory to: backend
# 6. Railway auto-deploys! ✨
# 7. Generate a domain in Settings → Networking
```

See [backend/DEPLOYMENT.md](backend/DEPLOYMENT.md) for detailed instructions.

#### 2. Update Extension URL

After deploying, update the extension to use your backend:

1. Open `extension/popup/popup.html`
2. Find line ~110: `<input type="text" id="backend-url" value="http://localhost:8000">`
3. Change to: `<input type="text" id="backend-url" value="https://your-app.railway.app">`

#### 3. Load Extension in Chrome

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select the `extension` directory from this project
5. The extension icon should appear in your toolbar!

#### 4. Test It Out

1. Visit any website with German text (e.g., [German Wikipedia](https://de.wikipedia.org/))
2. Shift+Click on German words
3. Watch as the text gets color-coded by part of speech!

### Local Development (Optional)

If you want to develop locally without cloud deployment:

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download German language model (large, ~500MB)
python -m spacy download de_core_news_lg

# Run the server
uvicorn app.main:app --reload --port 8000
```

The backend will run at `http://localhost:8000`

## Usage

### Extension Controls

Click the extension icon to access controls:

- **Toggle** - Enable/disable highlighting
- **Color Legend** - See what each color represents
- **Backend URL** - Configure the API endpoint (default: `http://localhost:8000`)

### Color Scheme

- 🟥 **Light Pink** - Nouns (Substantive)
- 🟩 **Light Green** - Verbs
- 🟦 **Light Blue** - Adjectives (Adjektive)
- 🟨 **Light Yellow** - Adverbs
- 🟪 **Light Purple** - Determiners (Artikel)
- And more! (See popup for full legend)

## Development

### Project Structure

```
langlearn/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── pos_analyzer.py   # spaCy POS analysis
│   │   ├── separable_verbs.py# Separable verb detection
│   │   ├── models.py         # Pydantic models
│   │   └── cache.py          # Response caching
│   ├── tests/
│   └── requirements.txt
│
└── extension/         # Chrome extension
    ├── manifest.json         # Extension configuration
    ├── background.js         # Service worker
    ├── content/             # Content scripts
    │   ├── content.js       # Main orchestrator
    │   ├── text_extractor.js# Text extraction
    │   ├── highlighter.js   # DOM highlighting
    │   └── content.css      # Highlight styles
    ├── popup/              # Extension popup UI
    │   ├── popup.html
    │   ├── popup.js
    │   └── popup.css
    ├── config/
    │   └── pos_colors.js   # Color mappings
    └── icons/
```

### Backend API

The backend exposes several endpoints:

- `POST /api/v1/analyze` - Analyze German text and return POS tags
- `GET /api/v1/health` - Health check
- `GET /api/v1/pos-categories` - Get POS categories with colors
- `GET /api/v1/cache/stats` - Cache statistics

See backend documentation for details: [backend/README.md](backend/README.md)

### Running Tests

```bash
cd backend
pytest tests/
```

## How It Works

### Architecture

```
┌─────────────────┐         ┌──────────────────┐
│  Chrome Browser │  click  │  Cloud Backend   │
│   (Extension)   ├────────►│    (Railway)     │
│                 │◄────────┤  FastAPI+spaCy   │
│  Highlights     │ analysis│                  │
└─────────────────┘         └──────────────────┘
```

1. **Chrome Extension** (Frontend)
   - Captures user interactions (Shift+Click)
   - Extracts sentence context
   - Applies color-coded highlights

2. **FastAPI Backend** (Cloud-hosted)
   - Analyzes German text with spaCy
   - Detects POS tags, separable verbs, verb-prepositions
   - Returns structured token data

3. **Communication**
   - Extension → Backend: POST request with text
   - Backend → Extension: JSON with POS analysis
   - Cached for 5 minutes to reduce API calls

### Why Cloud Backend?

The spaCy German model is ~500MB and requires Python. By hosting it in the cloud:
- ✅ Users just install the extension - zero setup
- ✅ No Python installation required
- ✅ Works on any device with Chrome
- ✅ Automatic updates and improvements
- ✅ Free tier available (Railway/Render)

### Separable Verb Detection

German has separable verbs where the prefix separates from the verb in certain contexts:

- **Infinitive**: aufstehen (to stand up)
- **Conjugated**: "Ich **stehe** um 7 Uhr **auf**" (I get up at 7 o'clock)

The system uses spaCy's dependency parser to detect these relationships and highlights both parts with the same color, linking them together.

### Performance Optimizations

- **Backend caching** - Recent analyses are cached for 5 minutes
- **Debouncing** - Click events debounced (200ms) to reduce API calls
- **Efficient model loading** - spaCy model loaded once at startup
- **Free tier friendly** - Railway free tier handles personal use perfectly

## Troubleshooting

### Extension not working

1. **Check backend URL**: In extension popup, verify the backend URL is correct
2. **Test backend**: Visit `YOUR_BACKEND_URL/api/v1/health` - should return `{"status":"healthy"}`
3. **Check console**: Open DevTools (F12) and look for errors in the Console tab
4. **Reload extension**: Go to `chrome://extensions/` and click the reload icon

### No highlights appearing

1. **Check extension is enabled**: Click extension icon and ensure toggle is ON
2. **Shift+Click required**: Make sure you're Shift+Clicking words (not just hovering)
3. **Test on German text**: Try on German Wikipedia to confirm

### Backend/Cloud Issues

1. **Cold start delay**: First request after inactivity takes ~30 seconds (Railway free tier)
2. **Check Railway logs**: Go to Railway dashboard → Your service → Logs tab
3. **Model download failed**: Increase healthcheck timeout in railway.json and redeploy
4. **Out of free tier**: Railway free tier is $5/month worth - upgrade or switch to Render

### Local Development Issues

If running locally:
1. **Model not found**: Run `python -m spacy download de_core_news_lg`
2. **Port in use**: Change port: `uvicorn app.main:app --port 8001`
3. **CORS errors**: Backend allows all origins by default

## Future Enhancements

- [ ] Offline mode with lightweight model
- [ ] User-customizable color schemes
- [ ] Export highlighted text
- [ ] Learning/quiz mode
- [ ] Support for other languages (French, Spanish, etc.)
- [ ] Grammar statistics and insights

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

MIT License - feel free to use this project for learning or personal use.

## Acknowledgments

- [spaCy](https://spacy.io/) - Industrial-strength NLP library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- German language learners everywhere! 🇩🇪

---

**Made with ❤️ for German language learners**
