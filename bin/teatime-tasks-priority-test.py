#!/usr/bin/env python3
"""
Original idea provided by: Chatgpt

Authors: Chatgpt, Lingma & Gemini.
- Original implementation kept crashing main machine because of Chrome OS instabilities and lack of compatibility in GPU enabled mode with my OS (Operating Syste)
- Heavy supports for Debugging from Microsoft's Github Copilot.
- Prompts provided by @genidma at Github throughout this cycle

---
Purpose of this script:
This script is designed to categorize the GitHub issues inside of a repository and then recommend a prioritized task list based on issue type, priority, and complexity. Right now, this script is inside of teatime-accessibility repository (repo) on Github.

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
import subprocess
# Register Firefox as the browser to use
firefox_path = '/usr/bin/firefox'  # Adjust if your Firefox executable is in a different location
if os.path.exists(firefox_path):
    webbrowser.register('firefox', None, webbrowser.BackgroundBrowser(firefox_path))

    
class IssueCategorizer:
    """
    Class to categorize GitHub issues for the TeaTime Accessibility project.
    """
    def __init__(self, repo_owner="genidma", repo_name="teatime-accessibility"):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = os.getenv('GITHUB_TOKEN')  # Optional, for authenticated requests
        self.issues = []

    def fetch_open_issues(self):
        """
        Fetch all open issues from the GitHub repository.
        """
        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }

        # Add authentication if token is available
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'

        url = f'https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/issues'
        params = {
            'state': 'open',
            'per_page': 100  # Get up to 100 issues
        }

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            # Filter out pull requests (they have 'pull_request' key)
            self.issues = [issue for issue in response.json() if 'pull_request' not in issue]
            print(f"Found {len(self.issues)} open issues")
            return self.issues
        else:
            print(f"Error fetching issues: {response.status_code}")
            print(response.text)
            return []


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
                # Debug: record environment and quick trace to disk
                print(f"DEBUG: OPEN_GANTT={open_env!r}, BROWSER_NAME={browser_override!r}, ALLOW_NO_SANDBOX={os.getenv('ALLOW_NO_SANDBOX')!r}")
                try:
                    with open('/tmp/tt-gantt-debug.log', 'ab') as df:
                        df.write((f"[{datetime.now().isoformat()}] Auto-open envs: OPEN_GANTT={open_env}, BROWSER_NAME={browser_override}, ALLOW_NO_SANDBOX={os.getenv('ALLOW_NO_SANDBOX')}\n").encode())
                except Exception:
                    pass
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
                            which_results = {}
                            for name in possible_bins:
                                path = shutil.which(name)
                                which_results[name] = path
                                if path and exe is None:
                                    exe = path
                            print(f"shutil.which results: {which_results}")
                            try:
                                with open('/tmp/tt-gantt-debug.log', 'ab') as df:
                                    df.write((f"[{datetime.now().isoformat()}] which_results={which_results}\n").encode())
                            except Exception:
                                pass

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
                                    '--disable-dev-shm-usage',
                                    # --disable-setuid-sandbox removed: it triggers "unsupported" warnings under
                                    # snap and may reduce stability; keep --no-sandbox only when explicitly allowed.
                                    # --no-sandbox is potentially problematic; include only if explicitly allowed
                                ]
                                if allow_no_sandbox:
                                    cmd.append('--no-sandbox')
                                # Create a dedicated directory in /tmp with proper permissions
                                tmp_dir = '/tmp/tt-gantt'
                                os.makedirs(tmp_dir, mode=0o755, exist_ok=True)
                                tmp_copy_path = os.path.join(tmp_dir, 'gantt-chart.html')
                                try:
                                    # Copy file and ensure the temp dir and file have reasonable permissions.
                                    shutil.copy2(file_path, tmp_copy_path)
                                    os.chmod(tmp_copy_path, 0o644)
                                    os.chmod(tmp_dir, 0o755)
                                    # Do NOT attempt to chmod '/tmp' (not permitted for unprivileged users).
                                    print(f"Copied gantt file to temporary path: {tmp_copy_path}")
                                    try:
                                        with open('/tmp/tt-gantt-debug.log', 'ab') as df:
                                            df.write((f"[{datetime.now().isoformat()}] Created {tmp_dir} and copied to {tmp_copy_path}\n").encode())
                                    except Exception:
                                        pass
                                except Exception as e:
                                    # If copy fails, fall back to original file path but log clearly.
                                    print(f"Failed to copy gantt file to {tmp_copy_path}: {e}")
                                    print("Attempting to open the original path directly (may fail under snap confinement).")
                                    try:
                                        with open('/tmp/tt-gantt-debug.log', 'ab') as df:
                                            df.write((f"[{datetime.now().isoformat()}] Copy failed: {e}\n").encode())
                                    except Exception:
                                        pass
                                    tmp_copy_path = file_path
                                # Use pathname2url to create a proper file:// URL without over-quoting
                                try:
                                    from urllib.request import pathname2url
                                    file_url = 'file://' + pathname2url(os.path.abspath(tmp_copy_path))
                                except Exception:
                                    # Fallback: basic quoting
                                    import urllib.parse
                                    file_url = 'file://' + urllib.parse.quote(os.path.abspath(tmp_copy_path))

                                # If the Chromium executable is a snap build, snap confinement may prevent
                                # file:// access. In that case start a tiny HTTP server serving the
                                # temp directory and open via http://127.0.0.1:PORT/gantt-chart.html
                                try:
                                    use_http_fallback = False
                                    if exe and '/snap/' in exe:
                                        use_http_fallback = True
                                    # Allow override via env var
                                    if os.getenv('OPEN_GANTT_SERVER', '').lower() in ('1', 'true', 'yes'):
                                        use_http_fallback = True

                                    if use_http_fallback:
                                        import socket
                                        # find a free port
                                        s = socket.socket()
                                        s.bind(('127.0.0.1', 0))
                                        port = s.getsockname()[1]
                                        s.close()
                                        server_cmd = [sys.executable, '-m', 'http.server', str(port)]
                                        try:
                                            with open(log_path, 'ab') as logf:
                                                logf.write((f"[{datetime.now().isoformat()}] Starting local HTTP server: {' '.join(server_cmd)} (cwd={tmp_dir})\n").encode())
                                                logf.flush()
                                            server_proc = subprocess.Popen(server_cmd, cwd=tmp_dir, stdout=logf, stderr=logf)
                                            # give server a moment to start
                                            time.sleep(0.2)
                                            http_url = f'http://127.0.0.1:{port}/gantt-chart.html'
                                            print(f"Started local HTTP server (PID: {server_proc.pid}) serving {tmp_dir} at {http_url}")
                                            try:
                                                with open('/tmp/tt-gantt-debug.log', 'ab') as df:
                                                    df.write((f"[{datetime.now().isoformat()}] Started HTTP server PID {server_proc.pid} port {port}\n").encode())
                                            except Exception:
                                                pass
                                            # Replace file_url with http_url so Chromium opens HTTP endpoint
                                            file_url = http_url
                                            # And set a short timeout for server liveness check later if needed
                                        except Exception as e:
                                            print(f"Failed to start local HTTP server fallback: {e}")
                                            try:
                                                with open('/tmp/tt-gantt-debug.log', 'ab') as df:
                                                    df.write((f"[{datetime.now().isoformat()}] HTTP server start failed: {e}\n").encode())
                                            except Exception:
                                                pass
                                except Exception:
                                    pass
                                cmd.extend([
                                    '--user-data-dir=/tmp/tt-gantt-userdata',
                                    '--no-first-run',
                                    '--no-default-browser-check',
                                    file_url
                                ])

                                # Prepare a log file to capture Chromium stdout/stderr for debugging
                                log_path = '/tmp/tt-gantt-chromium.log'
                                print(f"Launching Chromium with command: {' '.join(cmd)}")
                                print(f"Chromium stdout/stderr will be redirected to: {log_path}")
                                try:
                                    with open(log_path, 'ab') as logf:
                                        # write a marker so log is never empty if we reach here
                                        logf.write((f"[{datetime.now().isoformat()}] Launching cmd: {' '.join(cmd)}\n").encode())
                                        logf.flush()
                                        proc = subprocess.Popen(cmd, stdout=logf, stderr=logf)
                                        print(f"Chromium launched (PID: {proc.pid}).")
                                        try:
                                            with open('/tmp/tt-gantt-debug.log', 'ab') as df:
                                                df.write((f"[{datetime.now().isoformat()}] Launched PID {proc.pid}\n").encode())
                                        except Exception:
                                            pass
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
                                    try:
                                        with open('/tmp/tt-gantt-debug.log', 'ab') as df:
                                            df.write((f"[{datetime.now().isoformat()}] Launch failed: {e}\n").encode())
                                    except Exception:
                                        pass
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