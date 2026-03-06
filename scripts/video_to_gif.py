import argparse
import os
import sys

try:
    from moviepy import VideoFileClip
except ImportError:
    print("Error: moviepy not installed. Please run 'pip install moviepy'")
    sys.exit(1)

def convert_video_to_gif(input_path, output_path=None, start_time=None, end_time=None, resize=None, fps=10):
    if not os.path.exists(input_path):
        print(f"Error: Input file '{input_path}' not found.")
        return

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".gif"

    clip = None
    try:
        clip = VideoFileClip(input_path)
        
        # Trim if needed
        if start_time is not None or end_time is not None:
            # Handle default end_time if only start_time is provided
            end = end_time if end_time is not None else clip.duration
            start = start_time if start_time is not None else 0
            clip = clip.subclipped(start, end)
            
        # Resize if needed (e.g. 0.5 for 50% scale)
        if resize:
            # Use scale parameter for resizing by factor
            clip = clip.resized(scale=resize)
            
        # Write GIF
        print(f"Converting '{input_path}' to '{output_path}'...")
        print(f"Settings: FPS={fps}, Resize={resize}, Duration={clip.duration:.2f}s")
        clip.write_gif(output_path, fps=fps)
        print("Done!")
        
    except Exception as e:
        print(f"Error during conversion: {e}")
    finally:
        if clip:
            clip.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert video to GIF using MoviePy")
    parser.add_argument("input", help="Path to input video file")
    parser.add_argument("--output", "-o", help="Path to output GIF file")
    parser.add_argument("--start", "-s", type=float, help="Start time in seconds")
    parser.add_argument("--end", "-e", type=float, help="End time in seconds")
    parser.add_argument("--resize", "-r", type=float, help="Resize factor (e.g. 0.5)")
    parser.add_argument("--fps", "-f", type=int, default=10, help="Frames per second (default: 10)")
    
    args = parser.parse_args()
    
    convert_video_to_gif(args.input, args.output, args.start, args.end, args.resize, args.fps)
