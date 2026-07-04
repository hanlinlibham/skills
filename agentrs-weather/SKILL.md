---
name: agentrs-weather
description: >
  天气查询工具 —— 通过京东 agentrs 代理网关调用高德天气，返回城市实况(气温/天气/湿度/风力)
  或未来预报。支持直接传高德 adcode，也支持传城市名/地址自动解析 adcode。当用户问某地天气、
  气温、今天/明天下不下雨、出门带不带伞、未来几天天气这类问题时使用。
  触发词：天气、气温、下雨、温度、湿度、风力、今天天气、明天天气、未来天气、weather、带伞。
---

# agentrs-weather —— 高德天气（实况 / 预报）

通过 `https://agentrs.jd.com/api/saas/proxy-k/v1/weather_inquiry` 查高德天气。

## 鉴权与调用约定（先读）
- 环境变量取密钥，**不硬编码**：`export JD_AGENTRS_TOKEN='你的token'`
- **网关只认 JSON body**（query string 不生效）；HTTP 恒 200，业务看 body：`1001`=未授权 / `9999 缺少必要输入参数`=参数错 / `9999 用户积分不足`=余额不足（重试常能通）。

## 关键：入参是 adcode
高德天气的 `city` 参数是**高德 adcode**（如北京=110100），**不是经纬度，也不是和风天气的 LocationID**。
本 skill 的脚本内置「城市名→adcode」自动解析（借地理编码），所以两种方式都行：
- 已知 adcode：`--city 110100`
- 只知城市名：`--address 北京` / `--address 上海市黄浦区`（自动解析）

| 入参 | 说明 |
|---|---|
| `city` | 高德 adcode（与 `address` 二选一） |
| `address` | 城市名/地址，脚本自动解析成 adcode |
| `extensions` | `base`=实况(默认) / `all`=预报 |

返回 `lives[]`（实况）含 weather/temperature/humidity/winddirection/windpower/reporttime；
`extensions=all` 时返回 `forecasts[]` 未来数日预报。

## 用法
```bash
export JD_AGENTRS_TOKEN='...'
python3 scripts/weather.py --city 110100                 # 北京实况
python3 scripts/weather.py --city 110100 --extensions all # 北京预报
python3 scripts/weather.py --address 上海市黄浦区          # 城市名自动解析
```
打印规整 JSON；遇 1001/9999 在 stderr 给可读提示。

## 直接 curl（需先有 adcode）
```bash
curl -s https://agentrs.jd.com/api/saas/proxy-k/v1/weather_inquiry \
  -X POST -H "Content-Type: application/json" \
  -H "Authorization: Bearer $JD_AGENTRS_TOKEN" \
  -d '{"city":"110100","extensions":"base"}'
```

> adcode/经纬度/POI/路径 等地图地理能力见姊妹 skill **agentrs-map**；
> 联网搜索见 **agentrs-search**。三者共用同一个 JD_AGENTRS_TOKEN。
