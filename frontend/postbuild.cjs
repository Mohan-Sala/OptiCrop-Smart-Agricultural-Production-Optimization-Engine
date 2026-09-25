const fs = require('fs');
const path = require('path');

const clientDir = path.join(__dirname, 'dist', 'client');
const distDir = path.join(__dirname, 'dist');
const shellHtml = path.join(clientDir, '_shell.html');
const clientIndexHtml = path.join(clientDir, 'index.html');
const distIndexHtml = path.join(distDir, 'index.html');

if (fs.existsSync(shellHtml)) {
  fs.copyFileSync(shellHtml, clientIndexHtml);
  fs.copyFileSync(shellHtml, distIndexHtml);
  console.log('Successfully copied _shell.html to index.html in dist and dist/client');
}

const clientAssets = path.join(clientDir, 'assets');
const distAssets = path.join(distDir, 'assets');
if (fs.existsSync(clientAssets) && !fs.existsSync(distAssets)) {
  fs.cpSync(clientAssets, distAssets, { recursive: true });
  console.log('Successfully copied assets to dist/assets');
}

const clientFavicon = path.join(clientDir, 'favicon.png');
const distFavicon = path.join(distDir, 'favicon.png');
if (fs.existsSync(clientFavicon) && !fs.existsSync(distFavicon)) {
  fs.copyFileSync(clientFavicon, distFavicon);
}
