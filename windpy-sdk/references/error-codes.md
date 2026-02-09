# WindPy 错误码参考

WindPy 函数返回的错误码及解决方案。

## 错误码列表

### 成功

| 错误码 | 含义 | 说明 |
|--------|------|------|
| `0` | 成功 | 数据获取成功 |

### 常见错误

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `-40520007` | 无数据权限 | 需要开通对应数据权限 |
| `-40520017` | 字段不支持 | Mac 版 SDK 部分字段不可用，请使用 Windows 版 |
| `-40522006` | 参数错误 | 检查参数名和参数值格式是否正确 |
| `-40522012` | 参数错误/需要参数 | 该 tableName 需要更多参数，或参数格式不正确 |
| `-40521001` | 网络连接失败 | 检查网络连接，或 Wind 终端是否登录 |
| `-40520008` | 请求超时 | 减少请求数据量，或增加超时时间 |
| `-40520010` | 数据不存在 | 该日期/品种无数据 |

### 连接相关

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `-40520001` | 未连接 | 调用 `w.start()` 建立连接 |
| `-40520002` | 连接断开 | 重新调用 `w.start()` |
| `-40520003` | 连接超时 | 检查网络或增加 `waitTime` 参数 |
| `-40520004` | 已在连接中 | 无需重复连接 |

### 数据相关

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `-40520005` | 数据为空 | 检查日期范围或品种代码 |
| `-40520006` | 数据超限 | 减少请求的数据量 |
| `-40520009` | 历史数据不存在 | 该日期范围无历史数据 |
| `-40520011` | 实时数据未开始 | 当前时间非交易时间 |
| `-40520013` | 数据权限过期 | 联系 Wind 客服续费 |

### 代码/字段相关

| 错误码 | 含义 | 解决方案 |
|--------|------|----------|
| `-40520014` | 无效证券代码 | 检查代码格式，如 `600519.SH` |
| `-40520015` | 无效字段 | 检查字段名拼写 |
| `-40520016` | 字段不支持该品种 | 该字段不适用于此证券类型 |
| `-40520018` | 多品种多字段冲突 | `wsd` 多品种时只能选一个字段 |
| `-40520019` | 日期格式错误 | 使用 `YYYYMMDD` 或 `YYYY-MM-DD` |

---

## 错误处理示例

### 基本错误处理

```python
from WindPy import w
w.start()

# wsd 错误处理
err, df = w.wsd("600519.SH", "close", "-10D", "", "", usedf=True)
if err == 0:
    print("成功:", df)
else:
    print(f"错误码: {err}")
    if err == -40520007:
        print("无数据权限，请联系 Wind 开通")
    elif err == -40522006:
        print("参数错误，请检查参数格式")

# wss 错误处理
result = w.wss("600519.SH", "close", "")
if result.ErrorCode == 0:
    print("数据:", result.Data)
else:
    print(f"错误: {result.ErrorCode}")

w.stop()
```

### 批量查询的错误处理

```python
def safe_wsd(code, fields, start, end, options=""):
    """带错误处理的 wsd 查询"""
    err, df = w.wsd(code, fields, start, end, options, usedf=True)
    if err == 0:
        return df
    elif err == -40520017:
        print(f"字段不支持: {fields}")
        return None
    elif err == -40522006:
        print(f"参数错误: {options}")
        return None
    else:
        print(f"未知错误 {err}: {code}")
        return None

# 批量查询
codes = ["600519.SH", "000858.SZ", "000001.SZ"]
for code in codes:
    df = safe_wsd(code, "close", "-10D", "", "")
    if df is not None:
        print(f"{code}: {df['CLOSE'].iloc[-1]}")
```

---

## 常见错误场景

### 1. Mac 版 SDK 字段不支持

**现象：** 返回 `-40520017`

**原因：** Mac 版 WindPy SDK 部分财务报表字段不可用

**解决：** 
- 使用 Windows 版 SDK
- 改用 `wset` 获取报表数据
- 使用 `w.wss` 配合 `rptDate` 参数

### 2. 参数错误

**现象：** 返回 `-40522006` 或 `-40522012`

**原因：** 参数名或参数值格式不正确

**解决：**
```python
# 错误
w.wset("sectorconstituent", "sectorid=a001010100000000")  # 缺少 date

# 正确
w.wset("sectorconstituent", "date=20260108;sectorid=a001010100000000")
```

### 3. 多品种多字段冲突

**现象：** 返回 `-40520018`

**原因：** `wsd` 函数多品种时只能获取一个字段

**解决：**
```python
# 错误 - 多品种多字段
w.wsd("600519.SH,000858.SZ", "close,volume", "-10D", "", "")

# 正确 - 多品种单字段
w.wsd("600519.SH,000858.SZ", "close", "-10D", "", "")

# 或 - 单品种多字段
w.wsd("600519.SH", "close,volume", "-10D", "", "")
```

### 4. 无数据权限

**现象：** 返回 `-40520007`

**解决：**
- 联系 Wind 客服开通对应数据权限
- 使用替代字段获取类似数据

---

## 调试技巧

### 打印完整错误信息

```python
result = w.wsd("600519.SH", "close", "-10D", "", "")
if result.ErrorCode != 0:
    print(f"错误码: {result.ErrorCode}")
    print(f"错误信息: {result.Data}")  # 有时包含详细错误信息
```

### 分步调试

```python
# 先测试连接
if not w.isconnected():
    w.start()

# 再测试简单查询
result = w.wsd("600519.SH", "close", "-1D", "", "")
print(f"连接测试: {result.ErrorCode}")

# 逐步增加复杂度
result = w.wsd("600519.SH", "close", "-10D", "", "")
print(f"简单查询: {result.ErrorCode}")

result = w.wsd("600519.SH", "close,volume", "-10D", "", "")
print(f"多字段: {result.ErrorCode}")
```

---

## 注意事项

1. **先检查连接：** 调用任何数据函数前确保 `w.isconnected()` 返回 True
2. **小范围测试：** 新字段或新品种先用小日期范围测试
3. **字段拼写：** WindPy 字段名区分大小写，建议全部小写
4. **返回列名：** 使用 `usedf=True` 时，列名自动转为大写
5. **数据权限：** 部分高级数据（如 Tick、分钟线）需要额外开通
