const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

// Basic window management boilerplate
function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js') // We'll create this next
        }
    });

    mainWindow.loadFile('index.html');

    // Open DevTools in development mode
    // mainWindow.webContents.openDevTools();
}

// Enable hot reload in development
try {
    require('electron-reloader')(module);
} catch (_) { }

app.whenReady().then(() => {
    createWindow();

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});
