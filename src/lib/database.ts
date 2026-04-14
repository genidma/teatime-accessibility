import initSqlJs, { Database } from 'sql.js';
import { auth, db as firestore } from '../firebase/index';
import { collection, doc, setDoc, query, where, onSnapshot } from 'firebase/firestore';

export interface Session {
  id: string;
  categoryId: string;
  title: string;
  date: string;
  time: string;
  duration: number;
  notes?: string;
  createdAt?: string;
  updatedAt?: string;
  userId?: string;
}

declare global {
  interface Window {
    electronAPI?: {
      saveDatabase: (data: Uint8Array) => Promise<{ success: boolean; error?: string }>;
      loadDatabase: () => Promise<{ success: boolean; data?: number[] | null; error?: string }>;
      getDbPath: () => Promise<string>;
    };
  }
}

export const SESSIONS_CHANGED_EVENT = 'teatime:sessions-changed';

const DB_STORAGE_KEY = 'teatime_db';
const LEGACY_SESSIONS_KEY = 'teatime_sessions';
const ISO_DATE_PATTERN = /^\d{4}-\d{2}-\d{2}$/;

let db: Database | null = null;
let initPromise: Promise<void> | null = null;

function isElectron(): boolean {
  return typeof window !== 'undefined' && window.electronAPI !== undefined;
}

function toLocalDateKey(date: Date): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}

function formatDateLabel(dateKey: string): string {
  const todayKey = toLocalDateKey(new Date());
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayKey = toLocalDateKey(yesterday);

  if (dateKey === todayKey) return 'Today';
  if (dateKey === yesterdayKey) return 'Yesterday';

  const [year, month, day] = dateKey.split('-').map(Number);
  const date = new Date(year, month - 1, day);
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
}

function parseSessionDate(session: Pick<Session, 'date' | 'time' | 'createdAt'>): Date | null {
  if (session.createdAt) {
    const createdAt = new Date(session.createdAt);
    if (!Number.isNaN(createdAt.getTime())) {
      return createdAt;
    }
  }

  if (ISO_DATE_PATTERN.test(session.date)) {
    const date = new Date(`${session.date}T00:00:00`);
    if (!Number.isNaN(date.getTime())) {
      return date;
    }
  }

  if (session.date === 'Today' || session.date === 'Yesterday') {
    const date = new Date();
    if (session.date === 'Yesterday') {
      date.setDate(date.getDate() - 1);
    }
    return date;
  }

  const parsedLegacy = new Date(`${session.date}, ${new Date().getFullYear()} ${session.time || '12:00 AM'}`);
  if (!Number.isNaN(parsedLegacy.getTime())) {
    return parsedLegacy;
  }

  return null;
}

function getSessionDateKey(session: Pick<Session, 'date' | 'time' | 'createdAt'>): string | null {
  if (ISO_DATE_PATTERN.test(session.date)) {
    return session.date;
  }

  const parsed = parseSessionDate(session);
  return parsed ? toLocalDateKey(parsed) : null;
}

function normalizeDateValue(date: string | undefined, createdAt: string): string {
  if (date && ISO_DATE_PATTERN.test(date)) {
    return date;
  }

  const createdAtDate = new Date(createdAt);
  if (!Number.isNaN(createdAtDate.getTime())) {
    return toLocalDateKey(createdAtDate);
  }

  return toLocalDateKey(new Date());
}

function isLegacyDisplayDate(date: string): boolean {
  return date === 'Today' || date === 'Yesterday' || /^[A-Z][a-z]{2} \d{1,2}$/.test(date);
}

function uint8ArrayToBase64(data: Uint8Array): string {
  let binary = '';
  const chunkSize = 0x8000;

  for (let index = 0; index < data.length; index += chunkSize) {
    const chunk = data.subarray(index, index + chunkSize);
    binary += String.fromCharCode(...chunk);
  }

  return btoa(binary);
}

async function loadPersistedBytes(): Promise<Uint8Array | null> {
  if (isElectron()) {
    try {
      const result = await window.electronAPI!.loadDatabase();
      if (result.success && result.data) {
        return new Uint8Array(result.data);
      }
    } catch (error) {
      console.error('[database] Failed to load Electron database:', error);
    }
  }

  const savedDb = localStorage.getItem(DB_STORAGE_KEY);
  if (!savedDb) {
    return null;
  }

  try {
    return Uint8Array.from(atob(savedDb), (character) => character.charCodeAt(0));
  } catch (error) {
    console.error('[database] Failed to decode localStorage database:', error);
    return null;
  }
}

