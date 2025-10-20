#!/usr/bin/env python3
"""
Script to create puppy-themed sprites for the TeaTime application.
"""

import cairo
import math
import os

def create_puppy_sprite_frame(filename, frame_num, total_frames):
    """
    Create a cute puppy-themed animated sprite frame.
    
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
    
    # Draw a cute puppy face
    
    # Draw head (circle)
    ctx.set_source_rgb(1.0, 0.9, 0.7)  # Light cream color for head
    ctx.arc(100, 100, 50, 0, 2 * math.pi)
    ctx.fill()
    
    # Draw ears (floppy ears that move gently)
    ear_angle = 0.1 * math.sin(2 * math.pi * progress)
    
    # Left ear (bigger, floppier)
    ctx.set_source_rgb(0.9, 0.7, 0.4)  # Cream/brown color for ears
    ctx.move_to(75, 65)
    ctx.curve_to(60, 50 + 10 * math.sin(ear_angle), 
                 70, 30 + 5 * math.sin(ear_angle), 
                 85, 45)
    ctx.close_path()
    ctx.fill()
    
    # Right ear
    ctx.move_to(125, 65)
    ctx.curve_to(140, 50 + 10 * math.sin(ear_angle + math.pi/2), 
                 130, 30 + 5 * math.sin(ear_angle + math.pi/2), 
                 115, 45)
    ctx.close_path()
    ctx.fill()
    
    # Draw eyes (bigger and brighter to look cuter)
    # Eye whites
    ctx.set_source_rgb(1, 1, 1)
    ctx.arc(85, 90, 10, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(115, 90, 10, 0, 2 * math.pi)
    ctx.fill()
    
    # Eye pupils (they move slightly to look more alive)
    ctx.set_source_rgb(0, 0, 0)
    pupil_offset = 2 * math.sin(2 * math.pi * progress)
    ctx.arc(85 + pupil_offset, 90, 5, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(115 + pupil_offset, 90, 5, 0, 2 * math.pi)
    ctx.fill()
    
    # Eye shine (to make them look cuter)
    ctx.set_source_rgb(1, 1, 1)
    ctx.arc(83 + pupil_offset, 88, 1.5, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(113 + pupil_offset, 88, 1.5, 0, 2 * math.pi)
    ctx.fill()
    
    # Draw nose (smaller and more cute)
    ctx.set_source_rgb(0.2, 0.1, 0.0)
    ctx.arc(100, 105, 4, 0, 2 * math.pi)
    ctx.fill()
    
    # Draw mouth (smile that changes with animation)
    ctx.set_source_rgb(0.5, 0.2, 0.1)  # Brown color for mouth
    ctx.set_line_width(2)
    ctx.move_to(90, 115)
    # Create a smiling mouth that moves with animation
    smile_factor = 0.5 + 0.5 * math.sin(progress * math.pi)
    ctx.curve_to(100, 120 + 5 * smile_factor, 100, 120 + 5 * smile_factor, 110, 115)
    ctx.stroke()
    
    # Draw tongue (to make it look cuter)
    if progress > 0.5:  # Tongue appears in second half of animation
        ctx.set_source_rgb(1.0, 0.7, 0.7)  # Pink tongue
        ctx.arc(100, 120 + 3 * smile_factor, 3, 0, math.pi)
        ctx.fill()
    
    # Draw cheeks (rosy cheeks for cuteness)
    ctx.set_source_rgba(1.0, 0.7, 0.7, 0.3)  # Light pink, semi-transparent
    ctx.arc(75, 105, 8, 0, 2 * math.pi)
    ctx.fill()
    ctx.arc(125, 105, 8, 0, 2 * math.pi)
    ctx.fill()
    
    # Draw tail (wagging, shorter than before)
    ctx.set_source_rgb(0.9, 0.7, 0.4)  # Same color as ears
    ctx.set_line_width(6)
    ctx.move_to(150, 100)
    # Shorter tail with wagging motion
    tail_end_x = 160 + 5 * math.cos(2 * math.pi * progress)
    tail_end_y = 95 + 5 * math.sin(2 * math.pi * progress)
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
    
    # Remove old frames
    for i in range(num_frames):
        filename = f"puppy_sprite_frame_{i:02d}.png"
        if os.path.exists(filename):
            os.remove(filename)
    
    # Create new frames
    for i in range(num_frames):
        # Use puppy in the filename to distinguish from other animations
        filename = f"puppy_sprite_frame_{i:02d}.png"
        create_puppy_sprite_frame(filename, i, num_frames)
    
    print(f"Created {num_frames} cute puppy sprite frames in {puppy_dir}")

if __name__ == "__main__":
    main()