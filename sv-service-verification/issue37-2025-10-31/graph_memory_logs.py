# Author: Chatgpt
# Date of creation: 2025-10-31
# Description: This script reads a CSV file containing memory usage logs and plots the data

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Load CSV (Time, AM/PM, RSS_MB)

df = pd.read_csv('mem_log.csv', names=['Time', 'AMPM', 'RSS_MB'])

# Combine Time + AMPM into one string

df['FullTime'] = df['Time'] + ' ' + df['AMPM']

# Keep only rows where FullTime is valid

df = df[df['FullTime'].str.match(r'^\d{2}:\d{2}:\d{2} [AP]M$')]

# Convert to datetime (arbitrary date, just for timedelta calculation)

df['FullTime'] = pd.to_datetime(df['FullTime'], format='%I:%M:%S %p')

# Compute elapsed time in seconds from the first timestamp

start_time = df['FullTime'].iloc[0]
df['Elapsed'] = (df['FullTime'] - start_time).dt.total_seconds()

# Ensure RSS_MB is numeric

df['RSS_MB'] = pd.to_numeric(df['RSS_MB'], errors='coerce')
df = df.dropna(subset=['RSS_MB'])

plt.figure(figsize=(24,8))
plt.subplots_adjust(bottom=0.25)

# Plot all memory usage points

plt.plot(df['Elapsed'], df['RSS_MB'], label='Memory Usage (MB)')

plt.xlabel('Elapsed Time (seconds)')
plt.ylabel('Memory (MB)')
plt.title('Process Memory Usage Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()


# Create a formatted label for every 60 seconds
xticks = df['Elapsed'][::60]  # every 60th second
xtick_labels = [(start_time + pd.to_timedelta(s, unit='s')).strftime('%I:%M:%S %p') for s in xticks]

# Label every 60th second (adjust font size)
plt.xticks(xticks, xtick_labels, rotation=90, fontsize=8)

# Timestamped filename

from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'memory_usage_{timestamp}.png'
plt.savefig(filename, dpi=150)
print(f'Plot saved as {filename}')

plt.show()
