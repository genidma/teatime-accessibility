# High CPU Usage Investigation and Resolution for kcresonance Branch

## Summary
This issue addresses the high CPU resource consumption observed in the kcresonance branch of the TeaTime Accessibility application. The branch introduces new UI features and testing infrastructure that appear to impact performance.

## Root Cause Analysis

### Primary Performance Issues Identified:

1. **Rainbow Timer System**:
   - The [_update_rainbow](file:///vms_and_github/Github/teatime-accessibility/bin/teatime/app.py#L491-L494) function runs every 1000ms updating UI colors
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
   - Dogtail test file had a missing [capture_ui_state](file:///vms_and_github/Github/teatime-accessibility/bin/teatime/app.py#L464-L466) method
   - This caused test failures but not runtime performance issues
   - Now fixed in [tests/test_ui_dogtail.py](file:///vms_and_github/Github/teatime-accessibility/tests/test_ui_dogtail.py)

### Important Clarification:
The UI testing components (Dogtail tests) do NOT run when the main application runs normally. They are separate test suites that run independently. The Dogtail tests are only executed when specifically running the test suite (e.g., via `pytest tests/test_ui_dogtail.py`). However, the test infrastructure was incorrectly referencing a non-existent method.

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
- Optimize the [_update_rainbow](file:///vms_and_github/Github/teatime-accessibility/bin/teatime/app.py#L491-L494) function to reduce frequency
- Implement frame caching for sprite animations

### Phase 2: Feature Improvements
- Add user controls to disable intensive features
- Implement conditional rendering based on window focus

### Phase 3: Long-term Enhancements
- Add performance monitoring to detect issues early
- Consider separating UI testing code from main application

## Files Modified
- [tests/test_ui_dogtail.py](file:///vms_and_github/Github/teatime-accessibility/tests/test_ui_dogtail.py) - Fixed missing [capture_ui_state](file:///vms_and_github/Github/teatime-accessibility/bin/teatime/app.py#L464-L466) method
- Created [kcresonance_performance_issue.md](file:///vms_and_github/Github/teatime-accessibility/kcresonance_performance_issue.md) - Complete analysis document

## Expected Outcomes
- Reduced idle CPU usage from current levels to under 5%
- Lower active timer CPU usage (target: under 10%)
- Improved responsiveness during fullscreen notifications
- Stable UI testing framework

## Priority
Medium-High - Performance degradation affects user experience but application remains functional