const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');

const DB_FILE = 'teatime-sessions.db';

function getDbPath() {
    const userDataPath = app.getPath('userData');
    return path.join(userDataPath, DB_FILE);
}

function createWindow() {
    const mainWindow = new BrowserWindow({
        width: 800,
        height: 600,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        }
    });

    const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
    if (isDev) {
        mainWindow.loadURL('http://localhost:3000');
    } else {
        mainWindow.loadFile(path.join(__dirname, 'dist/index.html'));
    }

    if (isDev) {
        mainWindow.webContents.openDevTools();
    }
}

try {
    require('electron-reloader')(module);
} catch (_) { }

ipcMain.handle('db:save', async (event, data) => {
    try {
        const dbPath = getDbPath();
        fs.writeFileSync(dbPath, Buffer.from(data));
        return { success: true };
    } catch (error) {
        console.error('Failed to save database:', error);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('db:load', async () => {
    try {
        const dbPath = getDbPath();
        if (fs.existsSync(dbPath)) {
            const data = fs.readFileSync(dbPath);
            return { success: true, data: Array.from(data) };
        }
        return { success: true, data: null };
    } catch (error) {
        console.error('Failed to load database:', error);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('db:getPath', async () => {
    return getDbPath();
});

app.whenReady().then(() => {
    createWindow();

    app.on('activate', function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on('window-all-closed', function () {
    if (process.platform !== 'darwin') app.quit();
});
