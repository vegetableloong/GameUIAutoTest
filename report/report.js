const API_BASE = 'http://10.100.0.153:8080';
let allData = [];
let currentSort = { column: 'name', direction: 'desc' };
let passRateChart = null;
let failCasesChart = null;
let trendChart = null;

// 格式化时间
function formatTime(name) {
  if (name.length === 14) {
    const year = name.substring(0, 4);
    const month = name.substring(4, 6);
    const day = name.substring(6, 8);
    const hour = name.substring(8, 10);
    const minute = name.substring(10, 12);
    const second = name.substring(12, 14);
    return `${year}-${month}-${day} ${hour}:${minute}:${second}`;
  }
  return name;
}

// 获取服务器IP
function getServerIP() {
  const hostname = window.location.hostname;
  if (hostname && hostname !== 'localhost') {
    return `http://${hostname}:8080`;
  }
  return API_BASE;
}

// 加载所有JSON文件
async function loadAllData() {
  try {
    const serverIP = getServerIP();
    const response = await fetch(`${serverIP}/report/summary`);
    const files = await response.json();

    if (files.length === 0) {
      renderEmptyState();
      return;
    }

    allData = [];
    const failExampleCount = {};
    let totalPassed = 0;
    let totalFailed = 0;

    for (const file of files.reverse()) {
      const filePath = `${serverIP}/report/summary/${file}`;
      try {
        const jsonData = await fetch(filePath);
        const parsedData = await jsonData.json();

        const summarySum = parsedData.sum || 0;
        const summaryPassed = parsedData.passed || 0;
        const summaryFailed = summarySum - summaryPassed;
        const summaryPassRate = summarySum > 0 ? (summaryPassed / summarySum) * 100 : 0;
        const summaryState = summaryPassRate === 100 ? 'pass' : 'fail';

        // 统计失败用例
        if (parsedData.failExample && Array.isArray(parsedData.failExample)) {
          parsedData.failExample.forEach(example => {
            failExampleCount[example] = (failExampleCount[example] || 0) + 1;
          });
        }

        totalPassed += summaryPassed;
        totalFailed += summaryFailed;

        allData.push({
          name: parsedData.name,
          passRate: summaryPassRate,
          passed: summaryPassed,
          failed: summaryFailed,
          total: summarySum,
          status: summaryState,
          formattedTime: formatTime(parsedData.name)
        });
      } catch (err) {
        console.error(`读取文件 ${file} 出错:`, err);
      }
    }

    if (allData.length > 0) {
      updateStatsCards();
      renderTable();
      renderCharts(failExampleCount);
    } else {
      renderEmptyState();
    }

  } catch (err) {
    console.error('加载数据失败:', err);
    renderEmptyState();
  }
}

// 更新统计卡片
function updateStatsCards() {
  // 总测试次数 = 测试运行次数
  const totalRuns = allData.length;

  // 总测试成功数 = 通过的测试运行次数 (passRate === 100%)
  const totalPassed = allData.filter(d => d.status === 'pass').length;

  // 总测试失败数 = 存在失败的测试运行次数
  const totalFailed = allData.filter(d => d.status === 'fail').length;

  // 总测试通过率 = 成功次数 / 总次数
  const totalPassRate = totalRuns > 0 ? (totalPassed / totalRuns) * 100 : 0;

  // 总测试次数
  document.getElementById('totalRuns').textContent = totalRuns;

  // 总测试成功数
  document.getElementById('totalPassed').textContent = totalPassed;

  // 总测试失败数
  document.getElementById('totalFailed').textContent = totalFailed;

  // 总测试通过率
  document.getElementById('totalPassRate').textContent = `${totalPassRate.toFixed(1)}%`;
}

// 渲染表格
function renderTable(filterText = '') {
  const tbody = document.getElementById('tableBody');
  const filteredData = allData.filter(item =>
    item.formattedTime.toLowerCase().includes(filterText.toLowerCase()) ||
    item.name.toLowerCase().includes(filterText.toLowerCase())
  );

  // 排序
  filteredData.sort((a, b) => {
    let aVal = a[currentSort.column];
    let bVal = b[currentSort.column];

    if (currentSort.column === 'name') {
      aVal = a.formattedTime;
      bVal = b.formattedTime;
    }

    if (typeof aVal === 'number') {
      return currentSort.direction === 'asc' ? aVal - bVal : bVal - aVal;
    }
    return currentSort.direction === 'asc'
      ? String(aVal).localeCompare(String(bVal))
      : String(bVal).localeCompare(String(aVal));
  });

  tbody.innerHTML = filteredData.map(item => `
    <tr>
      <td>
        <div style="font-weight: 500;">${item.formattedTime}</div>
        <div class="last-run">${item.name}</div>
      </td>
      <td>
        <div class="progress-cell">
          <div class="progress-bar">
            <div class="fill ${item.passRate >= 80 ? 'high' : item.passRate >= 60 ? 'medium' : 'low'}"
                 style="width: ${item.passRate}%"></div>
          </div>
          <div class="progress-text">${item.passRate.toFixed(1)}%</div>
        </div>
      </td>
      <td style="color: #00ff88;">${item.passed}</td>
      <td style="color: #ff4757;">${item.failed}</td>
      <td>${item.total}</td>
      <td>
        <span class="status-badge ${item.status}">${item.status === 'pass' ? '通过' : '失败'}</span>
      </td>
      <td>
        <button class="btn btn-primary" onclick="openDetailReport('${item.name}')">
          查看详情
        </button>
      </td>
    </tr>
  `).join('');
}

