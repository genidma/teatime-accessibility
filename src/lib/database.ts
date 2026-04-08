import initSqlJs, { Database } from "sql.js";

export interface Session {
  id: string;
  categoryId: string;
  title: string;
  date: string;
  time: string;
  duration: number;
  notes?: string;
}

let db: Database | null = null;

const DB_STORAGE_KEY = "teatime_db";

async function getWasmUrl(): Promise<string> {
  // In production (Electron), use the extraResources path
  // In development, use the node_modules path
  if (typeof window !== "undefined") {
    // Check if we're in Electron
    const isElectron = window.location.protocol === "file:";
    if (isElectron) {
      return `../resources/sql-wasm.wasm`;
    }
  }
  // Development - use the node_modules path
  return "/node_modules/sql.js/dist/sql-wasm.wasm";
}

export async function initDatabase(): Promise<void> {
  if (db) return;

  try {
    const SQL = await initSqlJs({
      locateFile: (file) => `https://sql.js.org/dist/${file}`,
    });

    // Try to load existing database from localStorage
    const savedDb = localStorage.getItem(DB_STORAGE_KEY);
    if (savedDb) {
      const binaryArray = Uint8Array.from(atob(savedDb), (c) => c.charCodeAt(0));
      db = new Database(binaryArray);
    } else {
      db = new Database();
    }

    // Create sessions table if it doesn't exist
    db.run(`
      CREATE TABLE IF NOT EXISTS sessions (
        id TEXT PRIMARY KEY,
        categoryId TEXT NOT NULL,
        title TEXT NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        duration INTEGER NOT NULL
      )
    `);

    console.log("[database] Initialized successfully");
  } catch (error) {
    console.error("[database] Failed to initialize:", error);
    throw error;
  }
}

function saveDbToStorage(): void {
  if (!db) return;
  try {
    const data = db.export();
    const base64 = btoa(String.fromCharCode(...data));
    localStorage.setItem(DB_STORAGE_KEY, base64);
  } catch (error) {
    console.error("[database] Failed to save to storage:", error);
  }
}

export async function saveSession(session: Session): Promise<void> {
  if (!db) {
    await initDatabase();
  }

  try {
    db!.run(
      `INSERT OR REPLACE INTO sessions (id, categoryId, title, date, time, duration) VALUES (?, ?, ?, ?, ?, ?)`,
      [session.id, session.categoryId, session.title, session.date, session.time, session.duration]
    );
    saveDbToStorage();
    console.log("[database] Session saved:", session.id);
  } catch (error) {
    console.error("[database] Failed to save session:", error);
    throw error;
  }
}

export async function getAllSessions(): Promise<Session[]> {
  if (!db) {
    await initDatabase();
  }

  try {
    const results = db!.exec("SELECT * FROM sessions ORDER BY date DESC, time DESC");
    if (results.length === 0) {
      return [];
    }

    const sessions: Session[] = [];
    const rows = results[0].values;
    for (const row of rows) {
      sessions.push({
        id: row[0] as string,
        categoryId: row[1] as string,
        title: row[2] as string,
        date: row[3] as string,
        time: row[4] as string,
        duration: row[5] as number,
      });
    }

    console.log("[database] Retrieved sessions:", sessions.length);
    return sessions;
  } catch (error) {
    console.error("[database] Failed to get sessions:", error);
    return [];
  }
}