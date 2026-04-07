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

    // Use the dev server URL in development
    const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
    } else {
        mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));
    }

    // Open DevTools in development mode
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }
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
