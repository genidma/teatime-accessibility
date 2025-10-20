#!/usr/bin/env python3
"""
Script to create puppy-themed sprites for the TeaTime application.
"""

import cairo
import math
import os

def create_puppy_sprite_frame(filename, frame_num, total_frames):
    """
    Create a puppy-themed animated sprite frame.
    
    Args:
        filename: Output PNG filename
        frame_num: Current frame number (0-based)
        total_frames: Total number of frames in the animation
    """
    # Create surface
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 200, 200)
    ctx = cairo.Context(surface)
    
    # Fill background with transparent color
    ctx.set_source_rgba(0, 0, 0, 0)  # Transparent
    ctx.paint()
    
    # Calculate animation progress (0.0 to 1.0)
    progress = frame_num / (total_frames - 1) if total_frames > 1 else 0
    
    # Draw a simple puppy face that animates (ears move, tail wags)
    
    # Draw head (circle)
    ctx.set_source_rgb(0.8, 0.6, 0.2)  # Golden brown color for head
    ctx.arc(100, 100, 50, 0, 2 * math.pi)
    ctx.fill()
    
    # Draw ears (they move with animation)
    ear_angle = 0.2 * math.sin(2 * math.pi * progress)
    
    # Left ear
    ctx.set_source_rgb(0.6, 0.4, 0.1)  # Darker brown for ears
    ctx.move_to(70, 60)
    ctx.line_to(60, 30 + 10 * math.sin(ear_angle))
    ctx.line_to(80, 50)
    ctx.close_path()
    ctx.fill()
    
    # Right ear
    ctx.move_to(130, 60)
    ctx.line_to(140, 30 + 10 * math.sin(ear_angle + math.pi))
    ctx.line_to(120, 50)
    ctx.close_path()
    ctx.fill()
    
    # Draw eyes
    ctx.set_source_rgb(0, 0, 0)  # Black eyes
    ctx.arc(85, 90, 8, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(115, 90, 8, 0, 2 * math.pi)
    ctx.fill()
    
    # Draw nose
    ctx.arc(100, 105, 5, 0, 2 * math.pi)
    ctx.fill()
    
    # Draw mouth (smile that changes with animation)
    ctx.set_line_width(3)
    ctx.move_to(85, 120)
    ctx.curve_to(100, 125 + 5 * math.sin(progress * math.pi), 100, 125 + 5 * math.sin(progress * math.pi), 115, 120)
    ctx.stroke()
    
    # Draw tail (wagging)
    ctx.set_line_width(8)
    ctx.move_to(150, 100)
    tail_end_x = 170 + 15 * math.cos(2 * math.pi * progress)
    tail_end_y = 90 + 15 * math.sin(2 * math.pi * progress)
    ctx.line_to(tail_end_x, tail_end_y)
    ctx.stroke()
    
    # Save to PNG
    surface.write_to_png(filename)
    print(f"Created {filename}")

def main():
    # Create 12 frames of animation
    num_frames = 12
    
    # Change to the puppy animation directory
    puppy_dir = "../assets/sprites/puppy_animation"
    if not os.path.exists(puppy_dir):
        os.makedirs(puppy_dir)
    
    os.chdir(puppy_dir)
    
    for i in range(num_frames):
        # Use puppy in the filename to distinguish from other animations
        filename = f"puppy_sprite_frame_{i:02d}.png"
        create_puppy_sprite_frame(filename, i, num_frames)
    
    print(f"Created {num_frames} puppy sprite frames in {puppy_dir}")

if __name__ == "__main__":
    main()