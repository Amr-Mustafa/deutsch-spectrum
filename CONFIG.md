# Configuration Guide - DeutschSpectrum

This project now supports easy switching between Railway production and local development environments.

## Chrome Extension Configuration

### Environment Presets

The extension includes three environment presets:

1. **Railway Production** (Default)
   - Backend URL: `https://deutsch-spectrum-production.up.railway.app`
   - Best for: End users, stable deployment

2. **Local Development**
   - Backend URL: `http://localhost:8000`
   - Best for: Development, testing

3. **Custom URL**
   - Allows you to specify any backend URL
   - Best for: Alternative deployments

### Changing Environment

1. Click the extension icon
2. Go to **Settings** tab
3. Select environment from the **Environment** dropdown
4. Backend URL updates automatically
5. Click **Save All Settings**

### Configuration Files

- `extension/config/config.js` - Environment configurations
- `extension/config/environments.json` - JSON version (optional)

### Adding New Environments

Edit `extension/config/config.js`:

```javascript
const ENVIRONMENTS = {
  // ... existing environments
  staging: {
    name: 'Staging Server',
    backendUrl: 'https://your-staging-url.com',
    apiTimeout: 30000,
    enableCache: true,
    cacheMaxAge: 3600000,
    enableLogging: true
  }
};
```

## Backend Configuration

### Environment Settings

The backend uses YAML configuration files for different environments.

Configuration file: `backend/config/config.yaml`

### Available Environments

1. **Development**
   - Host: 0.0.0.0
   - Port: 8000
   - Hot reload: Enabled
   - Logging: Debug level
   - CORS: Restricted to localhost and extensions

2. **Production** (Default)
   - Host: 0.0.0.0
   - Port: From $PORT environment variable
   - Hot reload: Disabled
   - Logging: Info level
   - CORS: Allow all origins

### Using Different Environments

Set the `ENVIRONMENT` environment variable:

```bash
# For local development
export ENVIRONMENT=development
python -m uvicorn app.main:app --reload

# For production (default)
export ENVIRONMENT=production
python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Configuration Options

Edit `backend/config/config.yaml`:

```yaml
environments:
  development:
    host: "0.0.0.0"
    port: 8000
    reload: true
    log_level: "debug"
    cors_origins:
      - "chrome-extension://*"
      - "http://localhost:*"
    spacy_model: "de_core_news_lg"
    cache_enabled: true
    cache_max_size: 1000
    cache_ttl: 3600
```

## Quick Start

### For End Users

1. Install the extension
2. Extension automatically uses Railway production backend
3. No configuration needed!

### For Developers

#### Local Development

1. **Start Backend:**
   ```bash
   cd backend
   pip install -r requirements.txt
   export ENVIRONMENT=development
   uvicorn app.main:app --reload
   ```

2. **Configure Extension:**
   - Load extension in Chrome
   - Go to Settings
   - Select "Local Development"
   - Save settings

#### Production Testing

1. **Configure Extension:**
   - Go to Settings
   - Select "Railway Production"
   - Save settings

2. Backend is already deployed at:
   ```
   https://deutsch-spectrum-production.up.railway.app
   ```

## Files Modified

### Extension
- `extension/manifest.json` - Added Railway URL to host_permissions
- `extension/config/config.js` - Environment configurations
- `extension/popup/popup.html` - Added environment selector
- `extension/popup/popup.js` - Environment switching logic
- `extension/background.js` - Default environment setup
- `extension/content/content.js` - Use environment config

### Backend
- `backend/config/config.yaml` - Environment configurations
- `backend/config/__init__.py` - Configuration loader
- `backend/requirements.txt` - Added PyYAML
- `requirements.txt` - Added PyYAML (root)

## Environment Variables

### Backend

- `ENVIRONMENT` - Set to `development` or `production`
- `PORT` - Port number (automatically set by Railway)

### Extension

Configuration is managed through Chrome's sync storage, accessible via the extension popup.

## Troubleshooting

### Extension can't connect to backend

1. Check environment selection in Settings
2. Verify backend URL is correct
3. For local: Ensure backend is running
4. For Railway: Check deployment status

### Backend configuration not loading

1. Verify `config.yaml` exists in `backend/config/`
2. Check YAML syntax is valid
3. Ensure PyYAML is installed: `pip install pyyaml`

### Changes not taking effect

1. **Extension**: Click "Save All Settings" after changes
2. **Backend**: Restart the server after config changes
3. **Railway**: Changes require a new deployment

## Best Practices

1. **Development**: Use local environment for faster testing
2. **Testing**: Use Railway production to test deployed version
3. **Custom**: Use for alternative deployments or testing new features
4. **Never commit** sensitive data in configuration files
5. **Use environment variables** for secrets and API keys

## Support

For issues or questions:
- Check Railway deployment logs
- Verify extension console for errors (F12 → Console)
- Review backend logs for API errors
