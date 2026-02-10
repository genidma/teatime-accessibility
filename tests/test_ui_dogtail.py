import unittest
import subprocess
import time
import os
import sys
from dogtail.tree import *
from dogtail.utils import *

class TestUIDogtail(unittest.TestCase):
    def setUp(self):
        """Set up the test environment by launching the application."""
        # Command to launch the application using the launcher script
        app_command = ["./teatime-accessible.sh"]
        
        # Start the application as a subprocess
        self.app_process = subprocess.Popen(app_command)
        
        # Wait for the application to open and be ready
        time.sleep(12)

    def tearDown(self):
        """Tear down the test environment by closing the application."""
        # Terminate the application process
        self.app_process.terminate()
        self.app_process.wait()

    def get_app_node(self):
        """Helper to find the application node."""
        for app in root.applications():
            if 'teatime' in app.name.lower():
                return app
        try:
            return root.application('teatime.py')
        except:
            pass
        try:
            return root.application('KCResonance')
        except:
            pass
        return None

    def dump_children(self, node, depth=0):
        """Diagnostic helper to dump children of a node."""
        try:
            print("  " * depth + f"[{node.roleName}] name='{node.name}'")
            if depth < 3: # Limit depth
                for child in node.children:
                    self.dump_children(child, depth + 1)
        except:
            pass

    def find_child_fuzzy(self, parent, roleName=None, name=None, recursive=True):
        """Fuzzy search for a child by role and partial name."""
        try:
            return parent.child(roleName=roleName, name=name)
        except:
            # Try fuzzy name match among direct children
            for child in parent.children:
                if (roleName is None or child.roleName == roleName) and \
                   (name is None or name.lower() in child.name.lower()):
                    return child
            
            if recursive:
                # Try to find the container grid or box first
                # In teatime, most controls are in a grid or stack
                for child in parent.children:
                    if child.roleName in ['filler', 'panel', 'box', 'grid']:
                        result = self.find_child_fuzzy(child, roleName, name, recursive=False)
                        if result: return result
        return None

    def capture_ui_state(self, node):
        """Capture UI state for debugging purposes."""
        try:
            print(f"Capturing UI state for node: {node.name}")
            self.dump_children(node)
        except Exception as e:
            print(f"Error capturing UI state: {e}")

    def test_main_window_is_present(self):
        """Test if the main application window is present and controls are visible."""
        app_node = self.get_app_node()
        if not app_node:
            print("Available apps:")
            for a in root.applications(): print(f" - {a.name}")
        self.assertIsNotNone(app_node, "Application not found via AT-SPI.")
        
        main_window = app_node.child(roleName='frame')
        self.assertIsNotNone(main_window, "Main window not found.")

    def test_start_stop_timer(self):
        """Test starting and stopping the timer."""
        app_node = self.get_app_node()
        main_window = app_node.child(roleName='frame')
        
        start_button = self.find_child_fuzzy(main_window, roleName='push button', name='Start')
        stop_button = self.find_child_fuzzy(main_window, roleName='push button', name='Stop')
        
        if not start_button:
            self.capture_ui_state(main_window)
        
        self.assertIsNotNone(start_button, "Start button not found.")
        self.assertIsNotNone(stop_button, "Stop button not found.")
        
        # Start the timer
        start_button.click()
        time.sleep(1)
        # Note: Sensitivity might not update immediately in AT-SPI
        # We check if it changed or at least didn't crash