const columns = ["名称", "成功率", "失败率", "状态", "详细报告"];
const data = [];  // 存储解析后的 JSON 数据
const folderPath = '/report/summary'; // 服务器路径
const failExampleCount = {}

// 使用 fetch 加载文件列表
async function readJsonFiles() {
  try {
    // 通过服务器的 /report/summary API 获取文件列表
    const response = await fetch('http://localhost:8080/report/summary');  // 确保路径正确
    const files = await response.json();  // 获取所有 JSON 文件列表

    let fileCount = 0;


    for (const file of files) {
      const filePath = `http://localhost:8080/report/summary/${file}`;  // 拼接完整的文件 URL

      try {
        // 获取每个 JSON 文件的内容
        const jsonData = await fetch(filePath);
        const parsedData = await jsonData.json();  // 解析 JSON 内容

        // 提取数据并计算成功率与失败率
        const summaryName = parsedData.name;
        const summarySum = parsedData.sum;
        const summaryPassed = (parsedData.passed / summarySum) * 100;
        const summaryFailed = 100 - summaryPassed;
        const summaryState = summaryPassed === 100 ? '通过' : '失败';


        // 如果 JSON 数据中有 failExample 字段
        if (parsedData.failExample && Array.isArray(parsedData.failExample)) {
            parsedData.failExample.forEach(example => {
            // 更新字典中的计数
            if (failExampleCount[example]) {
              failExampleCount[example] += 1;
            } else {
              failExampleCount[example] = 1;
            }
          });
        }
        // 将数据封装成字典并添加到数组
        const dict = {
          名称: summaryName,
          成功率: `${summaryPassed.toFixed(2)}%`,
          失败率: `${summaryFailed.toFixed(2)}%`,
          状态: summaryState,
        };
        data.push(dict);  // 将解析后的数据添加到数组中


        fileCount++;  // 每读取一个文件就增加计数
      } catch (err) {
        console.error(`读取或解析文件 ${filePath} 时出错：`, err);
      }
    }

    console.log("失败用例",failExampleCount)
    console.log(`文件夹 ${folderPath} 中共有 ${fileCount} 个文件`);
    console.log('读取到的所有 JSON 数据：', data);  // 在所有文件处理完成后输出 data

    if (fileCount > 0) {
      renderTable();  // 先渲染表格
      renderPieChart(data); // 再渲染饼图
    } else {
      console.log('没有文件可显示');
    }

  } catch (err) {
    console.error('读取文件夹时出错:', err);
  }
}

// 渲染表格的函数
function renderTable() {
  const headerRow = document.getElementById("tableHeader");
  headerRow.innerHTML = ''; // 清空之前内容
  columns.forEach(col => {
    const th = document.createElement("th");
    th.textContent = col;
    headerRow.appendChild(th);
  });

  const tableBody = document.getElementById("tableBody");
  tableBody.innerHTML = ''; // 清空之前内容
  data.forEach(rowData => {
    const tr = document.createElement("tr");
    columns.forEach(col => {
      const td = document.createElement("td");
      if (col === "详细报告") {
        const btn = document.createElement("button");
        btn.textContent = "查看";
        btn.onclick = () => {
          openDetailReport(rowData["名称"]);
        };
        td.appendChild(btn);
      } else {
        td.textContent = rowData[col] || "";
      }

      // 给“状态”列添加颜色
      if (col === "状态") {
        if (rowData[col] === "通过") {
          td.style.backgroundColor = '#4CAF50'; // 绿色
          td.style.color = "#000";  // 黑色文字
          td.style.fontWeight = "bold";          // 加粗
        } else if (rowData[col] === "失败") {
          td.style.backgroundColor = '#F44336'; // 红色
          td.style.color = "#000";  // 黑色文字
          td.style.fontWeight = "bold";          // 加粗
        }
      }
      tr.appendChild(td);
    });
    tableBody.appendChild(tr);
  });
}

// 绘制饼图函数
let pieChartInstance = null;

