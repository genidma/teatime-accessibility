# Author: Chatgpt
# Date of creation: 2025-10-31
# Description: This script reads a CSV file containing memory usage logs and plots the data

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load CSV (assumes columns: Time, PID, RSS_MB)

df = pd.read_csv('mem_log.csv', names=['Time', 'PID', 'RSS_MB'])

# Keep only rows where 'Time' looks like HH:MM:SS

df = df[df['Time'].str.match(r'^\d{2}:\d{2}:\d{2}$')]

# Convert Time column to pandas datetime

df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')

# Ensure RSS_MB is numeric, drop rows that are not

df['RSS_MB'] = pd.to_numeric(df['RSS_MB'], errors='coerce')
df = df.dropna(subset=['RSS_MB'])

plt.figure(figsize=(12,6))
plt.plot(df['Time'], df['RSS_MB'], label='Memory Usage (MB)')

plt.xlabel('Time')
plt.ylabel('Memory (MB)')
plt.title('Process Memory Usage Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.xticks(rotation=45)

# Create a timestamped filename to avoid overwriting

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'memory_usage_{timestamp}.png'
plt.savefig(filename, dpi=150)
print(f'Plot saved as {filename}')

# Show the plot on screen

plt.show()
