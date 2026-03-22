# Financial Layouts Reference

金融演示专用页面布局。每种布局都遵循 viewport fitting 规范，所有尺寸使用 `clamp()`。

---

## 1. KPI Dashboard (关键指标仪表盘)

适用于：业绩概览、核心指标展示、投资亮点

```html
<section class="slide kpi-slide">
    <div class="slide-content">
        <h2 class="reveal">核心业绩指标</h2>
        <p class="reveal slide-subtitle">2024年度 / 单位：人民币</p>
        <div class="kpi-grid reveal">
            <div class="kpi-card">
                <span class="kpi-label">营业收入</span>
                <span class="kpi-value" data-count="2340000000">23.4亿</span>
                <span class="kpi-trend positive">+18.2% YoY</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">净利润</span>
                <span class="kpi-value" data-count="580000000">5.8亿</span>
                <span class="kpi-trend positive">+22.5% YoY</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">毛利率</span>
                <span class="kpi-value">42.3%</span>
                <span class="kpi-trend positive">+2.1pp</span>
            </div>
            <div class="kpi-card">
                <span class="kpi-label">ROE</span>
                <span class="kpi-value">16.8%</span>
                <span class="kpi-trend negative">-0.5pp</span>
            </div>
        </div>
    </div>
</section>
```

```css
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 200px), 1fr));
    gap: clamp(0.75rem, 2vw, 1.5rem);
    margin-top: clamp(1rem, 3vh, 2rem);
}

.kpi-card {
    background: var(--card-bg, rgba(255, 255, 255, 0.05));
    border: 1px solid var(--border-color, rgba(0, 0, 0, 0.08));
    border-radius: clamp(6px, 1vw, 12px);
    padding: clamp(0.75rem, 2vw, 1.5rem);
    display: flex;
    flex-direction: column;
    gap: clamp(0.25rem, 0.5vh, 0.5rem);
}

.kpi-label {
    font-size: clamp(0.65rem, 1vw, 0.85rem);
    color: var(--text-secondary);
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.kpi-value {
    font-size: clamp(1.5rem, 3.5vw, 2.5rem);
    font-weight: 700;
    font-family: var(--font-display);
    color: var(--text-primary);
    line-height: 1.1;
}

.kpi-trend {
    font-size: clamp(0.6rem, 0.9vw, 0.8rem);
    font-weight: 500;
}

.kpi-trend.positive { color: var(--color-positive, #16a34a); }
.kpi-trend.negative { color: var(--color-negative, #dc2626); }
.kpi-trend.neutral  { color: var(--text-secondary); }

/* A股惯例：涨为红、跌为绿。如需切换，覆盖以下变量 */
/* --color-positive: #dc2626; --color-negative: #16a34a; */
```

### KPI 计数动画

```javascript
class KPICounter {
    constructor(el) {
        this.el = el;
        this.target = parseFloat(el.dataset.count) || 0;
        this.duration = 1200;
    }

    animate() {
        const start = performance.now();
        const step = (now) => {
            const progress = Math.min((now - start) / this.duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3); // ease-out-cubic
            const current = this.target * eased;
            this.el.textContent = formatCN(current);
            if (progress < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
    }
}

// 在 IntersectionObserver 回调中触发
entry.target.querySelectorAll('.kpi-value[data-count]').forEach(el => {
    new KPICounter(el).animate();
});
```

---

## 2. Data Table (数据表格)

适用于：财务数据对比、同业比较、历史趋势

