const { app, BrowserWindow } = require('electron');
const path = require('path');
const { exec } = require('child_process');

let mainWindow;

function createWindow () {
  mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
    }
  });

  // Load your Django app URL (update to match your server URL)
  mainWindow.loadURL('http://127.0.0.1:8000');

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

// Start the Django server
function startDjangoServer() {
  const server = exec(path.join(__dirname, 'dist/moiinventory.exe'));

  server.stdout.on('data', function(data) {
    console.log('stdout: ' + data.toString());
  });

  server.stderr.on('data', function(data) {
    console.log('stderr: ' + data.toString());
  });

  server.on('exit', function(code) {
    console.log('child process exited with code ' + code.toString());
  });

  return server;
}

app.on('ready', () => {
  const djangoServer = startDjangoServer();
  createWindow();

  app.on('before-quit', () => {
    // Stop the Django server when the Electron app is closed
    djangoServer.kill();
  });
});

app.on('window-all-closed', function () {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', function () {
  if (mainWindow === null) {
    createWindow();
  }
});
