# Author: Lingma
# Date of creation: 2025-10-31
# Description: This script reads a CSV file containing memory usage logs and plots the data

#!/usr/bin/env python3
"""
Script to plot memory usage over time from mem_log.csv
Time values will be on the x-axis and memory values on the y-axis.
"""

import sys

try:
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from datetime import datetime
except ImportError as e:
    print(f"Error importing required packages: {e}")
    print("Please install required packages with: pip install pandas matplotlib")
    sys.exit(1)

try:
    # Read the CSV file
    file_path = 'sv-service-verification/issue37-2025-10-31/mem_log.csv'

    # Read data with custom column names since the CSV has no header
    df = pd.read_csv(file_path, names=['time', 'period', 'memory'])
    print(f"Successfully loaded {len(df)} data points")
    
    # Filter out rows that don't match the expected time format
    # The last row contains "Average:" which is not a valid time
    df = df[df['time'] != 'Average:']
    print(f"Filtered to {len(df)} valid data points")

    # Convert to datetime objects (assuming today's date for plotting purposes)
    # We need to add a date to the time strings to create proper datetime objects
    today = datetime.now().date()
    df['datetime'] = pd.to_datetime(today.strftime('%Y-%m-%d') + ' ' + df['time'] + ' ' + df['period'], 
                                   format='%Y-%m-%d %I:%M:%S %p')

    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(df['datetime'], df['memory'], linewidth=1)
    plt.xlabel('Time')
    plt.ylabel('Memory Usage (MB)')
    plt.title('Memory Usage Over Time')
    plt.grid(True, alpha=0.3)

    # Format x-axis to show time nicely
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
    plt.xticks(rotation=45)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save the plot
    plt.savefig('memory_usage_plot.png', dpi=300, bbox_inches='tight')
    print("Plot saved as 'memory_usage_plot.png'")

    # Display the plot
    plt.show()

except FileNotFoundError:
    print(f"Error: Could not find the file {file_path}")
    sys.exit(1)
except Exception as e:
    print(f"Error while processing data or creating plot: {e}")
    sys.exit(1)