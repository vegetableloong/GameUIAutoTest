const express = require('express');
const fs = require('fs');
const path = require('path');

const app = express();
const port = 8080;

app.use(express.static(path.join(__dirname)));

// 把 summary 目录映射成静态资源目录
app.use('/report/summary', express.static(path.join(__dirname, 'summary')));

// 把 allure-results 目录映射成静态资源目录（用于截图）
app.use('/report/allure-results', express.static(path.join(__dirname, 'allure-results')));

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

// 获取单个 summary JSON 文件
app.get('/report/summary/:name', (req, res) => {
  const filePath = path.join(__dirname, 'summary', req.params.name);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    res.json(JSON.parse(content));
  } else {
    res.status(404).json({ error: '文件不存在' });
  }
});

// 读取 allure-results JSON 目录列表
app.get('/report/allure-results/:name/json', (req, res) => {
  const folderPath = path.join(__dirname, 'allure-results', req.params.name, 'json');
  if (fs.existsSync(folderPath)) {
    fs.readdir(folderPath, (err, files) => {
      if (err) {
        return res.status(500).json({ error: '无法读取文件夹' });
      }
      res.json(files);
    });
  } else {
    res.status(404).json({ error: '文件夹不存在' });
  }
});

// 获取单个 allure JSON 文件
app.get('/report/allure-results/:name/json/:file', (req, res) => {
  const filePath = path.join(__dirname, 'allure-results', req.params.name, 'json', req.params.file);
  if (fs.existsSync(filePath)) {
    const content = fs.readFileSync(filePath, 'utf8');
    res.json(JSON.parse(content));
  } else {
    res.status(404).json({ error: '文件不存在' });
  }
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Server running at http://0.0.0.0:${port}`);
});
