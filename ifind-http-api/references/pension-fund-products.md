# iFinD 养老金产品数据接口参考

## 概述

养老金产品在 iFinD 中使用 `.YLJ` 后缀（养老金），通过 `date_sequence` 接口获取净值、基本信息等数据。

## 代码格式

养老金产品代码格式：`{管理人前缀}{产品类型}{编号}.YLJ`

### 产品类型字母

| 字母 | 类型 | 说明 |
|------|------|------|
| A | 权益型 | 主要投资股票等权益类资产 |
| B | 混合型 | 股债混合配置 |
| C | 债券型 | 主要投资债券等固收类资产（含多种子类：Ca/Cb/Cc/Cf/Cg/Ch） |
| D | 货币/现金管理型 | 低风险现金管理类产品 |
| Y | 养老目标型 | 特殊养老目标产品（如 10Y003.YLJ） |

### 管理人前缀

| 前缀 | 管理人 | 产品数量(权益/混合/债券/货币) |
|------|--------|-------------------------|
| 00 | 全国社保基金理事会 | A:19 / B:5 / C:2 / D:1 |
| 02 | 博时基金 | A:4 / B:3 / C:1 / D:1 |
| 05 | 大成基金 | A:9 / B:5 / C:1 / D:1 |
| 07 | 工银瑞信 | A:6 / B:4 / C:70+ / D:1 |
| 10 | 海富通基金 | A:10 / B:7 / C:2 / D:1 |
| 11 | 华夏基金 | A:9 / B:10 / C:3 / D:3 |
| 15 | 嘉实基金 | A:10 / B:3 / C:8 / D:3 |
| 18 | 南方基金 | A:4 / B:2 / C:21 / D:1 |
| 20 | 鹏华基金 | A:6 / B:6 / C:2 |
| 48 | 易方达基金 | A:8 / B:13 / C:5 / D:2 |
| 51 | 银华基金 | A:6 / B:2 / C:1 / D:1 |
| CJ | 长江养老 | A:6 / B:6 / C:28 |
| CL | 长城人寿 | A:14 / B:16 / C:7 |
| HT | 华泰资产 | A:11 / B:5 / C:1 / D:1 |
| JX | 建信养老金 | A:2 / B:4 / C:3 / D:1 |
| PA | 平安养老 | A:14 / B:11 / C:50+ / D:3 |
| RB | 人保资产 | A:7 / B:5 / C:20 / D:2 |
| TP | 太平养老 | A:3 / B:4 / C:13 / D:2 |
| TZ | 泰康资产 | A:16 / B:10 / C:20 |
| XH | 新华养老 | A:2 / B:3 / C:18 |
| ZJ | 中金公司 | A:12 / B:4 / C:55+ / D:2 |
| ZX | 中信证券 | A:10 / B:4 / C:3 |

### 债券型子类说明

| 子类 | 代码模式 | 说明 |
|------|---------|------|
| Ca | `xxCaNN` | 债券型 A 子类（普通债券） |
| Cb | `xxCbNNNN` | 债券型 B 子类（信用债/定制类，编号4位） |
| Cc | `xxCcNN` | 债券型 C 子类 |
| Cf | `xxCfNNNN` | 债券型 F 子类（定制固收，编号4位） |
| Cg | `xxCgNNNN` | 债券型 G 子类（定制固收，编号4位） |
| Ch | `xxChNN` | 债券型 H 子类 |

---

## 常用指标（date_sequence 接口）

### 净值与基本信息指标

| indicator | 说明 | indiparams |
|-----------|------|------------|
| ths_unit_nv_fund | 单位净值 | 无 |
| ths_fund_short_name_fund | 基金简称 | 无 |
| ths_fund_establishment_date_fund | 基金成立日 | 无 |
| ths_rsbfl_pension | 人社部养老金分类 | `["100"]`（100 表示人社部分类体系） |
| ths_invest_manager_current_obcm | 投资经理(现任) | 无 |

