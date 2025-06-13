const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 8080;

app.use(express.static(path.join(__dirname)));

// 把 summary 目录映射成静态资源目录
app.use('/report/summary', express.static(path.join(__dirname, 'summary')));

app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

// 读取 summary 目录中文件列表的接口
app.get('/report/summary', (req, res) => {
  const folderPath = path.join(__dirname, 'summary');
  console.log(`Reading files from: ${folderPath}`);

  fs.readdir(folderPath, (err, files) => {
    if (err) {
      console.error('Error reading directory:', err);
      return res.status(500).json({ error: '无法读取文件夹' });
    }
    const jsonFiles = files.filter(file => path.extname(file).toLowerCase() === '.json');
    res.json(jsonFiles);
  });
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
