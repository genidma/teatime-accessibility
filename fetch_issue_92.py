import requests
import json
import sys

def fetch_issue(number):
    url = f"https://api.github.com/repos/genidma/teatime-accessibility/issues/{number}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_comments(number):
    url = f"https://api.github.com/repos/genidma/teatime-accessibility/issues/{number}/comments"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return []

if __name__ == "__main__":
    issue = fetch_issue(92)
    comments = fetch_comments(92)
    
    with open("issue_92_details.txt", "w", encoding="utf-8") as f:
        if issue:
            f.write(f"Title: {issue.get('title')}\n")
            f.write(f"Body:\n{issue.get('body')}\n")
            f.write("\nComments:\n")
            for comment in comments:
                f.write(f"--- Comment by {comment['user']['login']} ---\n")
                f.write(f"{comment['body']}\n\n")
        else:
            f.write("Issue not found.")
