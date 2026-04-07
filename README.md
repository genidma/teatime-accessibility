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

Access at: http://localhost:3000

---

## Circular Dial Timer

The timer features an interactive **circular dial** for setting session duration:

- **Drag to set**: Click and drag around the dial to set any duration (1-60 minutes)
- **Quick select**: Tap numbers 1-5 for instant short sessions (1-5 minutes)
- **Visual feedback**: Progress ring shows selected duration
- **Tactile feel**: Clean, minimal interface that feels responsive

### How It Works

1. **Circular Dial** - Drag around the ring to set duration
2. **Quick Time Buttons** - Tap 1-5 for instant 1-5 minute sessions
3. **Mode Selector** - Choose category (Meditation, Gratitude, Deep Work, or custom)

---

## SQLite Database Integration

This branch uses **sql.js** (SQLite compiled to WebAssembly) for in-browser database functionality.

### How It Works

1. **Database Initialization** (`src/lib/database.ts`)
   - Uses `sql.js` loaded from CDN (`https://sql.js.org/dist/`)
   - Creates an in-memory SQLite database
   - Schema: `sessions` table with columns: `id`, `categoryId`, `title`, `date`, `time`, `duration`, `notes`, `createdAt`

2. **Session Auto-Save**
   - When the timer completes (reaches 0:00), a session is automatically saved
   - The session captures: category, title, duration, date, and time
   - Saved via `saveSession()` function in `database.ts`

3. **Data Persistence**
   - Sessions are backed up to `localStorage` key: `teatime_sessions`
   - On app load, data is restored from localStorage to SQLite
   - This ensures data survives page refreshes

### Note on File Persistence

Currently, data is stored in-browser using:
- **SQLite (sql.js)**: In-memory database for queries
- **localStorage**: Backup storage for persistence across sessions

To write to a file on the user's home directory, Electron IPC would be required. This is a future enhancement.

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
| `initDatabase()` | Initialize SQLite, create schema, load from localStorage |
| `saveSession(session)` | Save a completed session to the database |
| `getAllSessions()` | Retrieve all sessions ordered by date |
| `getTodaySessions()` | Get only today's sessions |
| `getSessionsByDate(date)` | Get sessions for a specific date |

### File Structure

```
src/
├── lib/
│   └── database.ts       # SQLite operations
├── components/
│   ├── ActiveSteepTimer.tsx   # Timer with circular dial
│   ├── SessionHistoryList.tsx # Loads sessions from DB
│   ├── StatsView.tsx          # Displays session analytics
│   ├── ProfileView.tsx        # User settings
│   └── categories.tsx          # Centralized category definitions
└── App.tsx               # Main app with navigation
```

### Categories (Centralized)

All session categories are defined in `src/components/categories.tsx`:

- **Deep Work** (DW) - Blue (#0969da)
- **Meditation** (M) - Green (#2e7a5f)
- **Gratitude** (G) - Orange (#fd8a42)
- **Break** (BR) - Grey (#e4e8f0)
- **Exercise** (EX) - Red (#ffdad6)
- **Walk** (WK) - Grey (#dee3eb)

To add a new category, edit the `CATEGORY_STYLES` object in `categories.tsx`.

---

## App Navigation

The app has 5 main views accessible via the bottom navigation:

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
- **TailwindCSS 4** - Styling
- **Motion** - Animations
- **Lucide React** - Icons
- **sql.js** - SQLite in WebAssembly

---

## Philosophy

> "Discipline equals freedom"

TeaTime is designed to help you build daily discipline through structured breaks between deep work sessions. Each session logged is proof of your commitment to intentional living.
