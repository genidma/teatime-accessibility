#!/usr/bin/env python3
"""
Script to create simple test sprites for the TeaTime application.
"""

import cairo
import math

def create_sprite_frame(filename, frame_num, total_frames):
    """
    Create a simple animated sprite frame.
    
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
    
    # Draw a simple animated shape - a circle that changes color and position
    radius = 40
    center_x = 100 + 60 * math.cos(2 * math.pi * progress)
    center_y = 100 + 60 * math.sin(2 * math.pi * progress)
    
    # Change color based on frame
    hue = progress
    r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
    
    ctx.set_source_rgb(r, g, b)
    ctx.arc(center_x, center_y, radius, 0, 2 * math.pi)
    ctx.fill()
    
    # Add a border
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(3)
    ctx.arc(center_x, center_y, radius, 0, 2 * math.pi)
    ctx.stroke()
    
    # Save to PNG
    surface.write_to_png(filename)
    print(f"Created {filename}")

def hsv_to_rgb(h, s, v):
    """
    Convert HSV color values to RGB.
    
    Args:
        h: Hue (0.0 to 1.0)
        s: Saturation (0.0 to 1.0)
        v: Value (0.0 to 1.0)
    
    Returns:
        Tuple of (r, g, b) values in range 0.0 to 1.0
    """
    if s == 0.0:
        return (v, v, v)
    
    i = int(h * 6)
    f = (h * 6) - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    
    if i % 6 == 0:
        return (v, t, p)
    elif i % 6 == 1:
        return (q, v, p)
    elif i % 6 == 2:
        return (p, v, t)
    elif i % 6 == 3:
        return (p, q, v)
    elif i % 6 == 4:
        return (t, p, v)
    else:  # i % 6 == 5
        return (v, p, q)

def main():
    # Create 12 frames of animation
    num_frames = 12
    
    for i in range(num_frames):
        filename = f"sprite_frame_{i:02d}.png"
        create_sprite_frame(filename, i, num_frames)
    
    print(f"Created {num_frames} sprite frames")

if __name__ == "__main__":
    main()