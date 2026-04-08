// Simple test to verify database functionality
import initSqlJs from 'sql.js';

async function testDatabase() {
  console.log('[test] Starting database test...');
  
  try {
    const SQL = await initSqlJs({
      locateFile: (file) => `https://sql.js.org/dist/${file}`
    });
    
    const db = new SQL.Database();
    console.log('[test] Database created');
    
    db.run(`
      CREATE TABLE IF NOT EXISTS test_sessions (
        id TEXT PRIMARY KEY,
        duration INTEGER
      )
    `);
    console.log('[test] Table created');
    
    db.run(
      `INSERT INTO test_sessions (id, duration) VALUES (?, ?)`,
      ['test-1', 60]
    );
    console.log('[test] Insert completed');
    
    const result = db.exec("SELECT * FROM test_sessions");
    console.log('[test] Query result:', result);
    
    const data = db.export();
    console.log('[test] Database exported, size:', data.length, 'bytes');
    
    console.log('[test] Database test PASSED');
  } catch (error) {
    console.error('[test] Database test FAILED:', error);
  }
}

testDatabase();