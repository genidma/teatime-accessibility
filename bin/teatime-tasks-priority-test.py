#!/usr/bin/env python3
"""
Author: Chatgpt, Lingma & Gemini. With supports for Debugging from Copilot. With prompts provided by @genidma at Github

Script to categorize GitHub issues and create corresponding tasks for TeaTime Accessibility project.

This script is designed to:
1. Fetch open issues from the GitHub repository
2. Categorize them by type, priority, and complexity
3. Generate task lists based on these categorizations
4. Create a Gantt chart visualization of planned tasks

The output will be saved to a file named 'teatime-tasks-output.txt' in the project root directory.
The Gantt chart will be saved as 'teatime-gantt-chart.html' in the project root directory.
"""

import requests
import json
import os
from collections import defaultdict
from datetime import datetime
import webbrowser
import time
import shutil
import sys
# Register Firefox as the browser to use
firefox_path = '/usr/bin/firefox'  # Adjust if your Firefox executable is in a different location
if os.path.exists(firefox_path):
    webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))

    
    def categorize_issues(self):
        """
        Categorize issues by type, priority, and complexity.
        """
        categories = {
            'bug': [],
            'feature': [],
            'enhancement': [],
            'documentation': [],
            'other': []
        }
        
        priorities = {
            'high': [],
            'medium': [],
            'low': []
        }
        
        complexity = {
            'simple': [],
            'medium': [],
            'complex': []
        }
        
        # Categorize by type
        for issue in self.issues:
            labels = [label['name'].lower() for label in issue.get('labels', [])]
            title = issue.get('title', '').lower()
            body = issue.get('body', '').lower() if issue.get('body') else ''
            
            # Determine issue type
            if 'bug' in labels or 'bug' in title or 'error' in body or 'crash' in body:
                categories['bug'].append(issue)
            elif 'feature' in labels or 'feature' in title or 'add' in title:
                categories['feature'].append(issue)
            elif 'enhancement' in labels or 'enhancement' in title or 'improve' in title:
                categories['enhancement'].append(issue)
            elif 'documentation' in labels or 'documentation' in title or 'docs' in title:
                categories['documentation'].append(issue)
            else:
                categories['other'].append(issue)
                
            # Determine priority based on labels or keywords
            if 'high priority' in labels or 'critical' in labels or 'urgent' in labels:
                priorities['high'].append(issue)
            elif 'low priority' in labels:
                priorities['low'].append(issue)
            else:
                priorities['medium'].append(issue)
                
            # Determine complexity (this is a rough estimation)
            if 'simple' in labels or len(body) < 200:
                complexity['simple'].append(issue)
            elif 'complex' in labels or 'refactor' in title or 'rewrite' in title:
                complexity['complex'].append(issue)
            else:
                complexity['medium'].append(issue)
                
        return {
            'by_type': categories,
            'by_priority': priorities,
            'by_complexity': complexity
        }
    
    def create_task_list(self, categorized_issues):
        """
        Create task lists based on issue categorization.
        """
        output = []
        output.append("=== TASK LIST BY CATEGORY ===")
        
        # By type
        output.append("\n1. BY TYPE:")
        for category, issues in categorized_issues['by_type'].items():
            if issues:
                output.append(f"\n  {category.upper()} ({len(issues)} issues):")
                for issue in issues:
                    output.append(f"    - [{issue['number']}] {issue['title']}")
                    
        # By priority
        output.append("\n\n2. BY PRIORITY:")
        for priority, issues in categorized_issues['by_priority'].items():
            if issues:
                output.append(f"\n  {priority.upper()} ({len(issues)} issues):")
                for issue in issues:
                    output.append(f"    - [{issue['number']}] {issue['title']}")
                    
        # By complexity
        output.append("\n\n3. BY COMPLEXITY:")
        for level, issues in categorized_issues['by_complexity'].items():
            if issues:
                output.append(f"\n  {level.upper()} ({len(issues)} issues):")
                for issue in issues:
                    output.append(f"    - [{issue['number']}] {issue['title']}")
                    
        return "\n".join(output)
    
    def generate_priority_tasks(self, categorized_issues):
        """
        Generate a prioritized task list.
        High priority, simple tasks should be done first.
        """
        output = []
        output.append("\n\n=== RECOMMENDED TASK ORDER ===")
        
        # Get high priority, simple tasks first
        high_priority = set(issue['number'] for issue in categorized_issues['by_priority']['high'])
        simple_tasks = set(issue['number'] for issue in categorized_issues['by_complexity']['simple'])
        
        # Find intersection
        high_simple = high_priority.intersection(simple_tasks)
        
        # Get the actual issues
        urgent_tasks = [issue for issue in self.issues if issue['number'] in high_simple]
        
        if urgent_tasks:
            output.append("\n1. URGENT & SIMPLE TASKS (Do these first):")
            for issue in urgent_tasks:
                output.append(f"   - [{issue['number']}] {issue['title']}")
        else:
            output.append("\n1. URGENT & SIMPLE TASKS (Do these first):")
            output.append("   - None found")
            
        # Medium priority, simple tasks
        medium_priority = set(issue['number'] for issue in categorized_issues['by_priority']['medium'])
        medium_simple = medium_priority.intersection(simple_tasks)
        medium_simple_tasks = [issue for issue in self.issues if issue['number'] in medium_simple]
        
        if medium_simple_tasks:
            output.append("\n2. MEDIUM PRIORITY & SIMPLE TASKS:")
            for issue in medium_simple_tasks:
                output.append(f"   - [{issue['number']}] {issue['title']}")
        else:
            output.append("\n2. MEDIUM PRIORITY & SIMPLE TASKS:")
            output.append("   - None found")
            
        # Complex tasks
        complex_tasks = categorized_issues['by_complexity']['complex']
        if complex_tasks:
            output.append("\n3. COMPLEX TASKS (Plan carefully):")
            for issue in complex_tasks:
                output.append(f"   - [{issue['number']}] {issue['title']}")
        else:
            output.append("\n3. COMPLEX TASKS (Plan carefully):")
            output.append("   - None found")
            
        return "\n".join(output)

