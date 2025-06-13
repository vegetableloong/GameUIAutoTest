const fs = require('fs').promises;
const path = require('path');

console.log((__dirname))

// 确保目标文件夹存在
async function ensureDirectoryExists(directoryPath) {
  try {
    await fs.mkdir(path.dirname(directoryPath), { recursive: true });
    console.log(`✅ 确保目录 ${directoryPath} 存在`);
  } catch (err) {
    console.error('创建目录失败:', err);
  }
}

// 写入 summary.json 文件
async function writeSummaryFile(data, summaryFilePath) {
  try {
    await fs.writeFile(summaryFilePath, JSON.stringify(data, null, 2), 'utf8');
    console.log('✅ summary.json 已成功更新');
  } catch (err) {
    console.error('写入 summary.json 失败:', err);
  }
}

// 加载并读取文件夹中的 JSON 文件，统计并更新数据
async function loadDataAndUpdateSummary(folderPath, summaryFilePath, name) {
  try {
    const files = await fs.readdir(folderPath);

    let jsonFileCount = 0;
    let passedCount = 0;
    let failList = [];

    // 遍历所有文件
    for (let file of files) {
      const filePath = path.join(folderPath, file);
      const stat = await fs.stat(filePath);

      // 只处理 .json 文件
      if (stat.isFile() && path.extname(file).toLowerCase() === '.json') {

        try {
          const fileContent = await fs.readFile(filePath, 'utf8');
          const jsonData = JSON.parse(fileContent);

          //console.log(`✅ 读取 ${file}:`);
          //console.log(jsonData.name, jsonData.status);  // 输出内容
          // 根据 存在用例名字字段统计的用例总数
          if (jsonData.name) {
            jsonFileCount++;
              // 根据 status 字段统计通过的个数
            if (jsonData.status === "passed") {
              passedCount++;
            } else {
              tmpName = jsonData.fullName
              failName = tmpName.substring(tmpName.lastIndexOf('.') + 1);
              failList.push(failName)
            }
          }

        } catch (e) {
          console.error(`❌ 解析 ${file} 时出错:`, e.message);
        }
      }
    }

    // 更新 summary.json 中的内容
    const updatedData = {
      name: name,       // 动态传入的 name
      sum: jsonFileCount,    // 更新文件总数
      passed: passedCount,   // 更新通过的用例数
      failExample: failList  // 更新失败的用例
    };

    // 写入更新后的数据
    await writeSummaryFile(updatedData, summaryFilePath);

  } catch (err) {
    console.error('读取文件夹或处理文件时出错:', err);
  }
}

// 主函数：确保目录存在并更新 summary.json
async function processing(name) {
  const folderPath = path.join(__dirname, '.', 'allure-results', name, 'json' );   // 使用动态传入的 name
  const summaryFilePath = path.join(__dirname, '.', 'summary', `${name}.json` );

  await ensureDirectoryExists(summaryFilePath);  // 确保目录存在
  await loadDataAndUpdateSummary(folderPath, summaryFilePath, name);  // 执行统计和更新 summary.json
}

module.exports = { loadDataAndUpdateSummary, ensureDirectoryExists, writeSummaryFile, processing };
