const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
    saveDatabase: (data) => ipcRenderer.invoke('db:save', data),
    loadDatabase: () => ipcRenderer.invoke('db:load'),
    getDbPath: () => ipcRenderer.invoke('db:getPath'),
});