function getColumnNames(database: Database): string[] {
  const pragma = database.exec('PRAGMA table_info(sessions)');
  if (pragma.length === 0) return [];
  return pragma[0].values.map((row) => String(row[1]));
}

function ensureSchema(database: Database): void {
  database.run(`
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

  const columns = getColumnNames(database);

  if (!columns.includes('notes')) {
    database.run('ALTER TABLE sessions ADD COLUMN notes TEXT');
  }

  if (!columns.includes('createdAt')) {
    database.run('ALTER TABLE sessions ADD COLUMN createdAt TEXT');
    database.run(`
      UPDATE sessions
      SET createdAt = CURRENT_TIMESTAMP
      WHERE createdAt IS NULL
    `);
  }

  if (!columns.includes('updatedAt')) {
    database.run('ALTER TABLE sessions ADD COLUMN updatedAt TEXT');
    database.run('UPDATE sessions SET updatedAt = createdAt WHERE updatedAt IS NULL');
  }

  if (!columns.includes('userId')) {
    database.run('ALTER TABLE sessions ADD COLUMN userId TEXT');
  }
}

function getSessionCount(database: Database): number {
  const result = database.exec('SELECT COUNT(*) FROM sessions');
  if (result.length === 0 || result[0].values.length === 0) {
    return 0;
  }

  return Number(result[0].values[0][0] ?? 0);
}

function migrateLegacySessions(database: Database): void {
  if (getSessionCount(database) > 0) {
    return;
  }

  const savedSessions = localStorage.getItem(LEGACY_SESSIONS_KEY);
  if (!savedSessions) {
    return;
  }

  try {
    const parsed = JSON.parse(savedSessions);
    if (!Array.isArray(parsed)) {
      return;
    }

    parsed.forEach((session: Partial<Session>) => {
      if (!session.id || !session.categoryId || !session.title) {
        return;
      }

      const createdAt = typeof session.createdAt === 'string' ? session.createdAt : new Date().toISOString();
      const normalizedDate = normalizeDateValue(typeof session.date === 'string' ? session.date : undefined, createdAt);

      database.run(
        `INSERT OR REPLACE INTO sessions (id, categoryId, title, date, time, duration, notes, createdAt, updatedAt, userId)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
        [
          session.id,
          session.categoryId,
          session.title,
          normalizedDate,
          session.time ?? '12:00 AM',
          Number(session.duration ?? 0),
          session.notes ?? null,
          createdAt,
          createdAt,
          null
        ],
      );
    });

    localStorage.removeItem(LEGACY_SESSIONS_KEY);
  } catch (error) {
    console.error('[database] Failed to migrate legacy sessions:', error);
  }
}

async function persistDatabase(): Promise<void> {
  if (!db) return;

  const data = db.export();

  try {
    localStorage.setItem(DB_STORAGE_KEY, uint8ArrayToBase64(data));
  } catch (error) {
    console.error('[database] Failed to save database to localStorage:', error);
  }

  if (isElectron()) {
    try {
      await window.electronAPI!.saveDatabase(data);
    } catch (error) {
      console.error('[database] Failed to save database to Electron:', error);
    }
  }
}

function emitSessionsChanged(): void {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event(SESSIONS_CHANGED_EVENT));
  }
}

export function subscribeToSessionChanges(onChange: () => void): () => void {
  if (typeof window === 'undefined') {
    return () => {};
  }

  window.addEventListener(SESSIONS_CHANGED_EVENT, onChange);
  return () => window.removeEventListener(SESSIONS_CHANGED_EVENT, onChange);
}

export function isSessionFromToday(session: Pick<Session, 'date' | 'time' | 'createdAt'>): boolean {
  if (session.date === 'Today') {
    return true;
  }

  const sessionDateKey = getSessionDateKey(session);
  return sessionDateKey === toLocalDateKey(new Date());
}

export function getSessionDateLabel(session: Pick<Session, 'date' | 'time' | 'createdAt'>): string {
  if (session.date && isLegacyDisplayDate(session.date)) {
    return session.date;
  }

  const sessionDateKey = getSessionDateKey(session);
  return sessionDateKey ? formatDateLabel(sessionDateKey) : session.date || 'Unknown';
}

