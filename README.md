<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# TeaTime Accessibility - Electron Main Dev Branch

This is the **electron-main-dev** branch - a complete Electron app overhaul with React, Vite, and SQLite for session persistence.

## Run Locally

**Prerequisites:** Node.js

```bash
npm install
npm run dev
```

To run as Electron app:
```bash
npm run electron-dev
```

Access at: http://localhost:3000

---

## Circular Dial Timer

The timer features an interactive **circular dial** for setting session duration:

- **Drag to set**: Click and drag around the dial to set any duration (1-60 minutes)
- **Quick select**: Tap numbers 1-5 for instant short sessions (1-5 minutes)
- **Visual feedback**: Progress ring shows selected duration

---

## SQLite Database Integration

This branch uses **sql.js** (SQLite compiled to WebAssembly) with file-based persistence via Electron IPC.

### How It Works

1. **Database Initialization** (`src/lib/database.ts`)
   - Uses `sql.js` loaded from CDN (`https://sql.js.org/dist/`)
   - Creates SQLite database
   - Schema: `sessions` table

2. **File Persistence** (Electron only)
   - Database file saved to user's data directory: `~/Library/Application Support/TeaTime/teatime-sessions.db` (macOS) or `%APPDATA%/TeaTime/teatime-sessions.db` (Windows)
   - Uses Electron IPC to read/write file
   - Falls back to localStorage if not running in Electron

3. **Session Auto-Save**
   - When timer completes, session is saved to both file and localStorage

### Database File Location

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/TeaTime/teatime-sessions.db` |
| Windows | `%APPDATA%/TeaTime/teatime-sessions.db` |
| Linux | `~/.config/TeaTime/teatime-sessions.db` |

### Database Schema

```sql
CREATE TABLE sessions (
  id TEXT PRIMARY KEY,
  categoryId TEXT NOT NULL,
  title TEXT NOT NULL,
  date TEXT NOT NULL,
  time TEXT NOT NULL,
  duration INTEGER NOT NULL,
  notes TEXT,
  createdAt TEXT DEFAULT CURRENT_TIMESTAMP
)
```

### Key Functions

| Function | Description |
|----------|-------------|
| `initDatabase()` | Initialize SQLite, load from file or localStorage |
| `saveSession(session)` | Save completed session to database |
| `getAllSessions()` | Retrieve all sessions |
| `getTodaySessions()` | Get today's sessions |
| `getSessionsByDate(date)` | Get sessions for specific date |

---

## App Navigation

The app has 5 main views:

1. **Sessions** - Your Steeps (session history)
2. **Timer** - Active Steep Timer (with circular dial)
3. **Stats** - Statistics & Analytics
4. **Trends** - (Coming soon)
5. **Profile** - User settings & preferences

---

## Building for Production

```bash
npm run build
```

Output will be in the `dist/` folder.

---

## Tech Stack

- **React 19** - UI Framework
- **Vite** - Build tool
- **Electron** - Desktop app shell
- **TailwindCSS 4** - Styling
- **Motion** - Animations
- **Lucide React** - Icons
- **sql.js** - SQLite in WebAssembly

---

## Philosophy

> "Discipline equals freedom"

TeaTime helps you build daily discipline through structured breaks between deep work sessions.