---

## HTTP API 调用示例

### 获取权益型养老金产品净值（date_sequence）

```python
# 批量获取权益型养老金净值和基本信息
params = {
    "codes": "00A001.YLJ,00A002.YLJ,02A001.YLJ,05A001.YLJ,07A003.YLJ",
    "startdate": "2026-02-10",
    "enddate": "2026-03-10",
    "indipara": [
        {"indicator": "ths_unit_nv_fund", "indiparams": [""]},
        {"indicator": "ths_fund_short_name_fund", "indiparams": [""]},
        {"indicator": "ths_fund_establishment_date_fund", "indiparams": [""]},
        {"indicator": "ths_rsbfl_pension", "indiparams": ["100"]},
        {"indicator": "ths_invest_manager_current_obcm", "indiparams": [""]}
    ]
}
data = ifind_request("date_sequence", params)
```

### 获取混合型养老金产品净值

```python
params = {
    "codes": "00B001.YLJ,00B002.YLJ,02B001.YLJ,05B001.YLJ,07B002.YLJ",
    "startdate": "2026-02-10",
    "enddate": "2026-03-10",
    "indipara": [
        {"indicator": "ths_unit_nv_fund", "indiparams": [""]},
        {"indicator": "ths_fund_short_name_fund", "indiparams": [""]}
    ]
}
data = ifind_request("date_sequence", params)
```

### 获取债券型养老金产品净值

```python
params = {
    "codes": "07Cb0115.YLJ,07Cf0701.YLJ,07Cg0201.YLJ,PACb0141.YLJ,ZJCf13.YLJ",
    "startdate": "2026-02-10",
    "enddate": "2026-03-10",
    "indipara": [
        {"indicator": "ths_unit_nv_fund", "indiparams": [""]}
    ]
}
data = ifind_request("date_sequence", params)
```

### 获取货币型养老金产品净值

```python
params = {
    "codes": "00D001.YLJ,02D001.YLJ,05D001.YLJ,07D001.YLJ,10D001.YLJ,11D001.YLJ",
    "startdate": "2026-02-10",
    "enddate": "2026-03-10",
    "indipara": [
        {"indicator": "ths_unit_nv_fund", "indiparams": [""]}
    ]
}
data = ifind_request("date_sequence", params)
```

---

## 完整产品代码清单

### 权益型（A类）— 共 183 只

