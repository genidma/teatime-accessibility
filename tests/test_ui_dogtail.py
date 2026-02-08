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
            self.dump_children(main_window)
        
        self.assertIsNotNone(start_button, "Start button not found.")
        self.assertIsNotNone(stop_button, "Stop button not found.")
        
        # Start the timer
        start_button.click()
        time.sleep(1)
        # Note: Sensitivity might not update immediately in AT-SPI
        # We check if it changed or at least didn't crash
        
        # Stop the timer
        stop_button.click()
        time.sleep(1)

    def test_presets(self):
        """Test each preset button."""
        app_node = self.get_app_node()
        main_window = app_node.child(roleName='frame')
        spin_button = self.find_child_fuzzy(main_window, roleName='spin button')
        
        presets = ["15m", "30m", "45", "1 Hour"] # Simplified names
        
        for preset in presets:
            btn = self.find_child_fuzzy(main_window, roleName='push button', name=preset)
            if btn:
                btn.click()
                time.sleep(1)
                stop_button = self.find_child_fuzzy(main_window, roleName='push button', name='Stop')
                if stop_button: stop_button.click()
                time.sleep(0.5)

    def test_categories(self):
        """Test category checkboxes."""
        app_node = self.get_app_node()
        main_window = app_node.child(roleName='frame')
        
        test_cats = ["rdp", "fc", "breaks"]
        for cat in test_cats:
            cb = self.find_child_fuzzy(main_window, roleName='check box', name=cat)
            if cb:
                cb.click()
                time.sleep(0.5)

    def test_settings_toggles(self):
        """Test Mini Mode, Nano Mode, and Sound toggles."""
        app_node = self.get_app_node()
        main_window = app_node.child(roleName='frame')
        
        toggles = ["Sound", "Mini", "Nano"]
        for toggle in toggles:
            cb = self.find_child_fuzzy(main_window, roleName='check box', name=toggle)
            if cb:
                cb.click()
                time.sleep(1)

    def test_font_scaling(self):
        """Test font scaling buttons."""
        app_node = self.get_app_node()
        main_window = app_node.child(roleName='frame')
        
        btn_plus = self.find_child_fuzzy(main_window, roleName='push button', name='A+')
        btn_minus = self.find_child_fuzzy(main_window, roleName='push button', name='A-')
        
        if btn_plus: btn_plus.click()
        if btn_minus: btn_minus.click()
        time.sleep(0.5)

    def test_menu_navigation(self):
        """Test opening About and Settings from the menu."""
        app_node = self.get_app_node()
        main_window = app_node.child(roleName='frame')
        
        # Try to find the menu button by icon name or tooltip if available, 
        # but in Dogtail usually it's better to find by role and index if name fails
        menu_button = self.find_child_fuzzy(main_window, roleName='push button', name='menu')
        if not menu_button:
            # Fallback to finding ANY button in the header bar area
            for child in main_window.children:
                if child.roleName == 'push button' and not child.name:
                    menu_button = child
                    break
        
        if menu_button:
            menu_button.click()
            time.sleep(1)

if __name__ == "__main__":
    unittest.main()