export async function initDatabase(): Promise<void> {
  if (db) return;
  if (initPromise) return initPromise;

  initPromise = (async () => {
    try {
      const SQL = await initSqlJs({
        locateFile: () => {
          if (typeof window !== 'undefined' && window.location.origin.includes('localhost')) {
            return '/node_modules/sql.js/dist/sql-wasm.wasm';
          }
          return 'sql-wasm.wasm';
        },
      });

      const persistedBytes = await loadPersistedBytes();
      db = persistedBytes ? new SQL.Database(persistedBytes) : new SQL.Database();

      ensureSchema(db);
      migrateLegacySessions(db);

      if (getSessionCount(db) > 0) {
        await persistDatabase();
      }

      console.log('[database] Initialized successfully');
    } catch (error) {
      db = null;
      console.error('[database] Failed to initialize:', error);
      throw error;
    }
  })();

  try {
    await initPromise;
  } finally {
    initPromise = null;
  }
}

async function getDatabase(): Promise<Database> {
  await initDatabase();
  return db!;
}

function mapSessionRows(database: Database): Session[] {
  const results = database.exec(`
    SELECT id, categoryId, title, date, time, duration, notes, createdAt, updatedAt, userId
    FROM sessions
  `);

  if (results.length === 0) {
    return [];
  }

  return results[0].values
    .map((row) => ({
      id: String(row[0]),
      categoryId: String(row[1]),
      title: String(row[2]),
      date: String(row[3]),
      time: String(row[4]),
      duration: Number(row[5]),
      notes: row[6] ? String(row[6]) : undefined,
      createdAt: row[7] ? String(row[7]) : undefined,
      updatedAt: row[8] ? String(row[8]) : undefined,
      userId: row[9] ? String(row[9]) : undefined,
    }))
    .sort((left, right) => {
      const leftTime = parseSessionDate(left)?.getTime() ?? 0;
      const rightTime = parseSessionDate(right)?.getTime() ?? 0;
      return rightTime - leftTime;
    });
}

export async function saveSession(session: Session): Promise<void> {
  const database = await getDatabase();
  const createdAt = session.createdAt ?? new Date().toISOString();
  const updatedAt = session.updatedAt ?? new Date().toISOString();
  const normalizedDate = normalizeDateValue(session.date, createdAt);
  
  const currentUser = auth.currentUser;
  const sessionUserId = session.userId || (currentUser ? currentUser.uid : undefined);

  try {
    database.run(
      `INSERT OR REPLACE INTO sessions (id, categoryId, title, date, time, duration, notes, createdAt, updatedAt, userId)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        session.id,
        session.categoryId,
        session.title,
        normalizedDate,
        session.time,
        session.duration,
        session.notes ?? null,
        createdAt,
        updatedAt,
        sessionUserId ?? null,
      ],
    );

    await persistDatabase();
    
    // Sync to Firestore if logged in
    if (currentUser && sessionUserId === currentUser.uid) {
      try {
        const docRef = doc(firestore, 'sessions', session.id);
        const payload = {
          ...session,
          date: normalizedDate,
          createdAt,
          updatedAt,
          userId: currentUser.uid
        };
        // Clean out undefined values for Firebase
        Object.keys(payload).forEach(key => payload[key as keyof typeof payload] === undefined && delete payload[key as keyof typeof payload]);
        
        await setDoc(docRef, payload, { merge: true });
      } catch (fbErr) {
        console.error('[database] Failed to push to Firestore:', fbErr);
      }
    }
    
    emitSessionsChanged();
  } catch (error) {
    console.error('[database] Failed to save session:', error);
    throw error;
  }
}

// Global Sync State
let activeSyncListener: (() => void) | null = null;

export async function syncUserData(userId: string): Promise<void> {
  try {
    const database = await getDatabase();
    
    // 1. Wipe previous local data upon login as requested (ensures clean slate for Firebase hydration)
    database.run('DELETE FROM sessions');
    await persistDatabase();
    
    // 2. Realtime sync down from Firestore
    if (activeSyncListener) {
      activeSyncListener();
    }
    
    const q = query(collection(firestore, 'sessions'), where('userId', '==', userId));
    
    activeSyncListener = onSnapshot(q, async (snapshot) => {
      let changed = false;
      const dbInstance = await getDatabase();
      
      snapshot.docChanges().forEach((change) => {
         const data = change.doc.data() as Session;
         if (change.type === 'added' || change.type === 'modified') {
           dbInstance.run(
              `INSERT OR REPLACE INTO sessions (id, categoryId, title, date, time, duration, notes, createdAt, updatedAt, userId)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
              [
                data.id,
                data.categoryId,
                data.title,
                data.date,
                data.time,
                data.duration,
                data.notes ?? null,
                data.createdAt ?? new Date().toISOString(),
                data.updatedAt ?? new Date().toISOString(),
                data.userId ?? userId,
              ]
           );
           changed = true;
         }
      });
      
      if (changed) {
        await persistDatabase();
        emitSessionsChanged();
      }
    }, (error) => {
      console.error('[database] Realtime sync error:', error);
    });
    
  } catch (err) {
    console.error('[database] Sync initialization failed:', err);
  }
}