```
00A001.YLJ, 00A002.YLJ, 00A003.YLJ, 00A004.YLJ, 00A005.YLJ, 00A006.YLJ,
00A007.YLJ, 00A009.YLJ, 00A010.YLJ, 00A011.YLJ, 00A012.YLJ, 00A013.YLJ,
00A014.YLJ, 00A015.YLJ, 00A016.YLJ, 00A017.YLJ, 00A018.YLJ, 00A020.YLJ,
00Ad01.YLJ, 02A001.YLJ, 02A002.YLJ, 02A003.YLJ, 02A004.YLJ, 02Ac01.YLJ,
05A001.YLJ, 05A002.YLJ, 05A003.YLJ, 05A004.YLJ, 05A005.YLJ, 05A006.YLJ,
05A007.YLJ, 05A008.YLJ, 05A009.YLJ, 05Ad01.YLJ, 07A003.YLJ, 07A004.YLJ,
07A005.YLJ, 07A007.YLJ, 07A008.YLJ, 07A009.YLJ, 07Ac01.YLJ, 10A001.YLJ,
10A002.YLJ, 10A003.YLJ, 10A004.YLJ, 10A005.YLJ, 10A006.YLJ, 10A007.YLJ,
10A008.YLJ, 10A010.YLJ, 10Y003.YLJ, 10Y003_1.YLJ, 10Y008.YLJ, 10Y009.YLJ,
11A001.YLJ, 11A002.YLJ, 11A003.YLJ, 11A004.YLJ, 11A005.YLJ, 11A006.YLJ,
11A007.YLJ, 11A008.YLJ, 11Ac01.YLJ, 11Ad01.YLJ, 15A001.YLJ, 15A002.YLJ,
15A003.YLJ, 15A004.YLJ, 15A005.YLJ, 15A006.YLJ, 15A007.YLJ, 15A008.YLJ,
15A009.YLJ, 15A010.YLJ, 18A001.YLJ, 18A002_1.YLJ, 18A003.YLJ, 18A004.YLJ,
18Ca04.YLJ, 20A001.YLJ, 20A002.YLJ, 20A003.YLJ, 20A004.YLJ, 20A005.YLJ,
20Ad01.YLJ, 20Ca06.YLJ, 48A001.YLJ, 48Ac01.YLJ, 48C015.YLJ, 48C031.YLJ,
48C045.YLJ, 48C056.YLJ, 48C060.YLJ, 48C062.YLJ, 51A001.YLJ, 51A002.YLJ,
51A003_1.YLJ, 51A004.YLJ, 51A005.YLJ, 51A006.YLJ, CJA001.YLJ, CJA002_1.YLJ,
CJA003.YLJ, CJA004.YLJ, CJA005.YLJ, CJAa01.YLJ, CL0001.YLJ, CL0021.YLJ,
CL0022.YLJ, CL0036.YLJ, CL0037.YLJ, CL0038.YLJ, CL0039.YLJ, CL0062.YLJ,
CL0068.YLJ, CL0069.YLJ, CL0070.YLJ, CL0071.YLJ, CL0072.YLJ, CL0161.YLJ,
HTA001.YLJ, HTA002.YLJ, HTA003.YLJ, HTA004.YLJ, HTA005.YLJ, HTA006.YLJ,
HTA007.YLJ, HTA008.YLJ, HTA009.YLJ, HTA010.YLJ, HTAc01.YLJ, JXA001.YLJ,
JXA002.YLJ, PAA001.YLJ, PAA002.YLJ, PAA005.YLJ, PAA006.YLJ, PAA007.YLJ,
PAA008.YLJ, PAA009.YLJ, PAA010.YLJ, PAA011.YLJ, PAA012.YLJ, PAA013.YLJ,
PAA014.YLJ, RB0012.YLJ, RB0039.YLJ, RB0051.YLJ, RB0053.YLJ, RB0057.YLJ,
RB0058.YLJ, RB0061.YLJ, TP1019.YLJ, TP1081.YLJ, TPA001.YLJ, TPA002.YLJ,
TZ0051.YLJ, TZ0053.YLJ, TZA001.YLJ, TZA002.YLJ, TZA003.YLJ, TZA004.YLJ,
TZA005.YLJ, TZA006.YLJ, TZA007.YLJ, TZA008.YLJ, TZA009.YLJ, TZA010.YLJ,
TZA011.YLJ, TZA012.YLJ, TZA013.YLJ, TZA014.YLJ, TZAc01.YLJ, TZAc02.YLJ,
XHA001.YLJ, XHA002.YLJ, ZJA001.YLJ, ZJA002.YLJ, ZJA003.YLJ, ZJA005.YLJ,
ZJA006.YLJ, ZJA007.YLJ, ZJA008.YLJ, ZJA009.YLJ, ZJA010.YLJ, ZJA011.YLJ,
ZJAc01.YLJ, ZJAd01.YLJ, ZXA001.YLJ, ZXA002.YLJ, ZXA003.YLJ, ZXA004.YLJ,
ZXA005.YLJ, ZXA006.YLJ, ZXA007.YLJ, ZXA008.YLJ, ZXA010.YLJ
```

### 混合型（B类）— 共 134 只

