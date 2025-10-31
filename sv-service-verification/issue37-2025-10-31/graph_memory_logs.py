# Author: Chatgpt
# Date of creation: 2025-10-31
# Description: This script reads a CSV file containing memory usage logs and plots the data

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load CSV (Time, AM/PM, RSS_MB)

df = pd.read_csv('mem_log.csv', names=['Time', 'AMPM', 'RSS_MB'])

# Combine Time + AMPM into one string, e.g., "04:48:00 PM"

df['FullTime'] = df['Time'] + ' ' + df['AMPM']

# Keep only rows where 'FullTime' looks valid (HH:MM:SS AM/PM)

df = df[df['FullTime'].str.match(r'^\d{2}:\d{2}:\d{2} [AP]M$')]

# Convert to datetime

df['FullTime'] = pd.to_datetime(df['FullTime'], format='%I:%M:%S %p')

# Ensure RSS_MB is numeric

df['RSS_MB'] = pd.to_numeric(df['RSS_MB'], errors='coerce')
df = df.dropna(subset=['RSS_MB'])

plt.figure(figsize=(18,6))  # wider figure for more labels
plt.plot(df['FullTime'], df['RSS_MB'], label='Memory Usage (MB)')

plt.xlabel('Time (P<)')
plt.ylabel('Memory (MB)')
plt.title('Process Memory Usage Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show every 60th timestamp on x-axis for readability

plt.xticks(df['FullTime'][::60], rotation=90)

# Timestamped filename

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'memory_usage_{timestamp}.png'
plt.savefig(filename, dpi=150)
print(f'Plot saved as {filename}')

plt.show()