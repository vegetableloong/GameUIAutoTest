// 导入 summaryUpdater 模块
const { processing, loadDataAndUpdateSummary } = require('./process');

const fs = require('fs');
const path = require('path');

console.log(__dirname);


// 规则：文件夹名为14位数字
const folderNamePattern = /^\d{14}$/; // 正则表达式，匹配14位数字

const folderPath = path.join(__dirname, '.', 'allure-results'); //替换为目标文件夹路径
console.log(folderPath);

fs.readdir(folderPath, (err, files) => {
  if (err) {
    return console.error('读取文件夹失败:', err);
  }

  let folderCount = 0;

  files.forEach(file => {
    const filePath = path.join(folderPath, file);
    const stat = fs.statSync(filePath);

    // 判断是否是文件夹，并且文件夹名符合规则
    if (stat.isDirectory() && folderNamePattern.test(file)) {
      folderCount++;
      console.log(`符合规则的子文件夹: ${file}`); // 打印符合规则的文件夹名字
      // 动态传入 'name' 参数
      const name = file; // 你可以根据需要修改这个值
      // 调用 processing 函数，传入动态的 'name'
      processing(name).then(() => {
        console.log('✅ 完成文件统计和更新 summary.json');
      }).catch((err) => {
        console.error('❌ 执行失败:', err);
      });
    }
  });

  console.log(`文件夹 ${folderPath} 中共有 ${folderCount} 个符合规则的子文件夹`);
});