function renderPieChart(data) {
  let totalSuccess = 0;
  let totalFail = 0;

  data.forEach(item => {
    if (item.状态 === '通过') {
      totalSuccess += 100;
      totalFail += 0;
    } else if (item.状态 === '失败') {
      totalSuccess += 0;
      totalFail += 100;
    }
  });

  const count = data.length;
  const avgSuccess = count ? totalSuccess / count : 0;
  const avgFail = count ? totalFail / count : 0;

  const ctx = document.getElementById('pieChart').getContext('2d');

  if (pieChartInstance) {
    pieChartInstance.destroy();
  }

  pieChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['成功率', '失败率'],
      datasets: [{
        label: '测试成功率 vs 失败率',
        data: [avgSuccess.toFixed(2), avgFail.toFixed(2)],
        backgroundColor: ['#4CAF50', '#F44336'],
        hoverOffset: 20
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'bottom'
        },
        tooltip: {
          callbacks: {
            label: ctx => ctx.label + ': ' + ctx.parsed + '%'
          }
        }
      }
    }
  });


  // 提取失败用例名称作为标签
  const labels = Object.keys(failExampleCount);
  // 提取失败用例数量作为数据
  const faildata = Object.values(failExampleCount);
  // 组合为对象数组，排序，再拆解
  const sortedData = labels.map((label, index) => ({
    label,
    value: faildata[index],
    color: `hsl(${(index * 360 / labels.length)}, 70%, 60%)`
  })).sort((a, b) => b.value - a.value);  // 按值降序排序

  // 限制最多展示 30 条数据
  const maxDisplay = 20;
  const limitedData = sortedData.slice(0, maxDisplay);

  // 拆解排序后的数据
  const sortedLabels = limitedData.map(item => item.label);
  const sortedValues = limitedData.map(item => item.value);
  const sortedColors = limitedData.map(item => item.color);
  const ctx2 = document.getElementById('summaryChart').getContext('2d');

  // 计算 canvas 高度，根据条形数量动态调整
  const barHeight = 30;  // 固定每个条形的高度
  let barSpacing = 2;
  if(limitedData.length <= 5){
    barSpacing = 15; // 每个条形之间的间隔
  }
  const canvasHeight = (limitedData.length * (barHeight + barSpacing));  // 根据条形数量自适应高度
  console.log(canvasHeight);

  // 设置 canvas 高度
  const canvas = document.getElementById('summaryChart');
  canvas.height = canvasHeight;
  console.log(canvas.height);


  summaryChartInstance = new Chart(ctx2, {
  type: 'bar',
  data: {
    labels: sortedLabels, // 用失败用例名称作为标签
    datasets: [{
      label: '失败用例数',
      data: sortedValues,  // 使用 failExampleCount 中的失败次数数据
      backgroundColor: sortedColors, // 失败用例的颜色
      maxBarThickness:40
    }],
  },

  options: {
    indexAxis: 'y',  // 横向条形图
    responsive: true,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: false,
        text: '失败用例统计'
      }
    },
    scales: {
      y: {
        ticks: {
          font: {
            size: 14,
            weight: 'bold',
            family: 'Arial',
            padding: 1
          },
        }

      },
      x: {
        beginAtZero: true,  // 确保 X 轴从零开始
        ticks: {
          padding: 10
        },
      }
    },
  }
});

  // 监听 window 的 resize 事件并触发图表的 resize 方法
  window.addEventListener('resize', () => {
    // 动态调整 canvas 高度
    canvas.height = (limitedData.length * (barHeight + barSpacing));
    summaryChartInstance.resize();
  });
}

// 跳转到详细报告页面
function openDetailReport(name) {
  // 假设你的详细报告 HTML 地址为 `/report/html/<名称>/index.html`
  const url = `./allure-results/${name}/index.html`;
  window.open(url, '_blank'); // 在新标签页中打开
}

// 调用异步函数执行
readJsonFiles();
