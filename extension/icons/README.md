# Extension Icons

This directory should contain three PNG icon files for the Chrome extension:

- `icon16.png` - 16x16 pixels (toolbar icon)
- `icon48.png` - 48x48 pixels (extension management page)
- `icon128.png` - 128x128 pixels (Chrome Web Store)

## Creating Icons

You can create these icons using any graphic design tool. Suggested design:
- A book icon with the German flag colors (black, red, gold)
- Or a highlighted text symbol
- Or the letter "De" for Deutsch

## Temporary Placeholder

For development purposes, you can use any simple PNG files. Here's how to create basic placeholder icons:

### Using Online Tools
1. Visit https://www.favicon-generator.org/
2. Upload a simple image or create one
3. Generate icons in the required sizes

### Using Python (PIL/Pillow)
```python
from PIL import Image, ImageDraw, ImageFont

def create_icon(size, filename):
    img = Image.new('RGB', (size, size), color=(103, 126, 234))
    draw = ImageDraw.Draw(img)
    text = "De"
    # Draw text in center
    draw.text((size//4, size//4), text, fill=(255, 255, 255))
    img.save(filename)

create_icon(16, 'icon16.png')
create_icon(48, 'icon48.png')
create_icon(128, 'icon128.png')
```

### Using ImageMagick
```bash
convert -size 16x16 xc:#667eea -pointsize 12 -fill white -gravity center -annotate +0+0 "De" icon16.png
convert -size 48x48 xc:#667eea -pointsize 32 -fill white -gravity center -annotate +0+0 "De" icon48.png
convert -size 128x128 xc:#667eea -pointsize 80 -fill white -gravity center -annotate +0+0 "De" icon128.png
```

## Note
The extension will not load without these icon files. Please create them before loading the extension in Chrome.