def create_gantt_chart():
    """
    Create a Gantt chart for sample tasks.
    """
    try:
        import pandas as pd
        import plotly.figure_factory as ff
        
        # Define tasks
        df = pd.DataFrame([
            {"Task":"Implement Nano Mode #65",   "Start":"2025-10-23 01:32","Finish":"2025-10-23 02:26","Step":"Step 1"},
            {"Task":"Test in main-dev and perform SV",   "Start":"2025-10-23 02:26","Finish":"2025-10-23 02:40","Step":"Step 2"},
            {"Task":"Update Readme for Nano mode",      "Start":"2025-10-23 02:40","Finish":"2025-10-23 02:45","Step":"Step 3"},
            {"Task":"Commit code to main-dev and sign off",      "Start":"2025-10-23 02:45","Finish":"2025-10-23 02:50","Step":"Step 4"},
            {"Task":"merge main-dev with main",         "Start":"2025-10-23 02:50","Finish":"2025-10-23 02:55","Step":"Step 5"},
            {"Task":"SV in main",      "Start":"2025-10-23 02:55","Finish":"2025-10-23 03:00","Step":"Step 6"}
        ])

        # Force Step column to be categorical with explicit order
        df['Step'] = pd.Categorical(df['Step'],
                                    categories=["Step 1","Step 2","Step 3","Step 4","Step 5", "Step 6"],
                                    ordered=True)

        # Create Gantt
        fig = ff.create_gantt(
            df,
            index_col='Step',       # colors bars by Step
            show_colorbar=True,     # right-hand legend
            group_tasks=True,
            title="Teatime Task Timeline - Testing Python script for Gantt Chart",
        )
        
        return fig
    except ImportError as e:
        print(f"Warning: Could not create Gantt chart. Missing required libraries: {e}")
        print("To install required libraries, run: pip install pandas plotly")
        return None

