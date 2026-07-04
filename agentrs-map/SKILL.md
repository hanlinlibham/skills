---
name: agentrs-map
description: >
  高德地图 / 地理工具箱 —— 通过京东 agentrs 代理网关，用单一 Bearer Token 调 6 个高德(Amap)工具：
  POI 地点检索、地理编码(地址↔经纬度/adcode)、行政区域查询、IP 定位、步行路径规划、坐标转换。
  当需要查地点经纬度与 adcode、找附近地点(POI)、做步行导航、转换坐标系、
  按 IP 定位、查行政区划时使用。触发词：高德、地图、经纬度、坐标、adcode、地理编码、
  POI、附近、步行路线、导航、坐标转换、IP定位、行政区、省市区。
---

# agentrs-map —— 高德地图 / 地理（6 工具）

通过 `https://agentrs.jd.com/api/saas/proxy-k/v1/<tool>`，单一 Bearer Token 调 6 个高德工具。

## 鉴权与调用约定（先读）
- 环境变量取密钥，**不硬编码**：`export JD_AGENTRS_TOKEN='你的token'`
- **网关只认 JSON body**：文档标 GET/POST 都不影响，query string 会报"缺少必要输入参数"。
- HTTP 恒 200，业务看 body：`1001`=token 未授权；`9999 缺少必要输入参数`=参数错；`9999 用户积分不足`=余额不足（重试常能通）。

## 6 个工具
| 工具 | 入参 | 返回要点 |
|---|---|---|
| `poi` | `{keywords(必填), city(拼音如 beijing)}` | POI 文本检索（名虽 around 但**非按经纬度周边**）；`pois[]` 含 rating/人均/营业时间/招牌菜/电话/location |
| `geocode` | `{address, city}` | 地址→坐标；`geocodes[]` 含 location/adcode/level/district |
| `region` | `{keywords, subdistrict, offset, page}` | 行政区树；`districts[]` 含 adcode/center/level/下级 |
| `ip` | `{ip}`（留空取请求 IP，仅国内） | province/city/adcode/rectangle |
| `walk` | `{origin:"lon,lat", destination:"lon,lat"}` | `route.paths[]` 含 distance/duration/steps[] 分段导航 |
| `coord` | `{locations:"lon,lat", coordsys: gps/baidu/mapbar/autonavi}` | 转成高德坐标 |

## 用法
```bash
export JD_AGENTRS_TOKEN='...'
python3 scripts/amap.py poi     --keywords 故宫 --city beijing
python3 scripts/amap.py geocode --address "北京市朝阳区建国路88号"
python3 scripts/amap.py region  --keywords 北京 --subdistrict 1
python3 scripts/amap.py ip      --ip 114.247.50.2
python3 scripts/amap.py walk    --origin 116.397455,39.909187 --destination 116.417854,39.914888
python3 scripts/amap.py coord   --locations 116.481499,39.990475 --coordsys gps
```
打印规整 JSON；遇 1001/9999 在 stderr 给可读提示。

## 组合范式
- **"附近有什么 / 某地点信息"**：`poi --keywords X --city Y`。
- **"A 到 B 步行怎么走"**：两端各 `geocode`/`poi` 拿经纬度 → `walk`。
- **坐标系不一致**（GPS/百度坐标接入高德）：先 `coord` 统一到高德。
- **查天气**：`geocode` 拿到的 `adcode` 即天气入参 → 见姊妹 skill **agentrs-weather**。

> 联网搜索见 **agentrs-search**；天气见 **agentrs-weather**。三者共用同一个 JD_AGENTRS_TOKEN。