```
00B001.YLJ, 00B002.YLJ, 00B006.YLJ, 00B007.YLJ, 00B008.YLJ, 02B001.YLJ,
02B002.YLJ, 02B003.YLJ, 05B001.YLJ, 05B003.YLJ, 05B004.YLJ, 05B005.YLJ,
05B006.YLJ, 07B002.YLJ, 07B003.YLJ, 07B004.YLJ, 10B001.YLJ, 10B002.YLJ,
10B003.YLJ, 10B004.YLJ, 10B005.YLJ, 10B006.YLJ, 10B007.YLJ, 10Y007.YLJ,
10Y007_1.YLJ, 10Y010.YLJ, 11B001.YLJ, 11B002.YLJ, 11B003.YLJ, 11B004.YLJ,
11B006.YLJ, 11B007.YLJ, 11B008.YLJ, 11B009.YLJ, 11B010.YLJ, 15B001.YLJ,
15B008.YLJ, 15B009.YLJ, 18B001.YLJ, 18B002.YLJ, 20B001.YLJ, 20B002.YLJ,
20B003.YLJ, 20B004.YLJ, 20B005.YLJ, 20B006.YLJ, 48B001.YLJ, 48B002.YLJ,
48B003.YLJ, 48B004.YLJ, 48B005.YLJ, 48B006.YLJ, 48B007.YLJ, 48B008.YLJ,
48B009.YLJ, 48B010.YLJ, 48B011.YLJ, 48B013.YLJ, 48C058.YLJ, 48C065.YLJ,
51B001.YLJ, 51B002.YLJ, CJB001.YLJ, CJB002.YLJ, CJB003.YLJ, CJB004.YLJ,
CJB005.YLJ, CJB006.YLJ, CL0003.YLJ, CL0004.YLJ, CL0020.YLJ, CL0033.YLJ,
CL0034.YLJ, CL0035.YLJ, CL0047.YLJ, CL0048.YLJ, CL0080.YLJ, CL0081.YLJ,
CL0082.YLJ, CL0083.YLJ, CL0084.YLJ, CL0146.YLJ, CL0157.YLJ, CL0158.YLJ,
CL0159.YLJ, CL0160.YLJ, CLB012.YLJ, HTB001.YLJ, HTB002.YLJ, HTB003.YLJ,
HTB004.YLJ, HTB005.YLJ, JXB001.YLJ, JXB002.YLJ, JXB003.YLJ, JXB004.YLJ,
PAB001.YLJ, PAB003.YLJ, PAB004.YLJ, PAB00501.YLJ, PAB006.YLJ, PAB007.YLJ,
PAB008.YLJ, PAB009.YLJ, PAB010.YLJ, PAB011.YLJ, RB0002.YLJ, RB0022.YLJ,
RB0045.YLJ, RB0056.YLJ, RB0060.YLJ, TP1005.YLJ, TP1042.YLJ, TP1069.YLJ,
TPB002.YLJ, TPB003.YLJ, TPB004.YLJ, TZ0050.YLJ, TZB001.YLJ, TZB002.YLJ,
TZB003.YLJ, TZB004.YLJ, TZB005.YLJ, TZB006.YLJ, TZB007.YLJ, TZB008.YLJ,
TZB009.YLJ, TZB010.YLJ, XHB001.YLJ, XHB002.YLJ, XHB003.YLJ, ZJB001.YLJ,
ZJB002.YLJ, ZJB003.YLJ, ZJB004.YLJ, ZXB001.YLJ, ZXB003.YLJ, ZXB004.YLJ
```

### 债券型（C类）— 共 345 只

