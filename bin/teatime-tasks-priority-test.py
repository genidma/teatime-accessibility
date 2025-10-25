#!/usr/bin/env python3
"""
Author: Chatgpt, Lingma & Gemini. With prompts provided by @genidma at Github
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
            
            # Automatically open the Gantt chart in Firefox
            print("Opening Gantt chart in your web browser...")
            try:
                # Try to use Firefox if registered
                if 'firefox' in webbrowser._browsers:
                    webbrowser.get('firefox').open_new_tab('file://' + os.path.abspath(gantt_path))
                else:
                    # Fallback to default browser if Firefox registration failed
                    webbrowser.open_new_tab('file://' + os.path.abspath(gantt_path))
            except Exception as e:
                print(f"Could not open browser automatically: {e}")
                print("Please open the file manually in your browser")
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