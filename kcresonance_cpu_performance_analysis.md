# High CPU Usage Investigation and Resolution for kcresonance Branch

## Summary
This document provides a comprehensive analysis of the high CPU resource consumption observed in the kcresonance branch of the TeaTime Accessibility application. The branch introduces new UI features and testing infrastructure that appear to impact performance.

## Issue Description
The kcresonance branch of TeaTime Accessibility is experiencing high CPU resource consumption that impacts application performance. Initial analysis suggests several potential causes related to UI refresh rates and animation systems.

## Root Cause Analysis

### Primary Performance Issues Identified:

1. **Rainbow Timer System**:
   - The `_update_rainbow` function runs every 1000ms updating UI colors
   - Constantly reapplies CSS skin which is computationally expensive
   - Could be optimized to run less frequently or only when window is focused

2. **Sprite Animation System**:
   - Fullscreen notifications trigger sprite animations every 100ms
   - Image loading and rendering consumes excessive resources
   - Should implement proper sprite frame caching

3. **Dynamic Skin System**:
   - CSS gradients and animations cause frequent UI redraws
   - The lava lamp skin applies complex animations every second
   - Needs optimization for performance

4. **UI Testing Infrastructure Bug**:
   - Dogtail test file had a missing `capture_ui_state` method
   - This caused test failures but not runtime performance issues
   - Now fixed in `<usual path>/tests/test_ui_dogtail.py`

### Important Clarification:
The UI testing components (Dogtail tests) do NOT run when the main application runs normally. They are separate test suites that run independently. The Dogtail tests are only executed when specifically running the test suite (e.g., via `pytest <usual path>/tests/test_ui_dogtail.py`). However, the test infrastructure was incorrectly referencing a non-existent method.

## Diagnostic Steps

### Phase 1: Baseline Performance Measurement
1. Run the application in isolation with minimal features enabled
2. Monitor CPU usage with `top` or `htop` while the app is idle
3. Record baseline CPU usage without timer running
4. Record CPU usage with timer running

### Phase 2: Feature Isolation
1. Disable rainbow effects and measure CPU usage
2. Disable sprite animations and measure CPU usage
3. Test with default skin vs. lava lamp skin
4. Test in different modes (normal, mini, nano)

### Phase 3: Profiling
1. Use Python profiling tools to identify hotspots
2. Profile the application with `cProfile` or similar tools
3. Identify functions with highest execution frequency

## Recommended Solutions

### Immediate Actions:
1. **Optimize Rainbow Timer Frequency**:
   - Increase the interval from 1000ms to 2000ms or higher
   - Only run when the application window is focused

2. **Improve Animation Efficiency**:
   - Implement proper sprite frame caching
   - Reduce animation frequency when window is not focused
   - Add option to disable animations completely

3. **Conditional UI Updates**:
   - Only apply skin changes when settings actually change
   - Implement dirty checking to reduce unnecessary redraws

### Code-level Optimizations:
1. **Update the rainbow timer mechanism** to be less resource intensive
2. **Implement frame caching** for sprite animations
3. **Add performance controls** to allow users to disable intensive features

## Implementation Plan

### Phase 1: Immediate Fixes
- Optimize the `_update_rainbow` function to reduce frequency
- Implement frame caching for sprite animations

### Phase 2: Feature Improvements
- Add user controls to disable intensive features
- Implement conditional rendering based on window focus

### Phase 3: Long-term Enhancements
- Add performance monitoring to detect issues early
- Consider separating UI testing code from main application

## Expected Behavior vs Actual Behavior
- Expected: Idle CPU usage under 5%, active timer CPU usage under 10%
- Observed: High CPU usage during normal application operation, particularly when animations are active or the rainbow timer is running

## Success Metrics
- Idle CPU usage under 5%
- Active timer CPU usage under 10%
- Notification animation CPU usage under 15%
- Consistent performance across different display scales

## Timeline
- Phase 1 (Days 1-2): Baseline measurements and profiling
- Phase 2 (Days 3-4): Implement immediate fixes
- Phase 3 (Days 5-7): Test improvements and optimize further

## Files Modified
- `<usual path>/tests/test_ui_dogtail.py` - Fixed missing `capture_ui_state` method

## Risk Mitigation
- Always test changes in a separate branch
- Maintain backward compatibility
- Keep performance improvements optional if needed
- Thoroughly test accessibility features aren't affected

## Priority
Medium-High - Performance degradation affects user experience but application remains functional