# TeaTime Feature Suggestions

Based on analysis of the codebase, here are potential features for the electron-main-dev branch:

## 1. Data Export/Import (CSV/JSON)

- **Description**: Allow users to export their session history for external analysis and import functionality to restore from backups or migrate from other apps.
- **Implementation**: Add UI in Profile or Settings tab; backend logic in `src/lib/database.ts` to handle serialization/deserialization.

## 2. Desktop Notifications

- **Description**: System notifications when timer completes or for break reminders using Electron's native notification API.
- **Implementation**: Implement in `main.js` with IPC handlers; add notification preferences in settings.

## 3. Custom Timer Sounds

- **Description**: Allow users to upload or select custom alert sounds for timer start/end.
- **Implementation**: Store sound files in user data directory; add sound selection UI in timer settings; modify timer completion logic to play custom sounds.

## 4. Dark Mode Toggle

- **Description**: Add a theme preference that switches between light/dark modes.
- **Implementation**: Update Tailwind CSS configuration; add theme state management; store preference in localStorage or user preferences.

## 5. Goal Setting & Tracking

- **Description**: Daily/weekly session duration goals with visual progress indicators.
- **Implementation**: Add goal UI to Stats or Trends tabs; store goals in database; track completion and display progress.

## 6. System-Wide Shortcuts

- **Description**: Global hotkeys to start/stop timer even when app is minimized.
- **Implementation**: Register global shortcuts in main process; make configurable with custom key bindings in settings.

## 7. Auto-Start with OS

- **Description**: Option to launch TeaTime automatically on system login.
- **Implementation**: Use Electron's auto-launch API; add preference toggle in settings.

## 8. Advanced Session Notes

- **Description**: Allow rich text or longer notes with attachments (images, links).
- **Implementation**: Integrate simple markdown editor; store notes as text or file references in database.

## 9. Sync Across Devices
see issue 
## 10. Pomodoro Mode

- **Description**: Structured work/break intervals (e.g., 25m work, 5m break) with visual indicator of current interval type.
- **Implementation**: Extend existing timer with mode toggle; add interval management logic.

---

*Generated on: 2026-04-13T17:34:58-04:00*
