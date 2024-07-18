const { app, BrowserWindow, Menu } = require('electron');
const path = require('path');
const { exec } = require('child_process');

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
  });

  mainWindow.loadURL('http://localhost:8000');

  const menuTemplate = [
    {
      label: 'Reload',
      click: () => {
        mainWindow.reload();
      }
    },
    {
      label: 'Add New Window',
      click: () => {
        createNewWindow();
      }
    },
    {
      label: 'Inventory',
      click: () => {
        mainWindow.loadURL('http://localhost:8000');
      }
    }
  ];

  const menu = Menu.buildFromTemplate(menuTemplate);
  Menu.setApplicationMenu(menu);
}

function createNewWindow() {
  const newWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
  });

  newWindow.loadURL('http://localhost:8000');
}

function startDjangoServer() {
  const djangoServer = exec(path.join(__dirname, 'dist/DjangoApp/DjangoApp.exe runserver'), (error, stdout, stderr) => {
    if (error) {
      console.error(`Error starting Django server: ${error}`);
      return;
    }
    console.log(`Django server stdout: ${stdout}`);
    console.error(`Django server stderr: ${stderr}`);
  });

  djangoServer.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });

  djangoServer.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });

  djangoServer.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });
}

app.whenReady().then(() => {
  startDjangoServer();
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