```html
<section class="slide table-slide">
    <div class="slide-content">
        <h2 class="reveal">财务数据摘要</h2>
        <div class="table-wrapper reveal">
            <table class="data-table">
                <thead>
                    <tr>
                        <th class="col-label">指标</th>
                        <th class="col-num">2022A</th>
                        <th class="col-num">2023A</th>
                        <th class="col-num">2024A</th>
                        <th class="col-num highlight">2025E</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>营业收入(亿)</td>
                        <td class="num">156.3</td>
                        <td class="num">189.7</td>
                        <td class="num">234.0</td>
                        <td class="num highlight">278.5</td>
                    </tr>
                    <tr>
                        <td>净利润(亿)</td>
                        <td class="num">38.2</td>
                        <td class="num">47.5</td>
                        <td class="num">58.0</td>
                        <td class="num highlight">69.2</td>
                    </tr>
                    <tr>
                        <td>毛利率(%)</td>
                        <td class="num">39.1</td>
                        <td class="num">40.8</td>
                        <td class="num">42.3</td>
                        <td class="num highlight">43.5</td>
                    </tr>
                    <tr>
                        <td>EPS(元)</td>
                        <td class="num">2.15</td>
                        <td class="num">2.68</td>
                        <td class="num">3.27</td>
                        <td class="num highlight">3.90</td>
                    </tr>
                    <tr class="separator">
                        <td>PE(倍)</td>
                        <td class="num">28.5</td>
                        <td class="num">24.3</td>
                        <td class="num">21.1</td>
                        <td class="num highlight">17.7</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <p class="reveal table-note">数据来源：公司年报、券商一致预期 | E = 预测值</p>
    </div>
</section>
```

```css
.table-wrapper {
    overflow-x: auto;
    margin-top: clamp(0.75rem, 2vh, 1.5rem);
    -webkit-overflow-scrolling: touch;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: clamp(0.7rem, 1.2vw, 0.95rem);
    font-family: var(--font-body);
}

.data-table th {
    font-size: clamp(0.6rem, 1vw, 0.8rem);
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--text-secondary);
    padding: clamp(0.4rem, 1vh, 0.75rem) clamp(0.5rem, 1.5vw, 1rem);
    border-bottom: 2px solid var(--border-color, rgba(0, 0, 0, 0.15));
    text-align: left;
}

.data-table th.col-num,
.data-table td.num {
    text-align: right;
    font-variant-numeric: tabular-nums;
}

.data-table td {
    padding: clamp(0.35rem, 0.8vh, 0.6rem) clamp(0.5rem, 1.5vw, 1rem);
    border-bottom: 1px solid var(--border-color, rgba(0, 0, 0, 0.06));
    color: var(--text-primary);
}

.data-table tbody tr:hover {
    background: var(--row-hover, rgba(0, 0, 0, 0.02));
}

.data-table .highlight {
    color: var(--accent);
    font-weight: 600;
}

.data-table .separator td {
    border-top: 2px solid var(--border-color, rgba(0, 0, 0, 0.1));
}

.table-note {
    font-size: clamp(0.55rem, 0.8vw, 0.7rem);
    color: var(--text-secondary);
    margin-top: clamp(0.5rem, 1vh, 0.75rem);
    opacity: 0.7;
}

/* 深色主题表格适配 */
@media (prefers-color-scheme: dark) {
    .data-table th { border-bottom-color: rgba(255, 255, 255, 0.15); }
    .data-table td { border-bottom-color: rgba(255, 255, 255, 0.06); }
    .data-table tbody tr:hover { background: rgba(255, 255, 255, 0.03); }
}
```

### 内容密度规范

| 表格类型 | 最大行数 | 最大列数 |
|----------|---------|---------|
| 财务摘要 | 6-8 行 | 5-6 列 |
| 同业对比 | 4-6 行 | 6-7 列 |
| 估值对比 | 5-6 行 | 4-5 列 |

**超出限制时拆分为多个 slide，不要压缩字号。**

---

## 3. Timeline (时间线)

适用于：公司发展历程、项目里程碑、政策演变

```html
<section class="slide timeline-slide">
    <div class="slide-content">
        <h2 class="reveal">发展里程碑</h2>
        <div class="timeline reveal">
            <div class="timeline-item">
                <span class="timeline-date">2018</span>
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <h4>成立与首轮融资</h4>
                    <p>完成A轮融资2亿元，核心团队组建完成</p>
                </div>
            </div>
            <div class="timeline-item">
                <span class="timeline-date">2020</span>
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <h4>产品商业化</h4>
                    <p>首款产品上市，当年营收突破5000万</p>
                </div>
            </div>
            <div class="timeline-item">
                <span class="timeline-date">2023</span>
                <div class="timeline-dot"></div>
                <div class="timeline-content">
                    <h4>IPO上市</h4>
                    <p>科创板上市，市值突破100亿</p>
                </div>
            </div>
            <div class="timeline-item">
                <span class="timeline-date">2025E</span>
                <div class="timeline-dot active"></div>
                <div class="timeline-content">
                    <h4>全球化布局</h4>
                    <p>海外营收占比目标达30%</p>
                </div>
            </div>
        </div>
    </div>
</section>
```

