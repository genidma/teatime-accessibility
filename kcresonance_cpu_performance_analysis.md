# KCResonance CPU Usage Investigation (Source of Record)

## Summary
High CPU usage has been observed in the kcresonance branch of TeaTime Accessibility. This document consolidates analysis, diagnostics, and mitigation plans.

## Branch Details
- Branch: `kcresonance`
- Application name: "teatime kcresonance" (version 1.0.2)
- Key additions: Enhanced UI features, Dogtail UI testing, new animation systems

## Issue Description
The kcresonance branch exhibits elevated CPU usage, especially during UI animation and refresh activity.

## Root Cause Analysis

### Primary Performance Issues Identified
1. **Rainbow Timer System**
   - `_update_rainbow` runs every 1000ms to update UI colors.
   - Reapplies CSS skin each tick, which can be expensive.
   - Optimize to run less frequently or only when the window is focused.

2. **Sprite Animation System**
   - Fullscreen notifications trigger sprite animations every 100ms.
   - Image loading/rendering can be costly without frame caching.

3. **Dynamic Skin System**
   - CSS gradients/animations cause frequent redraws.
   - Lava lamp skin applies complex animations continuously.

4. **UI Testing Infrastructure Bug**
   - Dogtail test file previously referenced a missing `capture_ui_state` method.
   - This affected test runs only, not runtime performance.
   - Fixed in `<usual path>/tests/test_ui_dogtail.py`.

### Important Clarification
Dogtail tests do NOT run during normal app execution. They only run when explicitly invoked (e.g., `pytest <usual path>/tests/test_ui_dogtail.py`).

## Diagnostics

### Phase 1: Baseline Performance Measurement
1. Run the app with minimal features enabled.
2. Monitor CPU with `top` or `htop` while idle.
3. Record baseline CPU usage without timer running.
4. Record CPU usage with timer running.

### Phase 2: Feature Isolation
1. Disable rainbow effects; measure CPU.
2. Disable sprite animations; measure CPU.
3. Test default skin vs. lava lamp skin.
4. Test normal/mini/nano modes.

### Phase 3: Profiling
1. Use Python profiling tools to identify hotspots.
2. Profile with `cProfile` or similar.
3. Identify functions with highest execution frequency.

## CPU Data Collection (Linux)
Use the repo script to capture process and thread CPU usage over time.

### Script
- Path: `debug/kcresonance_cpu_probe.sh`
- Purpose: Captures top CPU processes, matched kcresonance processes, and per-thread CPU for matched PIDs.

### Example
```
chmod +x debug/kcresonance_cpu_probe.sh
debug/kcresonance_cpu_probe.sh -d 300 -i 1 -m 'teatime|KCResonance|kcresonance'
```

### Outputs
- `debug/cpu-probe-YYYYmmdd-HHMMSS/top_processes.csv`
- `debug/cpu-probe-YYYYmmdd-HHMMSS/targets.csv`
- `debug/cpu-probe-YYYYmmdd-HHMMSS/threads.txt`
- `debug/cpu-probe-YYYYmmdd-HHMMSS/system.txt`

### Suggested Run Matrix
1. Idle baseline (2-5 minutes).
2. Rainbow on/off.
3. Lava skin on/off.
4. Trigger fullscreen notification (sprite animation).

## Recommended Solutions

### Immediate Actions
1. **Optimize Rainbow Timer Frequency**
   - Increase interval from 1000ms to 2000ms or higher.
   - Run only when window is focused.

2. **Improve Animation Efficiency**
   - Implement sprite frame caching.
   - Reduce animation frequency when unfocused.
   - Add option to disable animations.

3. **Conditional UI Updates**
   - Only apply skin changes when settings change.
   - Add dirty checking to reduce redraws.

### Code-level Optimizations
1. Update the rainbow timer mechanism to be less resource intensive.
2. Implement frame caching for sprite animations.
3. Add performance controls to disable intensive features.

## Implementation Plan

### Phase 1: Immediate Fixes
- Optimize `_update_rainbow` frequency.
- Implement frame caching for sprite animations.

### Phase 2: Feature Improvements
- Add user controls to disable intensive features.
- Conditional rendering based on window focus.

### Phase 3: Long-term Enhancements
- Add performance monitoring.
- Consider separating UI testing code from main application.

## Expected Behavior vs Actual Behavior
- Expected: Idle CPU usage under 5%, active timer CPU under 10%.
- Observed: High CPU usage during normal operation, especially with animations.

## Success Metrics
- Idle CPU usage under 5%.
- Active timer CPU usage under 10%.
- Notification animation CPU usage under 15%.
- Consistent performance across display scales.

## Timeline
- Phase 1 (Days 1-2): Baseline measurements and profiling.
- Phase 2 (Days 3-4): Implement immediate fixes.
- Phase 3 (Days 5-7): Test improvements and optimize further.

## Risk Mitigation
- Test changes in a separate branch.
- Maintain backward compatibility.
- Keep performance improvements optional if needed.
- Verify accessibility features remain intact.

## Priority
Medium-High. Performance degradation affects user experience but app remains functional.