```
00Ca09.YLJ, 00Cg0202.YLJ, 02Ca01.YLJ, 05Ca02.YLJ,
07Cb0115.YLJ, 07Cb0117.YLJ, 07Cb0118.YLJ, 07Cb0119.YLJ, 07Cb0120.YLJ,
07Cb0121.YLJ, 07Cb0122.YLJ, 07Cb0123.YLJ, 07Cb0124.YLJ, 07Cb0125.YLJ,
07Cc01.YLJ, 07Cc02.YLJ, 07Cc03.YLJ,
07Cf0701.YLJ, 07Cf0702.YLJ, 07Cf0703.YLJ, 07Cf0704.YLJ, 07Cf0705.YLJ,
07Cf0706.YLJ, 07Cf0707.YLJ, 07Cf0708.YLJ, 07Cf0709.YLJ, 07Cf0710.YLJ,
07Cf0711.YLJ, 07Cf0712.YLJ, 07Cf0713.YLJ, 07Cf0714.YLJ, 07Cf0715.YLJ,
07Cf0716.YLJ, 07Cf0717.YLJ, 07Cf0718.YLJ, 07Cf0719.YLJ, 07Cf0720.YLJ,
07Cf0721.YLJ, 07Cf0722.YLJ, 07Cf0723.YLJ, 07Cf0724.YLJ, 07Cf0725.YLJ,
07Cg0201.YLJ, 07Cg0202.YLJ, 07Cg0203.YLJ, 07Cg0204.YLJ, 07Cg0205.YLJ,
07Cg0206.YLJ, 07Cg0207.YLJ, 07Cg0208.YLJ, 07Cg0209.YLJ, 07Cg0216.YLJ,
07Cg0217.YLJ, 07Cg0218.YLJ, 07Cg0219.YLJ, 07Cg0220.YLJ, 07Cg0221.YLJ,
07Cg0222.YLJ, 07Cg0223.YLJ, 07Cg0224.YLJ, 07Cg0225.YLJ, 07Cg0226.YLJ,
07Cg0227.YLJ, 07Cg0228.YLJ, 07Cg0229.YLJ, 07Cg0230.YLJ, 07Cg0231.YLJ,
07Cg0232.YLJ, 07Cg0233.YLJ, 07Cg0234.YLJ,
10Ca02.YLJ, 11Ca01.YLJ, 11Cc01.YLJ, 11Cg02.YLJ,
15Ca01.YLJ, 15CgAB.YLJ, 15CgAC.YLJ, 15CgBA.YLJ, 15CgBD.YLJ, 15CgBF.YLJ,
15CgBG.YLJ, 15CgBH.YLJ,
18Ca02.YLJ, 18Cb0101.YLJ ~ 18Cb0120.YLJ (20只),
20Ca02.YLJ, 20Ca05.YLJ,
48C063.YLJ, 48Ca04.YLJ, 48Ca06.YLJ, 48Cc02.YLJ, 48Ch02.YLJ, 51Ca01.YLJ,
CJ0012.YLJ ~ CJ0068.YLJ (28只),
CL0002.YLJ, CL0005.YLJ, CL0025.YLJ, CL0026.YLJ, CL0027.YLJ, CL0041.YLJ,
CL0064.YLJ, CL0067.YLJ, CL0101.YLJ, CL0140.YLJ, CL0189.YLJ, CL0190.YLJ,
HTCc01.YLJ, JXCa01.YLJ, JXCa02.YLJ, JXCf03.YLJ,
PACa17.YLJ ~ PACa19.YLJ, PACb0141.YLJ ~ PACb0161.YLJ (20只),
PACf0819.YLJ ~ PACf0904.YLJ (6只), PACg0202.YLJ ~ PACg0245.YLJ (30只),
RB0052.YLJ ~ RB0092.YLJ (20只),
TP1091.YLJ ~ TP1108.YLJ (9只), TPCc01.YLJ, TPCc02.YLJ, TPCg01.YLJ, TPCg02.YLJ,
TZ1088.YLJ, TZ1092.YLJ, TZCa01.YLJ, TZCb0182.YLJ ~ TZCb0199.YLJ (14只),
TZCg0101.YLJ, TZCg0118.YLJ, TZCg0119.YLJ,
XHCb0112.YLJ ~ XHCb0130.YLJ (18只),
ZJCa02.YLJ ~ ZJCa06.YLJ, ZJCb09.YLJ ~ ZJCb18.YLJ (10只),
ZJCc01.YLJ, ZJCc02.YLJ, ZJCf13.YLJ ~ ZJCf57.YLJ (22只),
ZJCg02.YLJ ~ ZJCg46.YLJ (33只),
ZXCa04.YLJ, ZXCf02.YLJ, ZXCg01.YLJ
```

