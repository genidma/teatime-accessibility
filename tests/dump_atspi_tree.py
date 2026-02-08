import sys
import time
import subprocess
from dogtail.tree import root

def dump_node(node, indent=0):
    try:
        print("  " * indent + f"[{node.roleName}] name='{node.name}'")
        for child in node.children:
            dump_node(child, indent + 1)
    except Exception as e:
        print("  " * Indent + f"Error reading node: {e}")

def main():
    # Launch app
    proc = subprocess.Popen(["./teatime-accessible.sh"])
    time.sleep(10)
    
    app_node = None
    for app in root.applications():
        if 'teatime' in app.name.lower():
            app_node = app
            break
            
    if app_node:
        print(f"Dumping tree for application: {app_node.name}")
        dump_node(app_node)
    else:
        print("Application not found.")
        print("Available applications:")
        for app in root.applications():
            print(f" - {app.name}")
            
    proc.terminate()

if __name__ == "__main__":
    main()
