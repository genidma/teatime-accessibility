import requests
import json
import sys

def fetch_discussion(number):
    # GitHub doesn't have a simple REST API for discussions in the same way as issues
    # But usually them can be accessed via GraphQL or sometimes they are listed as issues in some contexts (though not here)
    # Actually, I'll try to use read_url_content if I can't find a REST API.
    # Wait, the user said "discussion #38".
    url = f"https://github.com/genidma/teatime-accessibility/discussions/{number}"
    return url

if __name__ == "__main__":
    url = fetch_discussion(38)
    print(f"URL: {url}")
