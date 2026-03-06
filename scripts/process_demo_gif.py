import argparse
import os
import sys

try:
    from moviepy import VideoFileClip, CompositeVideoClip
    # vfx is the new location for fx in moviepy 2.0+
    # But let's check what's available or use clip methods directly
except ImportError:
    print("Error: moviepy not installed. Please run 'pip install moviepy'")
    sys.exit(1)

def apply_blur_to_center(clip, blur_ratio=0.5):
    """
    Apply a pixelation effect to the center of the video.
    blur_ratio: Size of the blurred area relative to the video size (0.5 = 50% width/height)
    """
    w, h = clip.size
    
    # Calculate center box dimensions
    box_w = int(w * blur_ratio)
    box_h = int(h * blur_ratio)
    
    # Calculate top-left corner
    x1 = (w - box_w) // 2
    y1 = (h - box_h) // 2
    
    # Crop the center region
    # In MoviePy 2.0+, use cropped() method
    center_region = clip.cropped(x1=x1, y1=y1, width=box_w, height=box_h)
    
    # Pixelate effect: resize down to very small, then back up to original size
    # This creates the blocky look
    # Factor 0.05 means 20x pixelation blocks
    pixelated = center_region.resized(0.05).resized(new_size=(box_w, box_h))
    
    # Set the position of the pixelated clip to where it was cropped from
    pixelated = pixelated.with_position((x1, y1))
    
    # Composite the pixelated patch over the original clip
    return CompositeVideoClip([clip, pixelated])

def process_video(input_path, output_path, end_time=60, resize_factor=0.5, fps=10):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    clip = None
    try:
        print(f"Loading video: {input_path}")
        clip = VideoFileClip(input_path)
        
        # 1. Trim to first minute (or less if video is shorter)
        original_duration = clip.duration
        trim_duration = min(original_duration, end_time)
        clip = clip.subclipped(0, trim_duration)
        print(f"Trimmed from {original_duration:.2f}s to {trim_duration:.2f}s.")
        
        # 2. Resize FIRST to reduce processing load
        if resize_factor:
            # MoviePy 2.x uses `kwarg` for scale if not first arg? No, it seems it takes first arg as scale factor if float
            clip = clip.resized(resize_factor)
            print(f"Resized by factor {resize_factor} to {clip.size}.")

        # 3. Apply Blur to Center (where file dialog usually is)
        # Assuming the user wants to hide file names in a dialog that pops up in the center
        # Since the dialog might not be there the whole time, this will blur the center for the WHOLE video.
        # Ideally we'd blur only when the dialog is open, but that requires manual timing.
        # For now, let's blur the center continuously as requested "privacy info mosaic".
        # Or maybe the user means just blur the file names? I can't detect text.
        # Center blur is the safest bet for a "file picker dialog".
        print("Applying mosaic to center area...")
        clip = apply_blur_to_center(clip, blur_ratio=0.6) # 60% of screen center

        # Write GIF
        print(f"Writing GIF to {output_path}...")
        # Optimize GIF generation - MoviePy 2.x changed parameters
        clip.write_gif(output_path, fps=fps) 
        print(f"Done! Saved to {output_path}")
        
    except Exception as e:
        print(f"Error processing video: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if clip:
            clip.close()

if __name__ == "__main__":
    input_file = "Screen Recording 2026-03-06 at 17.34.33.mov"
    # Check if file exists in current directory, if not check absolute path just in case
    if not os.path.exists(input_file):
        # Fallback to check absolute path if needed, but we copied it to .
        pass
        
    output_file = "docs/images/demo-assessment.gif"
    
    process_video(input_file, output_file)
