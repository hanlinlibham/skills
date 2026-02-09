# WindPy 字段验证报告

**验证时间**: 2026-02-09
**验证方式**: 通过 WindPy API 实际测试

---

## 已验证字段

### ✅ 行情字段 (通过验证)

| 字段 | 状态 | 说明 |
|------|------|------|
| `close` | ✅ | 收盘价 |
| `open` | ✅ | 开盘价 |
| `high` | ✅ | 最高价 |
| `low` | ✅ | 最低价 |
| `volume` | ✅ | 成交量 |
| `amt` | ✅ | 成交额 |
| `pct_chg` | ✅ | 涨跌幅 |

**测试代码**:
```python
err, df = w.wsd("600519.SH", "close,open,high,low,volume,amt,pct_chg", "-5D", "", "", usedf=True)
# 返回: ['CLOSE', 'OPEN', 'HIGH', 'LOW', 'VOLUME', 'AMT', 'PCT_CHG']
```

---

### ✅ 估值字段 (通过验证)

| 字段 | 状态 | 说明 |
|------|------|------|
| `pe_ttm` | ✅ | 市盈率(TTM) |
| `pb_lf` | ✅ | 市净率(LF) |
| `ps_ttm` | ✅ | 市销率(TTM) |
| `mkt_cap_ard` | ✅ | 总市值 |

**测试代码**:
```python
err, df = w.wss("600519.SH", "pe_ttm,pb_lf,ps_ttm,mkt_cap_ard", "tradeDate=20260209", usedf=True)
# 返回: ['PE_TTM', 'PB_LF', 'PS_TTM', 'MKT_CAP_ARD']
```

**注意**: 非交易日可能返回 None

---

### ⚠️ 资金流向字段 (需要权限)

| 字段 | 状态 | 说明 |
|------|------|------|
| `mfd_inflow_xl` | ⚠️ | 超大单净流入 (需权限) |
| `mfd_inflow_l` | ⚠️ | 大单净流入 (需权限) |
| `mfd_inflow_m` | ⚠️ | 中单净流入 (需权限) |
| `mfd_inflow_s` | ⚠️ | 小单净流入 (需权限) |

**测试代码**:
```python
err, df = w.wsd("600519.SH", "mfd_inflow_xl,mfd_inflow_l,mfd_inflow_m,mfd_inflow_s", "-5D", "", "", usedf=True)
# 返回错误: -40522007 (需要开通权限)
```

**解决方案**: 联系 Wind 客服开通资金流向数据权限

---

### ✅ 技术指标 (通过验证)

| 字段 | 状态 | 说明 |
|------|------|------|
| `MACD` | ✅ | MACD指标 |
| `RSI` | ✅ | RSI相对强弱 |
| `KDJ` | ✅ | KDJ随机指标 |

**测试代码**:
```python
err, df = w.wsd("600519.SH", "MACD,RSI,KDJ", "-10D", "", "", usedf=True)
# 返回: ['MACD', 'RSI', 'KDJ']
```

---

### ✅ 板块/指数代码 (通过验证)

| 板块 | 代码 | 数量 | 状态 |
|------|------|------|------|
| 全部A股 | a001010100000000 | 5,479只 | ✅ |
| 沪深300 | 000300.SH | 300只 | ✅ |
| 中证500 | 000905.SH | 500只 | ✅ |
| 申万三级行业 | a39901011i000000 | 259个 | ✅ |

**测试代码**:
```python
# 全部A股
result = w.wset("sectorconstituent", "date=20260209;sectorid=a001010100000000")
# 返回: 5,479 只股票

# 沪深300
result = w.wset("sectorconstituent", "date=20260209;windcode=000300.SH")
# 返回: 300 只股票
```

---

## 使用建议

### 1. 基础字段 (无需特殊权限)
- 行情字段: `close`, `open`, `high`, `low`, `volume`, `amt`, `pct_chg`
- 估值字段: `pe_ttm`, `pb_lf`, `ps_ttm`, `mkt_cap_ard`
- 技术指标: `MACD`, `RSI`, `KDJ`, `BOLL`, `CCI`, `WR`

### 2. 需要权限的字段
- 资金流向: `mfd_inflow_*` (需开通权限)
- 实时行情: `rt_*` (需实时行情权限)
- Tick数据: (需Level 2权限)

### 3. 验证方法
```python
# 测试单个字段
err, df = w.wsd("600519.SH", "close", "-1D", "", "", usedf=True)
if err == 0:
    print(f"字段可用: {list(df.columns)}")
else:
    print(f"字段错误或需要权限: {err}")
```

---

## 数据覆盖范围 (已验证)

| 数据类型 | 数量 | 验证状态 |
|----------|------|----------|
| A股总数 | 5,479只 | ✅ |
| 沪深300成分股 | 300只 | ✅ |
| 中证500成分股 | 500只 | ✅ |
| 申万三级行业 | 259个 | ✅ |

---

## 注意事项

1. **列名大写**: 使用 `usedf=True` 时，返回的 DataFrame 列名自动转为大写
2. **非交易日**: 非交易日部分字段可能返回 None
3. **数据权限**: 部分高级字段（如资金流向）需要额外开通权限
4. **字段拼写**: WindPy 字段名不区分大小写，但建议统一使用小写

---

**验证结论**: 常用字段均可正常使用，资金流向等高级字段需要开通权限。