```css
.timeline {
    display: flex;
    flex-direction: column;
    gap: clamp(0.5rem, 1.5vh, 1.25rem);
    margin-top: clamp(0.75rem, 2vh, 1.5rem);
    padding-left: clamp(3rem, 8vw, 6rem);
    position: relative;
}

/* 纵轴线 */
.timeline::before {
    content: '';
    position: absolute;
    left: clamp(1.2rem, 3.5vw, 2.5rem);
    top: 0;
    bottom: 0;
    width: 2px;
    background: var(--border-color, rgba(0, 0, 0, 0.12));
}

.timeline-item {
    position: relative;
    display: flex;
    align-items: flex-start;
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

.timeline-date {
    position: absolute;
    left: calc(-1 * clamp(3rem, 8vw, 6rem));
    width: clamp(2.5rem, 7vw, 5rem);
    font-size: clamp(0.65rem, 1vw, 0.85rem);
    font-weight: 700;
    color: var(--accent);
    text-align: right;
    padding-top: 0.15em;
}

.timeline-dot {
    position: absolute;
    left: calc(-1 * clamp(3rem, 8vw, 6rem) + clamp(2.7rem, 7.3vw, 5.3rem));
    width: clamp(8px, 1vw, 12px);
    height: clamp(8px, 1vw, 12px);
    border-radius: 50%;
    background: var(--accent);
    border: 2px solid var(--bg-primary, #fff);
    box-shadow: 0 0 0 2px var(--accent);
    flex-shrink: 0;
    margin-top: 0.3em;
}

.timeline-dot.active {
    box-shadow: 0 0 0 2px var(--accent), 0 0 0 5px rgba(var(--accent-rgb, 37, 99, 235), 0.2);
}

.timeline-content h4 {
    font-size: clamp(0.8rem, 1.3vw, 1.05rem);
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: clamp(0.15rem, 0.3vh, 0.3rem);
}

.timeline-content p {
    font-size: clamp(0.65rem, 1vw, 0.85rem);
    color: var(--text-secondary);
    line-height: 1.4;
}

/* 时间线最多 4-5 个节点 */
```

---

## 4. Comparison (对比分析)

适用于：可比公司、方案对比、产品差异

```html
<section class="slide comparison-slide">
    <div class="slide-content">
        <h2 class="reveal">可比公司估值对比</h2>
        <div class="comparison-grid reveal">
            <div class="comp-card featured">
                <div class="comp-header">
                    <h3>标的公司</h3>
                    <span class="comp-tag">当前持仓</span>
                </div>
                <div class="comp-metrics">
                    <div class="comp-row"><span>PE (TTM)</span><strong>21.3x</strong></div>
                    <div class="comp-row"><span>PB</span><strong>3.8x</strong></div>
                    <div class="comp-row"><span>ROE</span><strong>18.2%</strong></div>
                    <div class="comp-row"><span>营收增速</span><strong>+23.4%</strong></div>
                </div>
            </div>
            <div class="comp-card">
                <div class="comp-header"><h3>可比A</h3></div>
                <div class="comp-metrics">
                    <div class="comp-row"><span>PE (TTM)</span><strong>25.1x</strong></div>
                    <div class="comp-row"><span>PB</span><strong>4.2x</strong></div>
                    <div class="comp-row"><span>ROE</span><strong>16.5%</strong></div>
                    <div class="comp-row"><span>营收增速</span><strong>+15.8%</strong></div>
                </div>
            </div>
            <div class="comp-card">
                <div class="comp-header"><h3>可比B</h3></div>
                <div class="comp-metrics">
                    <div class="comp-row"><span>PE (TTM)</span><strong>18.7x</strong></div>
                    <div class="comp-row"><span>PB</span><strong>2.9x</strong></div>
                    <div class="comp-row"><span>ROE</span><strong>15.1%</strong></div>
                    <div class="comp-row"><span>营收增速</span><strong>+11.2%</strong></div>
                </div>
            </div>
        </div>
    </div>
</section>
```

