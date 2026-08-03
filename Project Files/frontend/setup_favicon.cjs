const fs = require('fs');
const path = require('path');

const src = 'C:\\Users\\salam\\.gemini\\antigravity\\brain\\b4df42b4-940b-400f-8a28-dd89d0ad15f7\\opticrop_favicon_1784042662793.jpg';
const destDir = 'd:\\opticrop-ai-main\\public';
const destFile = path.join(destDir, 'favicon.png');

if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir, { recursive: true });
}

try {
  fs.copyFileSync(src, destFile);
  console.log(`Successfully copied favicon to ${destFile}`);

  // Delete the old favicon.ico if it exists
  const oldIco = path.join(destDir, 'favicon.ico');
  if (fs.existsSync(oldIco)) {
    fs.unlinkSync(oldIco);
    console.log('Removed old favicon.ico');
  }
} catch (err) {
  console.error(`Error copying favicon: ${err.message}`);
}
