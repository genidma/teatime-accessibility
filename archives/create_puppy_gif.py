#!/usr/bin/env python3
"""
Script to create a GIF from puppy sprite frames.
"""

from PIL import Image
import glob
import os

def create_puppy_gif():
    # Change to the puppy animation directory
    puppy_dir = "../assets/sprites/puppy_animation"
    os.chdir(puppy_dir)
    
    # Remove old GIF if it exists
    if os.path.exists("puppy_animation.gif"):
        os.remove("puppy_animation.gif")
    
    # Get all puppy sprite frames
    frame_files = sorted(glob.glob("puppy_sprite_frame_*.png"))
    
    if not frame_files:
        print("No puppy sprite frames found!")
        return
    
    print(f"Found {len(frame_files)} frames")
    
    # Open all frames
    frames = []
    for frame_file in frame_files:
        frame = Image.open(frame_file)
        frames.append(frame)
    
    # Save as animated GIF
    output_gif = "puppy_animation.gif"
    frames[0].save(
        output_gif,
        save_all=True,
        append_images=frames[1:],
        duration=100,  # 100ms per frame = 10 FPS
        loop=0  # Infinite loop
    )
    
    print(f"Created {output_gif} with {len(frames)} frames")

if __name__ == "__main__":
    create_puppy_gif()