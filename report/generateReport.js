const fs = require('fs');
const path = require('path');
const baseDir = __dirname;

// ========== 主程序入口 ==========
const args = process.argv.slice(2); // 命令行参数

if (args.length === 0) {
  console.error("❌ 请提供时间戳目录参数，例如: node generateReport.js 20250610155137");
  process.exit(1);
}

const exampleName = args[0];

// ========== 读取所有 JSON 文件 ==========
const imgDirName =  'img' // 图片文件夹名

function readAllJsonFiles(dirPath) {
  //console.log(`readAllJsonFiles:${dirPath}`)
  const dataList = [];
  const countExample = {count:0,pass:0,fail:0}
  const allData = {countExample:countExample,data:dataList};
  let id = 1;

  if (!fs.existsSync(dirPath)) {
    console.error("❌ 目录不存在: " + dirPath);
    return [];
  }

  const files = fs.readdirSync(dirPath);
  for (const file of files) {
    const filePath = path.join(dirPath, file);
    if (file.endsWith('.json')) {
      try {
        const content = fs.readFileSync(filePath, 'utf-8');
        const data = JSON.parse(content);
        const img_name = data.fullName.replace(/.*\.(\w+)#(\w+)$/, "$1_$2") + '.jpg';
        //console.log("ReporImgName:",img_name)

        // 处理msg字段，生成相对路径 img/xxx.jpg
        const  msgPath = path.join(imgDirName, path.basename(img_name)).replace(/\\/g, '/');
        //console.log('图片路径',msgPath)
        // 判断图片文件是否存在，实际路径为 outputDir/img/xxx.jpg，需要传入完整绝对路径判断
        const absImgPath = path.join(baseDir, 'allure-results', exampleName, msgPath);
        const finalMsgPath = fs.existsSync(absImgPath) ? msgPath : ''; // 不存在就空字符串
        //计算耗时
        const duration = data.stop && data.start ? `${data.stop - data.start} ms` : '';
        //打印错误信息
        const errmsg = data.status === 'failed' ? data.statusDetails.message : ''

        allData.countExample.count += 1
        if(data.status === 'passed'){
          allData.countExample.pass += 1
        }else {
          allData.countExample.fail += 1
        }

        allData.data.push({
          id: id++,
          name: data.name || '',
          duration: duration,
          status: data.status === 'passed' ? '通过' : '失败',
          msg: finalMsgPath,
          err: errmsg,
          module: data.fullName || '',
          start: data.start
        });
        //console.log(`✅ 已读取: ${filePath}`);
      } catch (e) {
        //console.error(`❌ 读取失败: ${filePath}，原因: ${e.message}`);
      }
    }
  }
  //console.log(`统计用例数: ${allData.countExample.count}, ${allData.countExample.pass}, ${allData.countExample.fail}`);
  return allData;
}

// ========== 生成 HTML 报告 ==========
function generateHtmlReport(data, outputPath = 'my_test_report', title = '测试报告') {
  // 确保输出目录存在
  if (!fs.existsSync(outputPath)) {
    fs.mkdirSync(outputPath, {recursive: true});
  }
  // 复制public目录和背景图
  const srcPublicDir = path.join(baseDir, 'public');
  const destPublicDir = path.join(outputPath, 'public');
  if (fs.existsSync(srcPublicDir)) {
    if (!fs.existsSync(destPublicDir)) {
      fs.mkdirSync(destPublicDir, {recursive: true});
    }
    // 复制背景图片
    const bgSrc = path.join(srcPublicDir, 'background2.gif');
    const bgDest = path.join(destPublicDir, 'background2.gif');
    fs.copyFileSync(bgSrc, bgDest);
  }

  const rowsPerPageOptions = [10, 20, 50, 100]; // 每页的条目数
  const defaultRowsPerPage = 20; //默认条目数
  // 计算总页数
  const totalPages = Math.ceil(data.length / defaultRowsPerPage);

  const html = `<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="utf-8">
  <title>${title}</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 100px;
      gap: 100px;
      background-image: url('public/background2.gif');  /* 添加这一行 */
      background-size: 15%;
      background-repeat: no-repeat;             /* 防止重复平铺 */
      background-position: top;       /* 居中显示背景图 */
    }
    table {
      border-collapse: collapse;
      width: 100%;
      background: #fff;
      box-shadow: 0 0 8px rgba(0,0,0,0.1);
    }
    th, td {
      border: 1px solid #ddd;
      padding: 10px;
      text-align: center;
      vertical-align: middle;
      word-break: break-word;
    }
    th {
      background-color: #f0f0f0;
    }
    tr.passed {
      background-color: #e6ffed;
    }
    tr.failed {
      background-color: #ffe6e6;
    }
    .msg-col img {
      max-width: 200px;
      max-height: 150px;
      border: 1px solid #ccc;
      cursor: pointer; /* 鼠标悬停变成手指 */
      transition: 0.3s ease;
    }
    .msg-col img:hover {
      opacity: 0.8;
    }
    /* 模态弹窗样式 */
    #modal {
      display: none; /* 默认隐藏 */
      position: fixed;
      z-index: 9999;
      padding-top: 60px;
      left: 0; top: 0;
      width: 100%; height: 100%;
      overflow: auto;
      background-color: rgba(0,0,0,0.8);
    }
    #modal img {
      margin: auto;
      display: block;
      max-width: 90%;
      max-height: 80%;
      box-shadow: 0 0 15px #fff;
      border-radius: 4px;
    }
    #modal span {
      position: absolute;
      top: 20px;
      right: 35px;
      color: #fff;
      font-size: 40px;
      font-weight: bold;
      cursor: pointer;
      transition: 0.3s;
    }
    #modal span:hover {
      color: #bbb;
    }
    .id-col { width: 50px; }
    .name-col { width: 100px; }
    .duration-col { width: 100px; }
    .status-col { width: 100px; }
    .module-col { width: 480px; }
    .msg-col { width: 300px; }
    .err-co { width: 480px; }
    .pagination {
      text-align: center;
      margin-top: 20px;
    }
    .pagination button,
    .pagination select,
    .pagination span {
      padding: 5px 10px;
      margin: 0 5px;
      cursor: pointer;
    }
    .pagination select {
      padding: 5px;
    }
    #paginationBottom {
      position: static;   /* 默认文档流定位，不固定 */
      bottom: 20px;        /* 这个值在 static 下不生效，可以去掉 */
      left: 0;
      right: 0;
      background: #fff;
      z-index: 999;
      margin-top: 20px;    /* 向下偏移20px，确保它在页面内容底部 */
      padding: 10px 0;     /* 上下内边距 */
      width: 100%;         /* 宽度占满整个页面 */
      text-align: center;  /* 内容居中 */
    }
  </style>
</head>
<body>
  <h1>${title}</h1>
  <h2 style="margin-top:-120px;text-align:right;">用例总计：${data.countExample.count}</h2>
  <h2 style="margin-top:-25px;text-align:right;">通过：${data.countExample.pass}</h2>
  <h2 style="margin-top:-25px;text-align:right;">失败：${data.countExample.fail}</h2>

  <table id="testTable">
    <thead>
      <tr>
        <th class="id-col">编号</th>
        <th class="name-col">用例名</th>
        <th class="duration-col">耗时</th>
        <th class="status-col">状态</th>
        <th class="msg-col">截图</th>
        <th class="err-col">错误信息</th>
        <th class="module-col">所属模块</th>
        <th style="display:none">开始时间</th>
      </tr>
    </thead>
    <tbody id="tableBody">
      ${data.data
      .sort((b, a) => new Date(b.start) - new Date(a.start)) // 按开始时间降序排序
      .map((row, index) => {
        row.id = index + 1;
        const statusClass = row.status === '通过' ? 'passed' : 'failed';
        const msgHtml = row.msg
            ? `<img src="${row.msg}" alt="截图" onclick="openModal(this.src)" />`
            : '';
        return `
          <tr class="${statusClass}">
            <td class="id-col">${row.id}</td>
            <td class="name-col">${row.name}</td>
            <td class="duration-col">${row.duration}</td>
            <td>${row.status}</td>
            <td class="msg-col">${msgHtml}</td>
            <td class="err-col">${row.err}</td>
            <td class="module-col">${row.module}</td>
            <td style="display:none">${row.start || ''}</td> <!-- 隐藏的开始时间列 -->
          </tr>`;
      }).join('')}
    </tbody>
    </table>
    
     <!-- 模态弹窗 -->
    <div id="modal" onclick="closeModal(event)">
      <span onclick="closeModal(event)">&times;</span>
      <img id="modal-img" src="" alt="放大截图" />
    </div>
    
    <!-- 分页控件 -->
    <div id="paginationBottom" class="pagination">
      <label for="rowsPerPage">每页显示:</label>
      <select id="rowsPerPage" onchange="updateTable()">
        ${rowsPerPageOptions.map(option => `<option value="${option}" ${option === defaultRowsPerPage ? 'selected' : ''}>${option}</option>`).join('')}
      </select>
  
      <button onclick="prevPage()">上一页</button>
      <span id="pageDisplay">第 1 页 / 共 ${totalPages} 页</span>
      <button onclick="nextPage()">下一页</button>
  
      <!-- 分页跳转 -->
      <span>跳转到: </span>
      <select id="pageSelect" onchange="jumpToPage()">
        ${Array.from({length: totalPages}, (_, i) => `<option value="${i + 1}">${i + 1}</option>`).join('')}
      </select>
    </div>
   
  
    <script>
      let currentPage = 1;
      let rowsPerPage = ${defaultRowsPerPage}; // 默认每页显示20条
      let totalPages = Math.ceil(${data.data.length} / rowsPerPage);;
      
      // 更新总页数并重新渲染
      function updateTotalPages() {
        totalPages = Math.ceil(${data.data.length} / rowsPerPage);
      }
  
      function renderTable() {
        const tableRows = document.querySelectorAll('#testTable tbody tr');
        const startIdx = (currentPage - 1) * rowsPerPage;
        const endIdx = currentPage * rowsPerPage;
  
        // 隐藏所有行
        tableRows.forEach((row, index) => {
          if (index >= startIdx && index < endIdx) {
            row.style.display = '';
          } else {
            row.style.display = 'none';
          }
        });
        
        document.getElementById('pageDisplay').innerText = '第 ' + currentPage + ' 页 / 共 ' + totalPages + ' 页';
        // 更新分页选择框
        const pageSelect = document.getElementById('pageSelect');
        pageSelect.innerHTML = '';
        for (let i = 1; i <= totalPages; i++) {
          const option = document.createElement('option');
          option.value = i;
          option.innerText = i;
          pageSelect.appendChild(option);
        }
        pageSelect.value = currentPage;
      }
      
      // 更新表格显示内容
      function updateTable() {
        rowsPerPage = document.getElementById('rowsPerPage').value;
        currentPage = 1; // 每次更新时重置当前页
        updateTotalPages(); // 更新总页数
        renderTable();
      }
  
      function nextPage() {
        if (currentPage < totalPages) {
          currentPage++;
          renderTable();
        }
      }
  
      function prevPage() {
        if (currentPage > 1) {
          currentPage--;
          renderTable();
        }
      }
      
      function jumpToPage() {
        currentPage = parseInt(document.getElementById('pageSelect').value);
        renderTable();
      }
      // 初次渲染表格
      renderTable();
      
      
      function openModal(src) {
        const modal = document.getElementById('modal');
        const modalImg = document.getElementById('modal-img');
        modal.style.display = "block";
        modalImg.src = src;
      }
      function closeModal(event) {
        // 点击遮罩层或关闭按钮关闭弹窗
        if (event.target.id === 'modal' || event.target.tagName === 'SPAN') {
          document.getElementById('modal').style.display = "none";
        }
      }
    </script>
</body>
</html>`;

  fs.writeFileSync(path.join(outputPath, 'index.html'), html, 'utf-8');
  console.log(`✅ 报告已生成: ${path.resolve(outputPath, 'index.html')}`);
}



function runGenerate(exampleName) {
  const timestamp = exampleName;
  const jsonDir = path.join(baseDir, 'allure-results', timestamp, 'json');
  const outputDir = path.join(baseDir, 'allure-results', timestamp);
  //console.log(`runGenerate文件：jsonDir ${jsonDir}`)

  const testData = readAllJsonFiles(jsonDir);
  //console.log(`runGenerate文件：testData ${testData.data}`)
  generateHtmlReport(testData, outputDir, `测试报告 - ${timestamp}`);

}


//最终生成报告
runGenerate(exampleName);
