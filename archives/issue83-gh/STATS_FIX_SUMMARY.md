# Fix for Statistics Not Populating Issue

## Problem
The Statistics window was not showing any entries despite completing timer sessions.

## Root Cause
The duplicate removal logic in `_log_timer_completion` method was flawed:
- Used dictionary comprehension that didn't preserve order properly
- Could potentially lose entries during the deduplication process

## Solution
Replaced the problematic deduplication approach with a more reliable one:

```python
# Old approach (problematic)
unique_logs = {log['timestamp']: log for log in reversed(logs)}
logs = list(unique_logs.values())

# New approach (fixed)
seen_timestamps = set()
unique_logs = []
for log in logs:
    timestamp = log.get('timestamp')
    if timestamp not in seen_timestamps:
        seen_timestamps.add(timestamp)
        unique_logs.append(log)

unique_logs.append(log_entry)
```

## Result
- Timer sessions now properly log to the statistics file
- Statistics window correctly displays completed timer sessions
- Data integrity maintained with proper duplicate handling