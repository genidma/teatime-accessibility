# Issue: High CPU Usage in kcresonance Branch

## Description
The kcresonance branch of TeaTime Accessibility is experiencing high CPU resource consumption that impacts application performance. Initial analysis suggests several potential causes related to UI refresh rates and animation systems.

## Root Cause Analysis
Based on code review, potential causes of high CPU usage include:

1. **Rainbow Timer System**: The `_update_rainbow` function runs every 1000ms updating UI colors and reapplying CSS skin which may be computationally expensive.

2. **Sprite Animation System**: Fullscreen notifications trigger sprite animations every 100ms, which may consume excessive resources.

3. **Dynamic Skin System**: The CSS gradient animations and constant UI redraws may be causing performance bottlenecks.

4. **Missing Method in Tests**: The Dogtail test file (e.g., `<usual path>/test_dogtail.py`) references a `capture_ui_state` method that doesn't exist, causing test failures.

## Expected Behavior
- Idle CPU usage under 5%
- Active timer CPU usage under 10%
- Notification animation CPU usage under 15%

## Actual Behavior
High CPU usage observed during normal application operation, particularly when animations are active or the rainbow timer is running.

## Environment
- Branch: `kcresonance`
- Application: TeaTime Accessibility
- Platform: Linux with GTK 3

## Steps to Reproduce
1. Launch the application from the kcresonance branch
2. Monitor CPU usage with system tools like `top` or `htop`
3. Observe CPU usage during different states (idle, timer running, fullscreen notification)

## Proposed Solution
1. Optimize rainbow timer frequency or make it conditional
2. Improve animation efficiency with proper sprite frame caching
3. Implement conditional UI updates to reduce unnecessary redraws
4. Fix the missing method in Dogtail tests
5. Add performance monitoring to detect regressions early

## Priority
Medium-High - Performance issue affects user experience