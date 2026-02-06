# Wind API 错误码对照表

> **状态：占位文档，待补充**
>
> 补充方法：
> 1. Wind 终端 → 帮助 → API 帮助中心 → 错误码查询
> 2. 运行代码故意触发错误，逐个记录

---

## 已知错误码

| 错误码 | 含义 | 常见原因 | 解决方法 |
|--------|------|----------|----------|
| 0 | 成功 | — | — |
| -40520007 | 无数据权限 | 账户未开通对应数据权限 | 联系 Wind 客服开通 |
| -40520017 | 字段不支持 | Mac 版 SDK 不支持该字段 | 换用 Windows 或改用其他字段 |
| -40522006 | 参数错误 | options 格式不对、字段名拼写错误 | 检查参数和分号分隔 |
| -40521001 | 网络连接失败 | Wind 终端未启动或网络断开 | 启动 Wind 终端，检查网络 |
| TODO | 品种不存在 | 代码错误或已退市 | 检查证券代码 |
| TODO | 超出数据范围 | 请求的日期超出可用范围 | 调整起止日期 |
| TODO | 请求超时 | 数据量过大或网络慢 | 减小数据范围或增大 waitTime |

---

## 待补充

> 在终端运行以下脚本收集更多错误码：

```python
from WindPy import w
w.start()

# 测试1: 无效代码
data = w.wsd("INVALID_CODE", "close", "-1D", "")
print(f"无效代码 → ErrorCode: {data.ErrorCode}")

# 测试2: 无效字段
data = w.wsd("600519.SH", "invalid_field_name", "-1D", "")
print(f"无效字段 → ErrorCode: {data.ErrorCode}")

# 测试3: 无效日期
data = w.wsd("600519.SH", "close", "invalid_date", "")
print(f"无效日期 → ErrorCode: {data.ErrorCode}")

# 测试4: 日期范围过大
data = w.wsd("600519.SH", "close", "1900-01-01", "")
print(f"日期过早 → ErrorCode: {data.ErrorCode}")

# 测试5: Mac 不支持的字段
data = w.wss("600519.SH", "tot_oper_rev", "rptDate=20231231;rptType=408001000")
print(f"财报字段 → ErrorCode: {data.ErrorCode}")

# 测试6: 未登录
# w.stop()
# data = w.wsd("600519.SH", "close", "-1D", "")
# print(f"未连接 → ErrorCode: {data.ErrorCode}")

# 将所有结果记录到此文件的表格中
```
