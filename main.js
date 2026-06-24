const { app, BrowserWindow, ipcMain } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let mainWindow;
let pythonProcess;

function startBackend() {
  const serverPath = path.join(__dirname, 'backend', 'server.py');
  pythonProcess = spawn('python', [serverPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });
  pythonProcess.stderr.on('data', (data) => {
    console.log(`Backend: ${data}`);
  });
  return new Promise((resolve) => {
    const check = setInterval(() => {
      const http = require('http');
      http.get('http://127.0.0.1:5678/api/health', (res) => {
        clearInterval(check);
        resolve();
      }).on('error', () => {});
    }, 500);
  });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      webviewTag: true,
    }
  });
  mainWindow.loadFile(path.join(__dirname, 'frontend', 'index.html'));
  mainWindow.setTitle('简历投递助手');
}

app.whenReady().then(async () => {
  await startBackend();
  createWindow();
});

app.on('window-all-closed', () => {
  if (pythonProcess) pythonProcess.kill();
  app.quit();
});
