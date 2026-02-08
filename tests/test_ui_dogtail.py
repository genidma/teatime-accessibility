import unittest
import subprocess
import time
import os
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
        # Increased wait time to ensure the app is fully loaded
        time.sleep(8)

    def tearDown(self):
        """Tear down the test environment by closing the application."""
        # Terminate the application process
        self.app_process.terminate()
        self.app_process.wait()

    def test_main_window_is_present(self):
        """Test if the main application window is present and controls are visible."""
        # The app name from AT-SPI listing is 'teatime.py'
        # Using a more robust search by checking all applications if needed
        app_node = None
        for app in root.applications():
            if 'teatime' in app.name.lower():
                app_node = app
                break
        
        if app_node is None:
            # Fallback to direct name if search fails
            try:
                app_node = root.application('teatime.py')
            except:
                app_node = root.application('KCResonance')

        self.assertIsNotNone(app_node, "Application 'teatime.py' or variant not found.")
        
        # Verify the main window exists
        main_window = app_node.child(roleName='frame')
        self.assertIsNotNone(main_window, "Main window not found.")

        # Test finding buttons
        start_button = main_window.child(roleName='push button', name='Start')
        self.assertIsNotNone(start_button, "Start button not found.")
        
        stop_button = main_window.child(roleName='push button', name='Stop')
        self.assertIsNotNone(stop_button, "Stop button not found.")

    def test_start_stop_timer(self):
        """Test starting and stopping the timer."""
        # Re-find app node for this test
        app_node = None
        for app in root.applications():
            if 'teatime' in app.name.lower():
                app_node = app
                break
        
        if app_node is None:
            app_node = root.application('teatime.py')

        main_window = app_node.child(roleName='frame')
        
        start_button = main_window.child(roleName='push button', name='Start')
        stop_button = main_window.child(roleName='push button', name='Stop')
        
        # Start the timer
        start_button.click()
        time.sleep(1)
        
        # Verify Start is insensitive and Stop is sensitive
        self.assertFalse(start_button.sensitive, "Start button should be insensitive when timer is running.")
        self.assertTrue(stop_button.sensitive, "Stop button should be sensitive when timer is running.")
        
        # Stop the timer
        stop_button.click()
        time.sleep(1)
        
        # Verify Start is sensitive and Stop is insensitive
        self.assertTrue(start_button.sensitive, "Start button should be sensitive when timer is stopped.")
        self.assertFalse(stop_button.sensitive, "Stop button should be insensitive when timer is stopped.")

if __name__ == "__main__":
    # It's recommended to run Dogtail tests with `dbus-run-session`
    # Example: dbus-run-session -- python3 tests/test_ui_dogtail.py
    unittest.main()
