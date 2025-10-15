#!/usr/bin/env python3
"""
Script to create a GIF from sprite frames.
"""

from PIL import Image
import glob
import os

def create_gif():
    # Get all sprite frames
    frame_files = sorted(glob.glob("sprite_frame_*.png"))
    
    if not frame_files:
        print("No sprite frames found!")
        return
    
    print(f"Found {len(frame_files)} frames")
    
    # Open all frames
    frames = []
    for frame_file in frame_files:
        frame = Image.open(frame_file)
        frames.append(frame)
    
    # Save as GIF
    frames[0].save(
        'test_animation.gif',
        save_all=True,
        append_images=frames[1:],
        duration=200,  # 200ms per frame
        loop=0         # Infinite loop
    )
    
    print("Created test_animation.gif")

if __name__ == "__main__":
    create_gif()