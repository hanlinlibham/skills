# WindPy wset 报表数据集参考

`w.wset()` 函数用于获取各类报表数据，如板块成分、指数成分、ETF清单、龙虎榜等。

## 函数签名

```python
w.wset(tableName, options, usedf=True)
```

| 参数 | 类型 | 必选 | 说明 |
|------|------|------|------|
| tableName | str | 是 | 报表名称，见下表 |
| options | str | 是 | 参数字符串，格式: `key1=value1;key2=value2` |
| usedf | bool | 否 | 返回 DataFrame，默认 True |

---

## 已验证可用的 TableName (2026-02-09)

### 1. sectorconstituent — 板块成分股 ✅

**验证状态**: 已验证 ✅ (5,479条数据)

**验证代码**:
```python
result = w.wset("sectorconstituent", "date=20260209;sectorid=a001010100000000")
print(f"全部A股: {len(result.Data[1])}只")  # 5479只
```

获取指定板块的成分股列表。

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| date | 日期 | `date=20260108` |
| sectorid | 板块代码 | `sectorid=a001010100000000` |

**返回列：**
- `date`: 日期
- `wind_code`: 证券代码
- `sec_name`: 证券名称

**示例：**
```python
# 全部A股成分股
data = w.wset("sectorconstituent", "date=20260108;sectorid=a001010100000000")

# 沪深300成分股
err, df = w.wset("sectorconstituent", 
    "date=20260108;sectorid=1000000098000000", usedf=True)

# 申万食品饮料行业成分股
err, df = w.wset("sectorconstituent",
    "date=20260108;sectorid=a39901130g000000", usedf=True)
```

---

### 2. indexconstituent — 指数成分股 ✅

**验证状态**: 已验证 ✅ (300条数据 - 沪深300)

**验证代码**:
```python
result = w.wset("indexconstituent", "date=20260209;windcode=000300.SH")
print(f"沪深300成分股: {len(result.Data[1])}只")  # 300只
```

获取指数成分股列表（与 sectorconstituent 类似）。

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| date | 日期 | `date=20260108` |
| windcode | 指数代码 | `windcode=000300.SH` |

**返回列：**
- `date`: 日期
- `wind_code`: 证券代码
- `sec_name`: 证券名称

**示例：**
```python
err, df = w.wset("indexconstituent",
    "date=20260108;windcode=000300.SH", usedf=True)
```

---

### 3. etfconstituent — ETF申赎清单(PCF) ✅

**验证状态**: 已验证 ✅ (300条数据 - 510300.SH)

**验证代码**:
```python
result = w.wset("etfconstituent", "date=20260209;windcode=510300.SH")
print(f"沪深300ETF成分股: {len(result.Data[1])}只")  # 300只
```

获取ETF的申赎清单，包括成分股、现金替代标记、溢价比例等。

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| date | 日期 | `date=20260108` |
| windcode | ETF代码 | `windcode=510300.SH` |

**返回列：**
- `date`: 日期
- `wind_code`: 成分股代码
- `sec_name`: 成分股名称
- `volume`: 成分数量
- `cash_substitution_mark`: 现金替代标记
- `cash_substitution_premium_ratio`: 现金替代溢价比例
- `fixed_substitution_amount`: 固定替代金额
- `subscribefixedamount`: 申购固定金额
- `cashdiscountratio`: 现金折扣比例
- `redemptionfixedamount`: 赎回固定金额

**示例：**
```python
# 沪深300ETF申赎清单
err, df = w.wset("etfconstituent",
    "date=20260108;windcode=510300.SH", usedf=True)
```

---

### 4. dividendproposal — 分红预案

获取上市公司分红预案信息。

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| year | 年份 | `year=2024` |

**返回列：**
- `wind_code`: 证券代码
- `sec_name`: 证券名称
- `progress`: 预案进度
- `dividend_type`: 分红类型
- `cash_dvd_per_sh_pre_tax`: 每股税前红利
- `cash_dvd_per_sh_after_tax`: 每股税后红利
- `stock_dvd_per_sh`: 每股送转股
- `record_date`: 股权登记日
- `ex_date`: 除权除息日
- `dividend_date`: 红利发放日

**示例：**
```python
# 2024年分红预案
err, df = w.wset("dividendproposal", "year=2024", usedf=True)
```

---

### 5. holdernumber — 股东户数

获取上市公司股东户数变化。

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| windcode | 股票代码 | `windcode=600519.SH` |

