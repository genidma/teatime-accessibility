// Preload script: Securely expose Electron APIs to the renderer
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    // We will add IPC methods here later (e.g., startTimer, logSession)
});
