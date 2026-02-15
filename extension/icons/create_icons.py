#!/usr/bin/env python3
"""
Simple script to create placeholder icons for the Chrome extension.
Requires: pip install pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow library not found.")
    print("Please install it with: pip install pillow")
    exit(1)

def create_icon(size, filename):
    """Create a simple icon with 'De' text."""
    # Create image with purple background
    img = Image.new('RGB', (size, size), color=(103, 126, 234))
    draw = ImageDraw.Draw(img)

    # Add text
    text = "De"
    font_size = size // 2
    try:
        # Try to use a nice font if available
        font = ImageDraw.Font.truetype("/System/Library/Fonts/Helvetica.ttc", font_size)
    except:
        # Fall back to default font
        font = None

    # Calculate text position to center it
    if font:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    else:
        # Rough estimate for default font
        text_width = len(text) * (font_size // 2)
        text_height = font_size

    x = (size - text_width) // 2
    y = (size - text_height) // 2

    # Draw text
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # Save
    img.save(filename)
    print(f"Created {filename}")

if __name__ == "__main__":
    create_icon(16, 'icon16.png')
    create_icon(48, 'icon48.png')
    create_icon(128, 'icon128.png')
    print("\nIcons created successfully!")
    print("Note: These are placeholder icons. Consider creating better graphics for production.")
