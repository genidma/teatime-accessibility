<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# TeaTime Accessibility

> "Discipline equals freedom"

A productivity app that helps you build daily discipline through structured breaks between deep work sessions.

## Quick Start

**Prerequisites:** Node.js

```bash
# Clone the repo
git clone https://github.com/genidma/teatime-accessibility.git
cd teatime-accessibility

# Install dependencies
npm install

# Run in development
npm run dev
```

Open http://localhost:3000 in your browser.

---

## How to Use

### 1. Start a Session
- Select a category (Meditation, Gratitude, Deep Work)
- Use the **circular dial** to set duration (drag around the ring)
- Or tap **1-5** for quick 1-5 minute sessions
- Click **START**

### 2. Timer Completes
- When timer hits 0:00, session is automatically saved
- Check the **Sessions** tab to see your history
- Check the **Stats** tab for analytics

### 3. Track Your Progress
- View session history with date grouping
- See total time, streaks, and daily goals
- Monitor your rhythm and flow

---

## App Navigation

| Tab | Description |
|-----|-------------|
| Sessions | Your Steeps - session history |
| Timer | Active Steep Timer with circular dial |
| Stats | Statistics & Analytics |
| Profile | User settings & preferences |

---

## Development Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Run in development mode |
| `npm run build` | Build for production |
| `npm run test` | Run automated tests |
| `npm run test:ui` | Run tests with UI |

---

## Running Tests

```bash
npm run test
```

This runs Playwright tests:
- ✓ App loads correctly
- ✓ Timer displays properly
- ✓ Category selection works
- ✓ Quick time buttons work
- ✓ All navigation tabs work

---

## Building for Distribution

### Linux (AppImage)
```bash
npm run build
npx electron-builder --linux
```

Output: `release/TeaTime-1.0.0.AppImage`

### Windows (unpacked)
```bash
npm run build
npx electron-builder --win --dir
```

Output: `release/win-unpacked/TeaTime.exe`

### macOS
```bash
npm run build
npx electron-builder --mac
```

---

## SQLite Database

Sessions are stored locally in SQLite:

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/TeaTime/teatime-sessions.db` |
| Windows | `%APPDATA%/TeaTime/teatime-sessions.db` |
| Linux | `~/.config/TeaTime/teatime-sessions.db` |

Data also backs up to browser localStorage.

---

## Features

- **Circular Dial Timer** - Drag to set any duration 1-60 min
- **Quick Select** - Tap 1-5 for instant short sessions
- **Categories** - Meditation, Gratitude, Deep Work + custom
- **Session History** - Track your daily resume
- **Statistics** - Analytics with daily rhythm charts
- **SQLite Persistence** - Data saved to disk

---

## Tech Stack

- React 19 + Vite
- Electron
- TailwindCSS 4
- Motion (animations)
- sql.js (SQLite in WebAssembly)
- Playwright (testing)

---

## Troubleshooting

**"vite not found" error?**
```bash
npm install
```

**Want to test timer is saving?**
1. Open DevTools (F12) → Console tab
2. Run a 1-minute timer
3. Look for "saveSession called" in console
4. Check Sessions tab for new entry
