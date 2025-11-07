# Demo Creation Plan using Peek

## Overview

This document outlines a simplified approach to creating demos for the teatime-accessibility application using Peek for GIF creation, with a 20-minute duration, UTC timestamps, and a reminder for the calculate_time_elapsed.py script.

## Tools Required

1. **Peek** - For screen recording and GIF creation
2. **Terminal** - For setting up the environment and running commands
3. **teatime-accessibility** - The application to be demonstrated

## Process

### 1. Environment Setup

```bash
# Navigate to the project directory
cd /vms_and_github/Github/teatime-accessibility

# Ensure the application is working
python3 bin/teatime.py
```

### 2. Peek Configuration

1. Open Peek
2. Configure recording settings:
   - Set format to GIF
   - Set duration to 20 minutes (1200 seconds)
   - Set frame rate to 10 FPS (to keep file size reasonable)
   - Select appropriate screen area to capture the teatime app

### 3. Recording Session

1. Start recording with Peek
2. Launch teatime application:
   ```bash
   python3 bin/teatime.py
   ```

3. Demonstrate key features:
   - Setting timer duration
   - Starting and stopping the timer
   - Adjusting font size
   - Enabling/disabling sound
   - Mini-mode and nano-mode
   - Settings and customization options
   - - Animations
   - Statistics view
    - Export to CSV
    - Clear History (Done)
   - Credits
   - Review app critically to ascertain what other features need a demo


4. Stop recording after 20 minutes

### 4. Post-Processing

1. Save the GIF with a descriptive name
2. Optimize the GIF if needed to reduce file size:
   ```bash
   # If needed, use tools like gifsicle to optimize
   gifsicle -O3 output.gif -o optimized.gif
   ```

### 5. UTC Time Tracking

Start Time: _______ UTC
End Time: _______ UTC

### 6. Reminder for Time Calculation

Set up a reminder to run the calculate_time_elapsed.py script:

```bash
# Create a simple reminder script
echo "echo 'Remember to run calculate_time_elapsed.py script'" > reminder.sh
chmod +x reminder.sh

# Add to crontab to run daily at a specific time (e.g., 9:00 AM)
# (crontab -e) and add:
# 0 9 * * * /vms_and_github/Github/teatime-accessibility/reminder.sh
```

Note: Since the calculate_time_elapsed.py script doesn't exist in the project, we'll need to create it or confirm its location.

## Additional Notes

- Keep recordings focused and concise
- Ensure good lighting and clear screen visibility
- Test audio if demonstrating sound features
- Consider adding text overlays to highlight key features