import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont


def create_social_preview():
    # Configuration
    WIDTH, HEIGHT = 1280, 640
    # Use a high-contrast gradient or solid dark background
    BG_COLOR = "#0B1120"  # Very Dark Slate (almost black)
    TEXT_COLOR = "#F8FAFC" # Slate 50 (Very bright white)
    SUBTITLE_COLOR = "#CBD5E1" # Slate 300 (Light grey)
    ACCENT_COLOR = "#3B82F6"  # Blue 500 (Vibrant Blue)
    ACCENT_BG = "#1E3A8A" # Blue 900 (Dark Blue for tags)

    # Paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    images_dir = os.path.join(base_dir, "docs", "images")
    output_path = os.path.join(images_dir, "social-preview.png")

    mascot_path = os.path.join(images_dir, "docsentinel-mascot.png")
    screenshot_path = os.path.join(images_dir, "streamlit-dashboard.png")

    # Create base image
    img = Image.new('RGB', (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Try to load fonts (fallback to default if not found)
    try:
        # MacOS system fonts
        title_font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 100, index=1) # Bold
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/HelveticaNeue.ttc", 40)
        tag_font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 30)
    except OSError:
        try:
            # Linux/Other
            title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 100)
            subtitle_font = ImageFont.truetype("DejaVuSans.ttf", 40)
            tag_font = ImageFont.truetype("DejaVuSansMono.ttf", 30)
        except OSError:
            # Fallback
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            tag_font = ImageFont.load_default()
            print("Warning: Custom fonts not found, using default.")

    # --- Layout Logic ---
    # Left Block (Text + Mascot): x=80
    # Right Block (Screenshot): x=550 to 1280

    left_margin = 80

    # 1. Draw Mascot (Top Left)
    mascot_size = 150
    mascot_y = 80

    if os.path.exists(mascot_path):
        try:
            mascot = Image.open(mascot_path).convert("RGBA")

            # Create a circular mask/background for mascot
            # White background circle
            circle_bg = Image.new("RGBA", (mascot_size, mascot_size), (0,0,0,0))
            circle_draw = ImageDraw.Draw(circle_bg)
            circle_draw.ellipse((0, 0, mascot_size, mascot_size), fill="white")

            # Resize mascot to fit inside circle with some padding
            padding = 20
            inner_size = mascot_size - (padding * 2)
            mascot.thumbnail((inner_size, inner_size))

            # Center mascot in circle
            offset = ((mascot_size - mascot.width) // 2, (mascot_size - mascot.height) // 2)
            circle_bg.paste(mascot, offset, mascot)

            # Paste the composite icon onto the main image
            img.paste(circle_bg, (left_margin, mascot_y), circle_bg)

        except Exception as e:
            print(f"Could not process mascot: {e}")

    # 2. Draw Title (Below Mascot)
    title_y = mascot_y + mascot_size + 30
    draw.text((left_margin, title_y), "DocSentinel", font=title_font, fill=TEXT_COLOR)

    # 3. Draw Subtitle
    subtitle_y = title_y + 120
    draw.text((left_margin, subtitle_y), "Automated Security Assessment", font=subtitle_font, fill=SUBTITLE_COLOR)
    draw.text((left_margin, subtitle_y + 50), "with LLMs & RAG", font=subtitle_font, fill=SUBTITLE_COLOR)

    # 4. Draw Tags (Bottom Left)
    tag_x = left_margin
    tag_y = subtitle_y + 120
    tags = ["MCP Ready", "Local LLM", "Python"]

    for tag in tags:
        bbox = draw.textbbox((tag_x, tag_y), tag, font=tag_font)
        padding_x = 20
        padding_y = 10
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]

        pill_box = (
            tag_x,
            tag_y,
            tag_x + width + padding_x * 2,
            tag_y + height + padding_y * 2
        )

        draw.rounded_rectangle(pill_box, radius=10, fill=ACCENT_BG, outline=ACCENT_COLOR, width=2)
        draw.text((tag_x + padding_x, tag_y + padding_y), tag, font=tag_font, fill=TEXT_COLOR)

        tag_x += (width + padding_x * 2) + 20

    # --- Right Side: Screenshot ---
    if os.path.exists(screenshot_path):
        try:
            screenshot = Image.open(screenshot_path).convert("RGBA")

            # Target size for screenshot
            target_h = 500
            # Calculate width to maintain aspect ratio
            ratio = target_h / screenshot.height
            target_w = int(screenshot.width * ratio)

            screenshot = screenshot.resize((target_w, target_h), Image.Resampling.LANCZOS)

            # Position: Right aligned, vertically centered
            # Let it bleed off the right edge slightly or just padding
            screenshot_x = 1280 - target_w + 100 # Push it right a bit to crop empty space if wide
            if screenshot_x < 650: # Don't overlap text
                screenshot_x = 650

            screenshot_y = (HEIGHT - target_h) // 2

            # Add rounded corners
            mask = Image.new("L", screenshot.size, 0)
            draw_mask = ImageDraw.Draw(mask)
            draw_mask.rounded_rectangle((0, 0) + screenshot.size, radius=20, fill=255)

            # Shadow
            shadow_offset = 20
            shadow = Image.new("RGBA", (screenshot.width + shadow_offset*2, screenshot.height + shadow_offset*2), (0,0,0,0))
            shadow_draw = ImageDraw.Draw(shadow)
            # Draw shadow rect
            shadow_draw.rounded_rectangle(
                (shadow_offset, shadow_offset, shadow.width-shadow_offset, shadow.height-shadow_offset),
                radius=20,
                fill=(0,0,0, 80)
            )
            shadow = shadow.filter(ImageFilter.GaussianBlur(15))

            # Paste shadow then image
            img.paste(shadow, (screenshot_x - shadow_offset, screenshot_y - shadow_offset), shadow)
            img.paste(screenshot, (screenshot_x, screenshot_y), mask)

        except Exception as e:
            print(f"Could not process screenshot: {e}")

    # Save
    img.save(output_path)
    print(f"Social preview saved to {output_path}")

if __name__ == "__main__":
    create_social_preview()
