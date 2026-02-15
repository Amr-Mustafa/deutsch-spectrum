# Quick Start Guide

Get your German POS Highlighter running in 5 minutes!

## Step 1: Install Backend Dependencies (2 min)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download de_core_news_lg
```

⏳ The spaCy model download is ~500MB and may take a few minutes.

## Step 2: Start Backend Server (30 sec)

```bash
# Make sure you're in the backend directory with venv activated
uvicorn app.main:app --reload --port 8000
```

✅ You should see: "Application startup complete"

Test it: Visit http://localhost:8000/docs in your browser

## Step 3: Create Extension Icons (1 min)

```bash
cd ../extension/icons

# If you have Python Pillow installed:
pip install pillow
python3 create_icons.py

# Otherwise, create simple placeholders manually
# (Any PNG files named icon16.png, icon48.png, icon128.png will work for testing)
```

## Step 4: Load Extension in Chrome (1 min)

1. Open Chrome
2. Go to `chrome://extensions/`
3. Enable "Developer mode" (top right)
4. Click "Load unpacked"
5. Select the `extension` folder
6. Done! 🎉

## Step 5: Test It! (30 sec)

1. Visit https://de.wikipedia.org/wiki/Deutschland
2. Hover over German words
3. Watch them light up with colors!

## Troubleshooting

### Backend not starting?

**Error**: `ModuleNotFoundError: No module named 'fastapi'`
- **Fix**: `pip install -r requirements.txt`

**Error**: `OSError: Can't find model 'de_core_news_lg'`
- **Fix**: `python -m spacy download de_core_news_lg`

### Extension not working?

**No highlights appearing:**
1. Check backend is running: http://localhost:8000/docs
2. Click extension icon → Check toggle is ON
3. Open DevTools (F12) → Look for errors

**Icons missing:**
- Create placeholder PNGs in `extension/icons/`
- Any 16x16, 48x48, 128x128 PNG files will work

### Still stuck?

Check the full README.md or extension/README.md for detailed troubleshooting.

## What to Try

Once it's working:

- ✅ Hover over "Ich stehe auf" → See separable verb detection
- ✅ Try different websites with German content
- ✅ Click extension icon → Explore the color legend
- ✅ Toggle on/off to see the difference

## Next Steps

- Read [README.md](README.md) for full features
- Check [backend/README.md](backend/README.md) for API details
- Explore [extension/README.md](extension/README.md) for customization

Enjoy learning German! 🇩🇪