```css
.comparison-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
    gap: clamp(0.75rem, 2vw, 1.5rem);
    margin-top: clamp(0.75rem, 2vh, 1.5rem);
}

.comp-card {
    background: var(--card-bg, rgba(0, 0, 0, 0.02));
    border: 1px solid var(--border-color, rgba(0, 0, 0, 0.08));
    border-radius: clamp(6px, 1vw, 12px);
    padding: clamp(0.75rem, 2vw, 1.5rem);
}

.comp-card.featured {
    border-color: var(--accent);
    border-width: 2px;
    background: var(--card-bg-featured, rgba(var(--accent-rgb, 37, 99, 235), 0.04));
}

.comp-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: clamp(0.5rem, 1vh, 0.75rem);
    padding-bottom: clamp(0.4rem, 0.8vh, 0.6rem);
    border-bottom: 1px solid var(--border-color, rgba(0, 0, 0, 0.08));
}

.comp-header h3 {
    font-size: clamp(0.85rem, 1.3vw, 1.1rem);
    font-weight: 700;
    color: var(--text-primary);
}

.comp-tag {
    font-size: clamp(0.5rem, 0.7vw, 0.65rem);
    background: var(--accent);
    color: var(--bg-primary, #fff);
    padding: 0.15em 0.5em;
    border-radius: 3px;
    font-weight: 500;
}

.comp-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: clamp(0.25rem, 0.5vh, 0.4rem) 0;
    font-size: clamp(0.65rem, 1vw, 0.85rem);
}

.comp-row span { color: var(--text-secondary); }
.comp-row strong {
    color: var(--text-primary);
    font-variant-numeric: tabular-nums;
}

/* 最多 3 列对比卡片，每卡片 4-5 行指标 */
```

---

## 5. Chart + Text Split (图文分栏)

适用于：数据解读、趋势分析配说明

```html
<section class="slide split-chart-slide">
    <div class="slide-content">
        <div class="split-layout">
            <div class="split-text reveal">
                <h2>营收持续高增长</h2>
                <ul class="insight-list">
                    <li><strong>收入增速 23.4%</strong>，连续4年保持20%+增长</li>
                    <li>核心产品市占率提升至 <strong>18.5%</strong></li>
                    <li>海外业务贡献 <strong>12%</strong> 增量</li>
                </ul>
            </div>
            <div class="split-chart reveal">
                <div class="chart-container" id="revenueChart"></div>
            </div>
        </div>
    </div>
</section>
```

```css
.split-layout {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: clamp(1rem, 3vw, 2.5rem);
    align-items: center;
    height: 100%;
}

.split-text h2 {
    font-size: clamp(1.2rem, 2.8vw, 2rem);
    margin-bottom: clamp(0.5rem, 1.5vh, 1rem);
}

.insight-list {
    list-style: none;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: clamp(0.4rem, 1vh, 0.75rem);
}

.insight-list li {
    font-size: clamp(0.75rem, 1.2vw, 1rem);
    line-height: 1.5;
    color: var(--text-secondary);
    padding-left: clamp(0.75rem, 1.5vw, 1.25rem);
    position: relative;
}

.insight-list li::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0.55em;
    width: clamp(4px, 0.5vw, 6px);
    height: clamp(4px, 0.5vw, 6px);
    border-radius: 50%;
    background: var(--accent);
}

.insight-list li strong {
    color: var(--text-primary);
    font-weight: 600;
}

/* 窄屏堆叠 */
@media (max-width: 768px) {
    .split-layout {
        grid-template-columns: 1fr;
    }
}
```

---

## 布局选择指南

| 页面用途 | 推荐布局 | 最大内容量 |
|----------|---------|-----------|
| 业绩概览 | KPI Dashboard | 4-6 个指标卡片 |
| 财务数据 | Data Table | 8 行 x 6 列 |
| 发展历程 | Timeline | 4-5 个节点 |
| 同业对比 | Comparison | 3 列 x 5 行指标 |
| 趋势解读 | Chart + Text Split | 1 图 + 3-4 条要点 |
| 收入拆解 | Chart (全幅) | 1 个图表 + 标题 |
| 投资亮点 | KPI + 简述 | 3-4 个亮点 |

**内容超限时拆分为多个 slide。绝对不要缩小字号或减少间距来容纳更多内容。**
