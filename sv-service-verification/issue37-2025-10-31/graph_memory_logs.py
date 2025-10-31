# Author: Chatgpt
# Date of creation: 2025-10-31
# Description: This script reads a CSV file containing memory usage logs and plots the data

import pandas as pd
import matplotlib.pyplot as plt

# Load CSV (assumes columns: Time, PID, RSS_MB)
df = pd.read_csv('mem_log.csv', names=['Time', 'PID', 'RSS_MB'])

# Convert Time column to pandas datetime (today's date + time)
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')

plt.figure(figsize=(12,6))
plt.plot(df['Time'], df['RSS_MB'], label='Memory Usage (MB)')

plt.xlabel('Time')
plt.ylabel('Memory (MB)')
plt.title('Process Memory Usage Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)  # rotate X-axis labels for readability
plt.show()