// Debug script to check localStorage
console.log('[debug] Checking localStorage for teatime_db');
const saved = localStorage.getItem('teatime_db');
console.log('[debug] teatime_db exists:', !!saved);
if (saved) {
  console.log('[debug] teatime_db length:', saved.length);
  try {
    const binary = Uint8Array.from(atob(saved), c => c.charCodeAt(0));
    console.log('[debug] Decoded size:', binary.length, 'bytes');
  } catch(e) {
    console.log('[debug] Failed to decode:', e);
  }
} else {
  console.log('[debug] No teatime_db in localStorage');
}

// Also check for teatime_sessions (old key from sqlite.ts)
const oldSaved = localStorage.getItem('teatime_sessions');
console.log('[debug] teatime_sessions exists:', !!oldSaved);
if (oldSaved) {
  console.log('[debug] teatime_sessions length:', oldSaved.length);
  try {
    const parsed = JSON.parse(oldSaved);
    console.log('[debug] Parsed sessions count:', parsed.length);
  } catch(e) {
    console.log('[debug] Failed to parse sessions:', e);
  }
}