def main():
    """
    Main function to run the issue categorizer.
    """
    print("TeaTime Accessibility Issue Categorizer")
    print("======================================")
    
    # Use simple fixed filenames for testing
    output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "teatime-tasks-output.txt")
    gantt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "teatime-gantt-chart.html")
    
    # Print paths for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Output path: {output_path}")
    print(f"Gantt chart path: {gantt_path}")
    
    # Initialize categorizer
    categorizer = IssueCategorizer()
    
    # Try to fetch issues
    try:
        issues = categorizer.fetch_open_issues()
        if not issues:
            print("No open issues found or unable to fetch issues.")
            print("Make sure you have internet connection and the repository name is correct.")
            return
            
        # Categorize issues
        categorized = categorizer.categorize_issues()
        
        # Create task lists
        output_content = []
        output_content.append("TeaTime Accessibility Issue Categorizer")
        output_content.append("======================================")
        output_content.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_content.append(f"Total issues found: {len(issues)}")
        output_content.append("")
        
        task_list = categorizer.create_task_list(categorized)
        output_content.append(task_list)
        
        priority_tasks = categorizer.generate_priority_tasks(categorized)
        output_content.append(priority_tasks)
        
        # Write to file
        full_output = "\n".join(output_content)
        with open(output_path, 'w') as f:
            f.write(full_output)
            
        print(f"\nOutput has been saved to: {output_path}")
        print(f"You can view the file directly with: cat {output_path}")
        
        # Create and save Gantt chart
        print("\nGenerating Gantt chart...")
        fig = create_gantt_chart()
        if fig:
            fig.write_html(gantt_path)
            print(f"Gantt chart has been saved to: {gantt_path}")
            
            # Ensure file is completely written before opening
            time.sleep(1)
            
            # Automatically open the Gantt chart in a browser only if explicitly allowed.
            # This prevents unexpected browser launches that may destabilize the system.
            print("Gantt chart generated. Deciding whether to open it automatically...")

            # Debug: show which browser controllers are registered
            try:
                print("Registered browser controllers:", list(webbrowser._browsers.keys()))
            except Exception:
                # webbrowser internals may differ across Python builds; ignore failures here
                pass

            # Show what the default webbrowser.get() would return (best-effort)
            try:
                default_browser = webbrowser.get()
                print("Default browser controller:", default_browser)
            except Exception as e:
                print(f"Could not determine default browser controller: {e}")

            # Allow the user to explicitly control auto-opening to avoid crashes.
            # Set OPEN_GANTT=1 or OPEN_GANTT=true in environment to enable auto-open.
            open_env = os.getenv('OPEN_GANTT', '').lower()
            browser_override = os.getenv('BROWSER_NAME')  # e.g. 'firefox' or 'chromium'

            if open_env in ('1', 'true', 'yes'):
                print("Auto-open enabled via OPEN_GANTT.")
                try:
                    # Use filesystem path for subprocess invocations to avoid ERR_FILE_NOT_FOUND
                    file_path = os.path.abspath(gantt_path)
                    file_url = 'file://' + file_path

                    if not os.path.exists(file_path):
                        print(f"Gantt file not found at expected path: {file_path}")
                        print("Aborting auto-open.")
                        raise FileNotFoundError(file_path)

                    # If user explicitly asked for a browser, try to use it
                    if browser_override:
                        print(f"Attempting to open with overridden browser: {browser_override}")
                        # Special-case Chromium: launch with safer flags via subprocess
                        if browser_override.lower() in ('chromium', 'chromium-browser', 'chrome', 'google-chrome'):
                            # Find an executable on PATH
                            possible_bins = [browser_override]
                            # include common names to try if user passed a generic name
                            if browser_override.lower() == 'chrome':
                                possible_bins = ['google-chrome', 'chrome', 'chromium', 'chromium-browser']
                            if browser_override.lower() == 'chromium':
                                possible_bins = ['chromium', 'chromium-browser', 'google-chrome']

                            exe = None
                            for name in possible_bins:
                                path = shutil.which(name)
                                if path:
                                    exe = path
                                    break

                            if not exe:
                                print(f"Could not find Chromium/Chrome executable among: {possible_bins}. Falling back to webbrowser module.")
                                try:
                                    webbrowser.get().open_new_tab(file_url)
                                except Exception as e:
                                    print(f"Fallback open failed: {e}")
                            else:
                                # Construct the safe flags the user requested
                                allow_no_sandbox = os.getenv('ALLOW_NO_SANDBOX', '').lower() in ('1', 'true', 'yes')
                                cmd = [
                                    exe,
                                    '--disable-gpu',
                                    '--disable-software-rasterizer',
                                    # --no-sandbox is potentially problematic; include only if explicitly allowed
                                ]
                                if allow_no_sandbox:
                                    cmd.append('--no-sandbox')
                                cmd.extend([
                                    '--user-data-dir=/tmp/tt-gantt',
                                    file_path,
                                ])

                                # Prepare a log file to capture Chromium stdout/stderr for debugging
                                log_path = '/tmp/tt-gantt-chromium.log'
                                print(f"Launching Chromium with command: {' '.join(cmd)}")
                                print(f"Chromium stdout/stderr will be redirected to: {log_path}")
                                try:
                                    with open(log_path, 'ab') as logf:
                                        proc = subprocess.Popen(cmd, stdout=logf, stderr=logf)
                                        print(f"Chromium launched (PID: {proc.pid}).")
                                        # Wait briefly to detect immediate exit/crash
                                        try:
                                            proc.wait(timeout=2)
                                            print(f"Chromium process exited quickly with return code {proc.returncode}.")
                                            print(f"See {log_path} for stdout/stderr content.")
                                        except subprocess.TimeoutExpired:
                                            print("Chromium is still running (no immediate crash detected).")
                                            print(f"See {log_path} for ongoing stdout/stderr.")
                                except Exception as e:
                                    print(f"Failed to launch Chromium subprocess: {e}")
                        else:
                            try:
                                webbrowser.get(browser_override).open_new_tab(file_url)
                                print(f"Opened Gantt chart with: {browser_override}")
                            except Exception as e:
                                print(f"Failed to open with {browser_override}: {e}")
                                print("Falling back to system default browser...")
                                webbrowser.open_new_tab(file_url)
                    else:
                        # Prefer 'firefox' if it's registered and exists on disk
                        if shutil.which('firefox') and 'firefox' in webbrowser._browsers:
                            print("Using registered 'firefox' to open the file")
                            webbrowser.get('firefox').open_new_tab(file_url)
                        else:
                            print("Using system default browser to open the file")
                            webbrowser.open_new_tab(file_url)
                except Exception as e:
                    print(f"Could not open browser automatically: {e}")
                    print("Please open the file manually in your browser")
            else:
                print("Auto-open disabled (set OPEN_GANTT=1 to enable).")
                print(f"Gantt chart file is available at: {os.path.abspath(gantt_path)}")
                print("To open it safely in Chromium with mitigations, try:")
                print("  chromium --disable-gpu --disable-software-rasterizer --no-sandbox --user-data-dir=/tmp/tt-gantt 'file://" + os.path.abspath(gantt_path) + "'")
        else:
            print("Gantt chart could not be generated due to missing libraries.")
        
        # Also print to console
        print("\n" + full_output)
        
    except Exception as e:
        print(f"Error running the script: {e}")
        print("Please make sure you have the 'requests' library installed:")
        print("pip install requests")


if __name__ == "__main__":
    main()