import unittest
import subprocess
import time
import os
from dogtail.tree import *

class TestUIDogtail(unittest.TestCase):
    def setUp(self):
        """Set up the test environment by launching the application."""
        # Command to launch the application
        # We assume the main script is in 'bin/teatime.py'
        app_command = ["python3", "bin/teatime.py"]
        
        # Start the application as a subprocess
        self.app_process = subprocess.Popen(app_command)
        
        # Wait for the application to open and be ready
        # This is a simple delay, a more robust solution might be needed
        time.sleep(5)

    def tearDown(self):
        """Tear down the test environment by closing the application."""
        # Terminate the application process
        self.app_process.terminate()
        self.app_process.wait()

    def test_main_window_is_present(self):
        """Test if the main application window is present."""
        # The name 'Teatime' is a guess based on the project name.
        # We might need to adjust this based on the actual window title
        # or accessibility name.
        app_node = root.application('Teatime')
        self.assertIsNotNone(app_node, "Application window not found.")
        
        # Example of finding a button in the window
        # button = app_node.child(roleName='push button', name='Start')
        # self.assertIsNotNone(button, "Start button not found.")

if __name__ == "__main__":
    # It's recommended to run Dogtail tests with `dbus-run-session`
    # Example: dbus-run-session -- python3 tests/test_ui_dogtail.py
    unittest.main()
