# Sprite Animation for TeaTime Accessibility

This document explains how to create and use sprite animations in the TeaTime Accessibility application.

## How It Works

The TeaTime application can display animated sprites when a timer completes. It looks for sprite frames in this directory with specific naming conventions.

## Creating Sprites

### Option 1: Using an Existing GIF

If you have a GIF animation you'd like to use:

1. Convert the GIF to individual PNG frames
2. Name the frames `sprite_frame_00.png`, `sprite_frame_01.png`, etc.
3. Place them in this directory

You can use ImageMagick to convert a GIF to frames:
```bash
convert your_animation.gif -crop 1x1@ +repage +adjoin sprite_frame_%02d.png
```

### Option 2: Creating Frames Manually

Create individual PNG images and name them:
- `sprite_frame_00.png`
- `sprite_frame_01.png`
- `sprite_frame_02.png`
- etc.

The application will display them in alphabetical/numerical order.

## Requirements

- Frames should be PNG format for best compatibility
- Recommended size: 200x200 pixels (will be scaled automatically)
- All frames should be the same size for best visual results

## Fallback Behavior

If no sprite frames are found:
- The application will look for any PNG/JPG image in this directory to use as a static sprite
- If no images are found, no sprite animation will be displayed

## Testing Your Sprites

1. Place your sprite frames in this directory
2. Run the TeaTime application
3. Start a timer and wait for it to complete
4. You should see your sprite animation in the center of the screen

## Troubleshooting

If your sprites aren't displaying:

1. Check that the files are named correctly (`sprite_frame_*.png`)
2. Check that the files are in this directory
3. Check the application console for error messages
4. Ensure files are valid PNG images