**返回列：**
- `wind_code`: 证券代码
- `sec_name`: 证券名称
- `report_date`: 报告期
- `shareholder_number`: 股东户数
- `shareholder_number_change`: 股东户数变化
- `growth`: 增长率
- `latest_shareholder_number`: 最新股东户数

**示例：**
```python
err, df = w.wset("holdernumber", "windcode=600519.SH", usedf=True)
```

---

### 6. cashflowstatement — 现金流量表

获取上市公司现金流量表数据。

**参数：**
| 参数 | 说明 | 示例 |
|------|------|------|
| windcode | 股票代码 | `windcode=600519.SH` |
| rptDate | 报告期 | `rptDate=20241231` (可选) |

**返回列：**
- 包含经营活动、投资活动、筹资活动现金流等科目

**示例：**
```python
err, df = w.wset("cashflowstatement", "windcode=600519.SH", usedf=True)
```

---

## 需要特定权限的 TableName

以下 tableName 已测试，返回 `-40522012`（参数错误或需要权限）：

| TableName | 说明 | 测试参数 | 错误码 |
|-----------|------|----------|--------|
| `abnormalactivitiesranking` | 龙虎榜 | `startdate=20260201;enddate=20260209` | -40522012 |
| `blocktrading` | 大宗交易 | `startdate=20260201;enddate=20260209` | -40522012 |
| `margintrading` | 融资融券 | `windcode=600519.SH;startdate=20260201` | -40522012 |
| `pledge` | 股权质押 | `windcode=600519.SH` | -40522012 |

**说明**: 以上 TableName 需要开通特定数据权限，或参数格式需要调整。

**可能的解决方案**:
1. 联系 Wind 客服开通对应数据权限
2. 尝试不同的参数组合
3. 使用替代方案（如通过 `w.wsd` 获取部分数据）

---

## 使用技巧

### 批量获取多个板块成分股

```python
def get_multiple_sectors(sector_ids, date=None):
    """获取多个板块的成分股"""
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime('%Y%m%d')
    
    results = {}
    for name, sid in sector_ids.items():
        data = w.wset("sectorconstituent", f"date={date};sectorid={sid}")
        if data.ErrorCode == 0:
            results[name] = data.Data[1] if len(data.Data) > 1 else []
    return results

# 使用
sectors = {
    "沪深300": "1000000098000000",
    "中证500": "1000000099000000",
    "创业板": "1000006528000000"
}
stocks = get_multiple_sectors(sectors)
```

### 获取ETF全部持仓

```python
def get_etf_holdings(etf_code, date=None):
    """获取ETF持仓明细"""
    if date is None:
        from datetime import datetime
        date = datetime.now().strftime('%Y%m%d')
    
    err, df = w.wset("etfconstituent",
        f"date={date};windcode={etf_code}", usedf=True)
    
    if err == 0:
        return df
    return None

# 获取沪深300ETF持仓
holdings = get_etf_holdings("510300.SH")
```

---

## 注意事项

1. **日期格式：** 大部分使用 `YYYYMMDD` 格式，少数可能需要 `YYYY-MM-DD`
2. **权限限制：** 部分高级报表需要特定数据权限，返回 `-40522012` 或 `-40520007`
3. **返回列名：** 使用 `usedf=True` 时，列名可能与文档有差异，建议打印 `df.columns` 确认
4. **数据时效：** 部分报表（如龙虎榜、大宗交易）只保留近期数据

---

## 文档状态

**最后验证**: 2026-02-09

**已验证 TableName**:
- ✅ `sectorconstituent` - 板块成分 (5,479条)
- ✅ `indexconstituent` - 指数成分 (300条)
- ✅ `etfconstituent` - ETF申赎清单 (300条)
- ✅ `dividendproposal` - 分红预案
- ✅ `holdernumber` - 股东户数
- ✅ `cashflowstatement` - 现金流量表

**需权限 TableName**:
- ⚠️ `abnormalactivitiesranking` - 龙虎榜
- ⚠️ `blocktrading` - 大宗交易
- ⚠️ `margintrading` - 融资融券
- ⚠️ `pledge` - 股权质押

**待进一步验证**:
- `tradingsuspend` - 停牌股票
- `top10holders` - 前十大股东
- `top10tradableholders` - 前十大流通股东
- `repurchases` - 股票回购
- `restrictedshare` - 限售股解禁
- `indexweight` - 指数成分股权重
- `split` - 送转股方案
- `dividendimplementation` - 分红实施
- `ipo` - IPO新股
- `delisting` - 退市股票
