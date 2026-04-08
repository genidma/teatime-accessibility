import * as React from 'react';
import { useState, useEffect } from 'react';
import { initDatabase, getAllSessions, type Session } from '../lib/database';

export default function SessionHistoryList() {
  const [sessions, setSessions] = useState<Session[]>([]);

  useEffect(() => {
    async function loadSessions() {
      try {
        await initDatabase();
        const dbSessions = await getAllSessions();
        setSessions(dbSessions);
      } catch (e) {
        console.error('Failed to load sessions:', e);
        setSessions([]);
      }
    }
    loadSessions();
  }, []);

  return (
    <div>
      <h1>Session History</h1>
      <div>
        {sessions.map((session) => (
          <div key={session.id}>
            <p>{session.title} - {session.duration} min</p>
          </div>
        ))}
      </div>
    </div>
  );
}