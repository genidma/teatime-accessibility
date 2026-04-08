import initSqlJs, { Database } from 'sql.js';

export type Session = {
  id: string;
  categoryId: string;
  title: string;
  date: string;
  time: string;
  duration: number;
  notes?: string;
};

declare global {
  interface Window {
    electronAPI?: {
      saveDatabase: (data: Uint8Array) => Promise<{ success: boolean; error?: string }>;
      loadDatabase: () => Promise<{ success: boolean; data?: number[]; error?: string }>;
      getDbPath: () => Promise<string>;
    };
  }
}

let db: Database | null = null;

function isElectron(): boolean {
  return typeof window !== 'undefined' && window.electronAPI !== undefined;
}

async function saveToFile() {
  if (!db) return;
  
  const data = db.export();
  const uint8Array = new Uint8Array(data);
  
  if (isElectron()) {
    try {
      await window.electronAPI!.saveDatabase(uint8Array);
    } catch (e) {
      console.error('Failed to save to Electron:', e);
    }
  }
}

async function loadFromFile(): Promise<Uint8Array | null> {
  if (isElectron()) {
    try {
      const result = await window.electronAPI!.loadDatabase();
      if (result.success && result.data) {
        return new Uint8Array(result.data);
      }
    } catch (e) {
      console.error('Failed to load from Electron:', e);
    }
  }
  return null;
}

export async function initDatabase(): Promise<Database> {
  if (db) return db;
  
  const SQL = await initSqlJs({
    locateFile: file => `https://sql.js.org/dist/${file}`
  });
  
  db = new SQL.Database();
  
  db.run(`
    CREATE TABLE IF NOT EXISTS sessions (
      id TEXT PRIMARY KEY,
      categoryId TEXT NOT NULL,
      title TEXT NOT NULL,
      date TEXT NOT NULL,
      time TEXT NOT NULL,
      duration INTEGER NOT NULL,
      notes TEXT,
      createdAt TEXT DEFAULT CURRENT_TIMESTAMP
    )
  `);
  
  const fileData = await loadFromFile();
  if (fileData) {
    db = new SQL.Database(fileData);
  } else {
    const saved = localStorage.getItem('teatime_sessions');
    if (saved) {
      try {
        const data = JSON.parse(saved);
        data.forEach((session: any) => {
          db!.run(
            `INSERT INTO sessions (id, categoryId, title, date, time, duration, notes) VALUES (?, ?, ?, ?, ?, ?, ?)`,
            [session.id, session.categoryId, session.title, session.date, session.time, session.duration, session.notes]
          );
        });
      } catch (e) {
        console.error('Failed to parse localStorage data:', e);
      }
    }
  }
  
  return db;
}

export function saveSession(session: {
  id: string;
  categoryId: string;
  title: string;
  date: string;
  time: string;
  duration: number;
  notes?: string;
}) {
  console.log('saveSession called:', session);
  console.log('db exists:', !!db);
  
  if (!db) {
    console.error('ERROR: db is null, calling initDatabase first');
    return;
  }
  
  try {
    db.run(
      `INSERT INTO sessions (id, categoryId, title, date, time, duration, notes) VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [session.id, session.categoryId, session.title, session.date, session.time, session.duration, session.notes || null]
    );
    console.log('Session inserted into db');
    
    saveToLocalStorage();
    console.log('Saved to localStorage');
    
    saveToFile();
    console.log('Saved to file');
  } catch (e) {
    console.error('Error saving session:', e);
  }
}

export function getAllSessions(): any[] {
  if (!db) return [];
  
  const results = db.exec(`SELECT * FROM sessions ORDER BY createdAt DESC`);
  if (results.length === 0) return [];
  
  const columns = results[0].columns;
  return results[0].values.map((row: any[]) => {
    const obj: any = {};
    columns.forEach((col, i) => {
      obj[col] = row[i];
    });
    return obj;
  });
}

export function getSessionsByDate(date: string): any[] {
  if (!db) return [];
  
  const results = db.exec(`SELECT * FROM sessions WHERE date = ? ORDER BY createdAt DESC`, [date]);
  if (results.length === 0) return [];
  
  const columns = results[0].columns;
  return results[0].values.map((row: any[]) => {
    const obj: any = {};
    columns.forEach((col, i) => {
      obj[col] = row[i];
    });
    return obj;
  });
}

export function getTodaySessions(): any[] {
  return getSessionsByDate('Today');
}

function saveToLocalStorage() {
  if (!db) return;
  
  try {
    const results = db.exec(`SELECT * FROM sessions`);
    if (results.length === 0) return;
    
    const columns = results[0].columns;
    const sessions = results[0].values.map((row: any[]) => {
      const obj: any = {};
      columns.forEach((col, i) => {
        obj[col] = row[i];
      });
      return obj;
    });
    
    localStorage.setItem('teatime_sessions', JSON.stringify(sessions));
  } catch (e) {
    console.error('Failed to save to localStorage:', e);
  }
}

export function getCategoryStats(): { categoryId: string; sessions: number; duration: number }[] {
  if (!db) return [];
  
  const results = db.exec(`
    SELECT categoryId, COUNT(*) as sessions, SUM(duration) as duration 
    FROM sessions 
    GROUP BY categoryId
  `);
  
  if (results.length === 0) return [];
  
  return results[0].values.map((row: any[]) => ({
    categoryId: row[0],
    sessions: row[1],
    duration: row[2]
  }));
}