### 货币/现金管理型（D类）— 共 29 只

```
00D001.YLJ, 02D001.YLJ, 05D001.YLJ, 07D001.YLJ, 10D001.YLJ, 11D001.YLJ,
11D002.YLJ, 11D003.YLJ, 15D001.YLJ, 15D003.YLJ, 15D004.YLJ, 18D001.YLJ,
48D001.YLJ, 48D002.YLJ, 51D001.YLJ, A948.YLJ, HTD001.YLJ, JXD001.YLJ,
PAD001.YLJ, PAD002.YLJ, PAD004.YLJ, RB0009.YLJ, RB0093.YLJ, TP1064.YLJ,
TPD001.YLJ, TPD002.YLJ, TZ0025.YLJ, ZJD001.YLJ, ZJD002.YLJ
```

---

## THS_DS 超级命令到 HTTP API 转换

超级命令格式：
```
THS_DS('codes', 'indicators', 'indiparams', 'functionpara', 'startdate', 'enddate')
```

其中 indicators 和 indiparams 使用分号分隔，一一对应。

### 转换规则

| 超级命令字段 | HTTP API 字段 | 说明 |
|-----------|-------------|------|
| codes | `codes` | 直接使用 |
| indicators（分号分隔） | `indipara[].indicator` | 每个指标一个对象 |
| indiparams（分号分隔） | `indipara[].indiparams` | 对应指标的参数数组 |
| functionpara | `functionpara` | key-value 格式 |
| startdate | `startdate` | 日期 |
| enddate | `enddate` | 日期 |

### 转换示例

超级命令：
```
THS_DS('00A001.YLJ,00A002.YLJ',
       'ths_unit_nv_fund;ths_fund_short_name_fund;ths_rsbfl_pension',
       ';;100',
       '',
       '2026-02-10',
       '2026-03-10')
```

对应 HTTP API（date_sequence）：
```python
params = {
    "codes": "00A001.YLJ,00A002.YLJ",
    "startdate": "2026-02-10",
    "enddate": "2026-03-10",
    "indipara": [
        {"indicator": "ths_unit_nv_fund", "indiparams": [""]},
        {"indicator": "ths_fund_short_name_fund", "indiparams": [""]},
        {"indicator": "ths_rsbfl_pension", "indiparams": ["100"]}
    ]
}
data = ifind_request("date_sequence", params)
```

---

## 批量获取全市场养老金数据的实践建议

1. **分批请求** — 养老金产品总计 690+ 只，建议每批 50-100 只避免触发 -4305 限制
2. **先取基本信息** — 用 `ths_fund_short_name_fund` + `ths_rsbfl_pension` 建立代码-名称-分类映射表
3. **再取净值序列** — 单独请求 `ths_unit_nv_fund`，按管理人或类型分批
4. **注意 CL 前缀** — 长城人寿的编号体系为纯数字（CL0001~CL0190），类型需通过人社部分类字段判断
5. **注意特殊代码** — 如 `A948.YLJ`、`10Y003_1.YLJ` 等非标准编号

```python
# 完整批量获取示例
import time

EQUITY_CODES = ["00A001.YLJ", "00A002.YLJ", ...]  # 权益型全部代码
BATCH_SIZE = 80

for i in range(0, len(EQUITY_CODES), BATCH_SIZE):
    batch = EQUITY_CODES[i:i+BATCH_SIZE]
    params = {
        "codes": ",".join(batch),
        "startdate": "2026-02-10",
        "enddate": "2026-03-10",
        "indipara": [
            {"indicator": "ths_unit_nv_fund", "indiparams": [""]}
        ]
    }
    data = ifind_request("date_sequence", params)
    # 处理 data...
    time.sleep(0.2)  # 控制请求频率（600次/分钟）
```
