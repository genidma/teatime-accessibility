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

- When timer hits `0:00`, the session is automatically saved
- Check the **Sessions** tab to see your history
- Check the **Stats** tab for analytics
- Check the **Trends** tab for rolling activity and flow insights

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
| Stats | Statistics and analytics |
| Profile | User settings and preferences |

---

## Development Commands

| Command | Description |
|---------|-------------|
| `npm run dev` | Run in development mode |
| `npm run build` | Build for production |
| `npm run lint` | Run TypeScript checks |
| `npm run test` | Run Playwright tests |
| `npm run test:trace` | Run Playwright tests with trace capture enabled |
| `npm run test:ui` | Run Playwright with the UI runner |
| `npm run codegen` | Launch Playwright codegen against the local app |
| `npm run trace:show -- <trace.zip>` | Open a Playwright trace in Trace Viewer |

---

## Running Tests

```bash
npm run test
```

This runs Playwright coverage for:

- App load and navigation
- Timer interactions
- Session history rendering
- Stats rendering
- Timer save flow into Sessions, Stats, and Trends

---

## Integrated Tools

### Codegen

A test generator that records your manual browser actions and automatically writes the corresponding test code.

Command:

```bash
npm run codegen
```

### Trace Viewer

A GUI tool that lets you investigate test failures by viewing a full timeline of the execution, including DOM snapshots, network requests, and console logs.

Commands:

```bash
npm run test:trace
npm run trace:show -- path/to/trace.zip
```

Notes:

- [`playwright.config.ts`](/c:/Users/user/Documents/GitHub/nasa-delta/teatime-accessibility/playwright.config.ts) already uses `trace: 'on-first-retry'`
- `npm run test:trace` is useful when you want trace artifacts for every local run
- Open the resulting trace archive with `npm run trace:show -- <trace.zip>`

### UI Mode

An interactive dashboard for running and debugging tests with a time-travel experience so you can see exactly what happened at each step.

Command:

```bash
npm run test:ui
```

---

## Playwright + Codegen Workflow

Playwright is the committed regression runner. Codegen, Trace Viewer, and UI Mode are the integrated tools we use around it to author, inspect, and debug tests faster.

### 1. Start the app

In terminal 1:

```bash
npm run dev
```

If this is a fresh machine and the Playwright browser is missing, install it once:

```bash
npx playwright install chromium
```

### 2. Record the flow with codegen

In terminal 2:

```bash
npm run codegen
```

This opens a Playwright browser pointed at `http://127.0.0.1:3000`.

Use it to:

- Click through the feature you want to cover
- Inspect stable selectors
- Capture a rough scaffold for the test

### 3. Move the useful parts into the real suite

Take the generated steps and fold them into [`tests/app.spec.ts`](/c:/Users/user/Documents/GitHub/nasa-delta/teatime-accessibility/tests/app.spec.ts).

Recommended cleanup after recording:

- Prefer `getByRole`, `getByText`, and label-based locators over brittle CSS chains
- Keep each test small and task-focused
- Add assertions for the outcome, not just the clicks
- Remove duplicate waits or noisy generated steps

### 4. Run the recorded test as a regression

Run the full suite:

```bash
npm run test
```

Or run one test by name while iterating:

```bash
npm run test -- --grep "timer session save flows into sessions stats and trends"
```

If you want the Playwright inspector and a visual debugging loop:

```bash
npm run test:ui
```

If you want a full execution timeline for failure analysis:

```bash
npm run test:trace
```

Then open the saved trace in Trace Viewer:

```bash
npm run trace:show -- path/to/trace.zip
```

### 5. Practical workflow

Use `npm run codegen` when:

- You are exploring a new UI flow
- You need help discovering reliable locators
- You want a quick first draft of a test

Use `npm run test` and `npm run test:ui` when:

- You want the committed regression suite
- You are validating a fix before merging
- You need repeatable pass/fail feedback in CI

Use `npm run test:trace` and Trace Viewer when:

- A test is failing and you need the exact sequence of DOM, console, and network activity
- You want to inspect a flaky interaction after the fact
- You need a visual execution trail instead of just console output

In short: codegen helps us author tests faster, UI Mode helps us debug live, Trace Viewer helps us investigate failures, and Playwright test runs remain the source of truth.

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

- **Circular Dial Timer** - Drag to set any duration `1-60` min
- **Quick Select** - Tap `1-5` for instant short sessions
- **Categories** - Meditation, Gratitude, Deep Work plus custom
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
- Playwright (testing and codegen)

---

## Troubleshooting

**"vite not found" error?**

```bash
npm install
```

**"Failed to resolve import 'recharts'" or "Could not resolve 'react-is'" error in Vite?**

If you encounter this when running the frontend, especially across a VM or WSL, you may need to force install the charting dependencies to satisfy strict peer dependency requirements:

```bash
npm install recharts react-is --save --legacy-peer-deps
```

**Want to test timer is saving?**

1. Open DevTools (F12) -> Console tab
2. Run a 1-minute timer
3. Look for `saveSession called` in the console
4. Check the Sessions tab for the new entry
