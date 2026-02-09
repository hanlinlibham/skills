---
name: windpy-sdk
description: WindPy SDK 数据获取工具包。提供标准化的 Wind 金融数据获取接口，包括行情数据、财务数据、板块成分、宏观经济等。其他 skill 可通过导入此模块获取 Wind 数据，无需直接调用 WindPy。
---

# WindPy SDK 数据获取工具包

## 定位

本 skill 是 **底层数据获取工具包**，专注于：
- WindPy 连接管理
- 标准化数据获取接口
- 数据格式转换 (DataFrame)
- 错误处理和重试

其他 skill（如 asset-monitor）应 **导入此模块** 获取数据，而不是直接调用 WindPy。

## 安装

```python
# 将 windpy_sdk 添加到 Python 路径
import sys
sys.path.insert(0, '/path/to/skills/windpy-sdk')

from windpy_sdk import WindClient, get_sector_constituents, get_historical_returns
```

## 快速开始

```python
from windpy_sdk import WindClient

# 使用上下文管理器（自动连接/断开）
with WindClient() as client:
    # 获取板块成分股
    stocks = client.get_sector_constituents('a001010100000000')
    
    # 获取历史行情
    df = client.get_daily_data('000300.SH', 'close,pct_chg', '-30D')
    
    # 获取实时行情
    snapshot = client.get_realtime_quote(['000300.SH', '000905.SH'])
```

## 核心类

### WindClient

WindPy 连接管理客户端。

```python
class WindClient:
    def __enter__(self): ...  # 自动连接
    def __exit__(self, ...): ...  # 自动断开
    
    # 板块数据
    def get_sector_constituents(self, sectorid, date=None) -> pd.DataFrame:
        """获取板块成分股"""
        
    def get_sector_list(self, sector_type='sw3') -> pd.DataFrame:
        """获取板块列表（如申万三级行业）"""
        
    # 历史数据
    def get_daily_data(self, codes, fields, start_date, end_date=None, **options) -> pd.DataFrame:
        """获取日级历史数据 (wsd)"""
        
    def get_minute_data(self, codes, fields, start_time, end_time, barsize=1) -> pd.DataFrame:
        """获取分钟数据 (wsi)"""
        
    # 截面数据
    def get_snapshot(self, codes, fields, trade_date=None) -> pd.DataFrame:
        """获取截面快照 (wss)"""
        
    def get_realtime_quote(self, codes, fields=None) -> pd.DataFrame:
        """获取实时行情 (wsq)"""
        
    # 报表数据
    def get_etf_list(self, date=None) -> pd.DataFrame:
        """获取 ETF 列表"""
        
    def get_index_constituents(self, index_code, date=None) -> pd.DataFrame:
        """获取指数成分股"""
```

## 便捷函数

```python
from windpy_sdk import (
    get_sector_constituents,      # 获取板块成分
    get_historical_returns,       # 获取历史收益率
    get_realtime_quote,           # 获取实时行情
    get_index_list,               # 获取指数列表
    get_etf_list,                 # 获取 ETF 列表
    get_bond_index_list,          # 获取债券指数列表
)

# 无需管理连接，函数内部自动处理
stocks = get_sector_constituents('a39901011i000000')  # 申万三级行业
returns = get_historical_returns('000300.SH', '-252TD')  # 过去一年日收益
```

## 常量定义

```python
from windpy_sdk.constants import (
    # 板块 SectorID
    SECTOR_ALL_A_SHARES,      # 全部A股
    SECTOR_SW3_INDUSTRIES,    # 申万三级行业
    SECTOR_HS300,             # 沪深300
    SECTOR_CSI500,            # 中证500
    
    # 常用指数代码
    INDEX_HS300,
    INDEX_CSI500,
    INDEX_SSE50,
    
    # 常用商品代码
    COMMODITY_GOLD,
    COMMODITY_SILVER,
    COMMODITY_COPPER,
)
```

## 依赖

- WindPy (Wind 金融终端 Python API)
- pandas
- numpy

## 使用示例

### 示例1: 获取申万三级行业列表

```python
from windpy_sdk import WindClient

with WindClient() as client:
    # 获取259个申万三级行业
    sw3_industries = client.get_sector_list('sw3')
    print(f"获取到 {len(sw3_industries)} 个申万三级行业")
    print(sw3_industries.head())
```

### 示例2: 获取历史收益率

```python
from windpy_sdk import get_historical_returns

# 获取过去一年日收益率
returns = get_historical_returns(
    codes='000300.SH',
    start_date='-252TD',
    field='pct_chg'
)

# 计算统计量
mean_ret = returns.mean()
std_ret = returns.std()
```

### 示例3: 批量获取多资产数据

```python
from windpy_sdk import WindClient

with WindClient() as client:
    # 获取多个指数的实时行情
    indices = ['000300.SH', '000905.SH', '000016.SH']
    quotes = client.get_realtime_quote(indices)
    
    # 获取申万三级行业的日涨跌幅
    sw3_codes = client.get_sector_list('sw3')['code'].tolist()
    daily_returns = client.get_daily_data(
        codes=sw3_codes[:10],  # 先取前10个测试
        fields='pct_chg',
        start_date='-30D'
    )
```

## 错误处理

```python
from windpy_sdk import WindClient, WindDataError

try:
    with WindClient() as client:
        data = client.get_daily_data('INVALID.CODE', 'close', '-30D')
except WindDataError as e:
    print(f"数据获取失败: {e}")
except ConnectionError as e:
    print(f"Wind 连接失败: {e}")
```

## 配置

```python
# windpy_sdk/config.py
WIND_CONFIG = {
    'start_timeout': 120,      # 连接超时
    'retry_times': 3,          # 重试次数
    'default_date_format': '%Y%m%d',
    'use_cache': True,         # 是否缓存数据
    'cache_dir': '~/.windpy_cache',
}
```

## 与其他 Skill 的关系

```
asset-monitor (监控逻辑)
    ↓ 导入
windpy-sdk (数据获取)
    ↓ 调用
WindPy (Wind API)
    ↓ 连接
Wind 金融终端
```

**原则**: 上层 skill 只依赖 windpy-sdk，不直接调用 WindPy。

## 参考

- `references/field-catalog.md` - Wind 字段速查
- `references/sector-ids.md` - 板块 SectorID 列表
- `references/error-codes.md` - 错误码说明
