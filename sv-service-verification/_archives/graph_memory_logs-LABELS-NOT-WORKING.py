# Author: Chatgpt
# Date of creation: 2025-10-31
# Description: This script reads a CSV file containing memory usage logs and plots the data

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Load CSV (Time, AM/PM, RSS_MB)

df = pd.read_csv('mem_log.csv', names=['Time', 'AMPM', 'RSS_MB'])

# Combine Time + AMPM as string

df['FullTimeStr'] = df['Time'] + ' ' + df['AMPM']

# Ensure RSS_MB is numeric

df['RSS_MB'] = pd.to_numeric(df['RSS_MB'], errors='coerce')
df = df.dropna(subset=['RSS_MB'])

# Create a numeric x-axis for plotting (0,1,2,...)

df['Index'] = range(len(df))

plt.figure(figsize=(24,8))
plt.subplots_adjust(bottom=0.25)

# Plot all memory usage points

plt.plot(df['Index'], df['RSS_MB'], label='Memory Usage (MB)')

plt.xlabel('Time (EST)')
plt.ylabel('Memory (MB)')
plt.title('Process Memory Usage Over Time')
plt.legend()
plt.grid(True)
plt.tight_layout()

# Label every 60th second using the original time strings

xticks = df['Index'][::60]
xtick_labels = df['FullTimeStr'][::60]

plt.xticks(xticks, xtick_labels, rotation=90, fontsize=8)

# Save PNG with timestamp

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f'memory_usage_{timestamp}.png'
plt.savefig(filename, dpi=150)
print(f'Plot saved as {filename}')

plt.show()