export function stopSync() {
  if (activeSyncListener) {
    activeSyncListener();
    activeSyncListener = null;
  }
}

export async function getAllSessions(): Promise<Session[]> {
  try {
    const database = await getDatabase();
    return mapSessionRows(database);
  } catch (error) {
    console.error('[database] Failed to get sessions:', error);
    return [];
  }
}

export async function getTodaySessions(): Promise<Session[]> {
  const sessions = await getAllSessions();
  return sessions.filter(isSessionFromToday);
}

export async function getCategoryStats(): Promise<{ categoryId: string; sessions: number; duration: number }[]> {
  const sessions = await getAllSessions();
  const stats = new Map<string, { categoryId: string; sessions: number; duration: number }>();

  sessions.forEach((session) => {
    const current = stats.get(session.categoryId) ?? {
      categoryId: session.categoryId,
      sessions: 0,
      duration: 0,
    };

    current.sessions += 1;
    current.duration += session.duration;
    stats.set(session.categoryId, current);
  });

  return Array.from(stats.values()).sort((left, right) => right.duration - left.duration);
}

export async function getWeeklyActivity(): Promise<{ date: string; duration: number }[]> {
  const sessions = await getAllSessions();
  const dailyTotals = new Map<string, number>();

  sessions.forEach((session) => {
    const dateKey = getSessionDateKey(session);
    if (!dateKey) return;
    dailyTotals.set(dateKey, (dailyTotals.get(dateKey) ?? 0) + session.duration);
  });

  const days: { date: string; duration: number }[] = [];
  const cursor = new Date();

  for (let index = 6; index >= 0; index -= 1) {
    const date = new Date(cursor);
    date.setDate(cursor.getDate() - index);
    const dateKey = toLocalDateKey(date);

    days.push({
      date: dateKey,
      duration: dailyTotals.get(dateKey) ?? 0,
    });
  }

  return days;
}

export async function getHeatmapData(): Promise<{ date: string; count: number }[]> {
  const sessions = await getAllSessions();
  const sessionCounts = new Map<string, number>();
  const cutoff = new Date();
  cutoff.setDate(cutoff.getDate() - 89);
  cutoff.setHours(0, 0, 0, 0);

  sessions.forEach((session) => {
    const parsed = parseSessionDate(session);
    const dateKey = getSessionDateKey(session);

    if (!parsed || !dateKey || parsed < cutoff) {
      return;
    }

    sessionCounts.set(dateKey, (sessionCounts.get(dateKey) ?? 0) + 1);
  });

  return Array.from(sessionCounts.entries())
    .sort(([left], [right]) => left.localeCompare(right))
    .map(([date, count]) => ({ date, count }));
}

function getSessionHour(session: Session): number | null {
  const parsed = parseSessionDate(session);
  if (parsed) {
    return parsed.getHours();
  }

  const time = session.time.trim();
  const match = time.match(/^(\d{1,2})(?::(\d{2}))?\s*(AM|PM)$/i);
  if (!match) return null;

  let hour = Number(match[1]) % 12;
  if (match[3].toUpperCase() === 'PM') {
    hour += 12;
  }

  return hour;
}

export async function getProductiveRange(): Promise<string> {
  const sessions = await getAllSessions();
  if (sessions.length === 0) {
    return 'No data';
  }

  const durationByHour = new Map<number, number>();

  sessions.forEach((session) => {
    const hour = getSessionHour(session);
    if (hour === null) return;
    durationByHour.set(hour, (durationByHour.get(hour) ?? 0) + session.duration);
  });

  if (durationByHour.size === 0) {
    return 'Not enough data';
  }

  const peakHour = Array.from(durationByHour.entries()).sort((left, right) => right[1] - left[1])[0][0];
  const startHour = Math.max(0, peakHour - 1);
  const endHour = Math.min(23, peakHour + 1);

  const formatHour = (hour: number) => {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 === 0 ? 12 : hour % 12;
    return `${displayHour}:00 ${period}`;
  };

  return `${formatHour(startHour)} - ${formatHour(endHour)}`;
}