// 渲染图表
function renderCharts(failExampleCount) {
  renderPassRateChart();
  renderFailCasesChart(failExampleCount);
  renderTrendChart();
}

// 渲染通过率分布图
function renderPassRateChart() {
  const passCount = allData.filter(d => d.status === 'pass').length;
  const failCount = allData.length - passCount;

  const ctx = document.getElementById('passRateChart').getContext('2d');

  if (passRateChart) passRateChart.destroy();

  passRateChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['全部通过', '存在失败'],
      datasets: [{
        data: [passCount, failCount],
        backgroundColor: ['#00ff88', '#ff4757'],
        borderWidth: 0,
        hoverOffset: 20
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: '#8892b0',
            padding: 20,
            font: { size: 12 }
          }
        }
      }
    }
  });
}

// 渲染失败用例图
function renderFailCasesChart(failExampleCount) {
  const sortedEntries = Object.entries(failExampleCount)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10);

  const ctx = document.getElementById('failCasesChart').getContext('2d');

  if (failCasesChart) failCasesChart.destroy();

  const colors = sortedEntries.map((_, i) =>
    `hsl(${(i * 360 / Math.max(sortedEntries.length, 1))}, 70%, 55%)`
  );

  failCasesChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: sortedEntries.map(e => e[0]),
      datasets: [{
        label: '失败次数',
        data: sortedEntries.map(e => e[1]),
        backgroundColor: colors,
        borderRadius: 6,
        maxBarThickness: 35
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          beginAtZero: true,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: { color: '#8892b0' }
        },
        y: {
          grid: { display: false },
          ticks: { color: '#8892b0', font: { size: 11 } }
        }
      }
    }
  });
}

// 渲染趋势图
function renderTrendChart() {
  const ctx = document.getElementById('trendChart').getContext('2d');

  if (trendChart) trendChart.destroy();

  const sortedData = [...allData].sort((a, b) => a.name.localeCompare(b.name));
  const labels = sortedData.map(d => d.formattedTime);
  const passRates = sortedData.map(d => d.passRate);

  trendChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: '通过率',
        data: passRates,
        borderColor: '#00d9ff',
        backgroundColor: 'rgba(0, 217, 255, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#00d9ff'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: {
            color: '#8892b0',
            maxTicksLimit: 10,
            font: { size: 10 }
          }
        },
        y: {
          min: 0,
          max: 100,
          grid: { color: 'rgba(255,255,255,0.05)' },
          ticks: {
            color: '#8892b0',
            callback: v => v + '%'
          }
        }
      },
      interaction: {
        intersect: false,
        mode: 'index'
      }
    }
  });
}

// 打开详细报告
function openDetailReport(name) {
  window.open(`./detail.html?name=${name}`, '_blank');
}

// 渲染空状态
function renderEmptyState() {
  document.getElementById('tableBody').innerHTML = `
    <tr>
      <td colspan="7" class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <h3>暂无测试数据</h3>
        <p>执行测试后将自动生成报告</p>
      </td>
    </tr>
  `;
}

// 排序功能
function setupSorting() {
  document.querySelectorAll('th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const column = th.dataset.sort;
      if (currentSort.column === column) {
        currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
      } else {
        currentSort.column = column;
        currentSort.direction = 'desc';
      }

      document.querySelectorAll('th[data-sort]').forEach(h => {
        h.classList.remove('sorted-asc', 'sorted-desc');
      });
      th.classList.add(`sorted-${currentSort.direction}`);

      renderTable(document.getElementById('searchInput').value);
    });
  });
}

// 搜索功能
function setupSearch() {
  const input = document.getElementById('searchInput');
  input.addEventListener('input', (e) => {
    renderTable(e.target.value);
  });
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
  loadAllData();
  setupSorting();
  setupSearch();
});
