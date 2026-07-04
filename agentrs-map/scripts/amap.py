#!/usr/bin/env python3
"""
agentrs-map —— 京东 agentrs 代理网关的「高德地图 / 地理 / 天气」客户端。

封装 6 个高德(Amap)工具：
  poi(POI检索) / geocode(地理编码) / region(行政区) / ip(IP定位) /
  walk(步行路径) / coord(坐标转换)
端点：https://agentrs.jd.com/api/saas/proxy-k/v1/<tool>

鉴权：环境变量 JD_AGENTRS_TOKEN（不硬编码密钥）。
约定：网关一律从 JSON body 取参（query string 不生效）；HTTP 恒 200，业务看 body。

注：天气查询见姊妹 skill agentrs-weather（geocode 拿到的 adcode 即天气入参）。

用法：
  python3 amap.py poi     --keywords 故宫 --city beijing
  python3 amap.py geocode --address "北京市朝阳区建国路88号"
  python3 amap.py region  --keywords 北京 --subdistrict 1
  python3 amap.py ip      --ip 114.247.50.2
  python3 amap.py walk    --origin 116.397455,39.909187 --destination 116.417854,39.914888
  python3 amap.py coord   --locations 116.481499,39.990475 --coordsys gps
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


# 7 个高德工具 -------------------------------------------------
def poi(keywords, city="", **k):
    return call("search_around_gaode", dict(keywords=keywords, city=city))

def geocode(address, city="", **k):
    return call("geocoding", dict(address=address, city=city))

def region(keywords, subdistrict="", page="", offset="", extensions="", filter="", **k):
    return call("administrative_region_inquiry", dict(keywords=keywords,
                subdistrict=subdistrict, page=page, offset=offset,
                extensions=extensions, filter=filter))

def ip(ip="", **k):
    return call("ip_locating", dict(ip=ip))

def walk(origin, destination, origin_id="", destination_id="", **k):
    return call("pedestrian_path_planning", dict(origin=origin, destination=destination,
                origin_id=origin_id, destination_id=destination_id))

def coord(locations, coordsys="gps", **k):
    return call("coordinate_transformation", dict(locations=locations, coordsys=coordsys))


TOOLS = {"poi": poi, "geocode": geocode, "region": region, "ip": ip,
         "walk": walk, "coord": coord}


def main():
    p = argparse.ArgumentParser(description="京东 agentrs 高德地图/地理（6 工具）")
    p.add_argument("tool", choices=list(TOOLS))
    for opt in ("keywords", "city", "address", "subdistrict", "page", "offset",
                "extensions", "filter", "ip", "origin", "destination",
                "origin_id", "destination_id", "locations", "coordsys"):
        p.add_argument(f"--{opt}", default=None)
    a = p.parse_args()
    kw = {k: v for k, v in vars(a).items() if k != "tool" and v is not None}
    resp = TOOLS[a.tool](**kw)
    err = biz_error(resp)
    if err:
        print(err, file=sys.stderr)
    print(json.dumps(resp, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
