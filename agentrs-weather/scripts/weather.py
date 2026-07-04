#!/usr/bin/env python3
"""
agentrs-weather —— 京东 agentrs 代理网关的「高德天气」客户端。

封装高德 weather_inquiry：实况(base) / 预报(all)。
端点：https://agentrs.jd.com/api/saas/proxy-k/v1/<tool>

⚠️ 高德天气入参是 adcode（北京=110100），不是经纬度也不是和风 LocationID。
本脚本内置「城市名→adcode」自动解析（借 geocoding），使天气查询可独立使用：
  --city  110100         直接给 adcode
  --address 北京 / 朝阳区  自动 geocoding 解析出 adcode 再查

鉴权：环境变量 JD_AGENTRS_TOKEN（不硬编码密钥）。
约定：网关一律从 JSON body 取参（query string 不生效）；HTTP 恒 200，业务看 body。

用法：
  python3 weather.py --city 110100               # 北京实况
  python3 weather.py --city 110100 --extensions all   # 预报
  python3 weather.py --address 上海市黄浦区        # 城市名自动解析
"""
import os, sys, json, argparse, urllib.request, urllib.error

BASE = "https://agentrs.jd.com/api/saas/proxy-k/v1"


def _token():
    tok = os.environ.get("JD_AGENTRS_TOKEN")
    if not tok:
        sys.exit("错误：未设置 JD_AGENTRS_TOKEN。\n  export JD_AGENTRS_TOKEN='你的token'")
    return tok


def call(tool, body, timeout=30):
    payload = {k: v for k, v in body.items() if v not in ("", None)}
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(f"{BASE}/{tool}", data=data, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {_token()}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            raw = r.read().decode("utf-8")
    except urllib.error.URLError as e:
        return {"_error": f"网络错误: {e}"}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_raw": raw}


def biz_error(resp):
    if not isinstance(resp, dict):
        return None
    code, msg = resp.get("code"), resp.get("msg") or ""
    if code in (1001, "1001"):
        return f"[未授权 1001] 该 token 未开通此工具：{msg}"
    if code in (9999, "9999") or "积分不足" in msg or "缺少必要输入参数" in msg:
        return f"[业务失败 {code}] {msg}"
    return None


def resolve_adcode(address):
    """城市名/地址 → adcode（借 geocoding 第一条结果）。"""
    resp = call("geocoding", dict(address=address))
    geos = resp.get("geocodes") if isinstance(resp, dict) else None
    if geos:
        return geos[0].get("adcode")
    return None


def weather(city, extensions="base"):
    return call("weather_inquiry", dict(city=city, extensions=extensions))


def main():
    p = argparse.ArgumentParser(description="京东 agentrs 高德天气（实况/预报）")
    p.add_argument("--city", default=None, help="高德 adcode，如北京 110100")
    p.add_argument("--address", default=None, help="城市名/地址，自动解析 adcode")
    p.add_argument("--extensions", default="base", help="base 实况 / all 预报")
    a = p.parse_args()

    city = a.city
    if not city and a.address:
        city = resolve_adcode(a.address)
        if not city:
            sys.exit(f"无法从“{a.address}”解析出 adcode")
        print(f"[解析] {a.address} → adcode {city}", file=sys.stderr)
    if not city:
        sys.exit("需提供 --city <adcode> 或 --address <城市名>")

    resp = weather(city, a.extensions)
    err = biz_error(resp)
    if err:
        print(err, file=sys.stderr)
    print(json.dumps(resp, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
