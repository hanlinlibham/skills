"""
WindPy SDK 常量定义
"""

# ============================================
# 板块 SectorID
# ============================================

# 市场板块
SECTOR_ALL_A_SHARES = 'a001010100000000'      # 全部A股
SECTOR_SH_A_SHARES = 'a001010200000000'       # 上证A股
SECTOR_SZ_A_SHARES = 'a001010300000000'       # 深证A股
SECTOR_GEM = '1000006528000000'               # 创业板
SECTOR_STAR = 'a001010l00000000'              # 科创板

# 申万行业
SECTOR_SW1_INDUSTRIES = 'a39901011g000000'    # 申万一级行业(31个)
SECTOR_SW3_INDUSTRIES = 'a39901011i000000'    # 申万三级行业(259个)

# 主要指数
SECTOR_HS300 = '1000000098000000'             # 沪深300
SECTOR_CSI500 = '1000000099000000'            # 中证500
SECTOR_SSE50 = '1000000087000000'             # 上证50
SECTOR_CSI1000 = '1000000088000000'           # 中证1000

# 债券板块
SECTOR_BOND_INDEX = 'a002010100000000'        # 债券指数板块

# ETF板块
SECTOR_ETF = 'a002010300000000'               # ETF板块

# ============================================
# 常用指数代码
# ============================================

INDEX_HS300 = '000300.SH'                     # 沪深300
INDEX_CSI500 = '000905.SH'                    # 中证500
INDEX_SSE50 = '000016.SH'                     # 上证50
INDEX_CSI1000 = '000852.SH'                   # 中证1000
INDEX_SSE = '000001.SH'                       # 上证指数
INDEX_SZSE = '399001.SZ'                      # 深证成指
INDEX_GEM = '399006.SZ'                       # 创业板指
INDEX_STAR = '000688.SH'                      # 科创50
INDEX_WIND_A = '883985.WI'                    # 万得全A

# ============================================
# 商品期货代码
# ============================================

COMMODITY_GOLD = 'AU00.SHF'                   # 黄金
COMMODITY_SILVER = 'AG00.SHF'                 # 白银
COMMODITY_COPPER = 'CU00.SHF'                 # 铜
COMMODITY_ALUMINUM = 'AL00.SHF'               # 铝
COMMODITY_ZINC = 'ZN00.SHF'                   # 锌
COMMODITY_REBAR = 'RB00.SHF'                  # 螺纹钢
COMMODITY_CRUDE = 'SC00.INE'                  # 原油
COMMODITY_PTA = 'TA00.CZC'                    # PTA

# ============================================
# 全球指数代码
# ============================================

GLOBAL_SPX = 'SPX.GI'                         # 标普500
GLOBAL_NASDAQ = 'IXIC.GI'                     # 纳斯达克
GLOBAL_DOW = 'DJI.GI'                         # 道琼斯
GLOBAL_VIX = 'VIX.GI'                         # VIX波动率
GLOBAL_HSI = 'HSI.HI'                         # 恒生指数
GLOBAL_NIKKEI = 'N225.GI'                     # 日经225
GLOBAL_KOSPI = 'KS11.GI'                      # 韩国KOSPI
GLOBAL_DAX = 'GDAXI.GI'                       # 德国DAX
GLOBAL_FTSE = 'FTSE.GI'                       # 英国富时100

# ============================================
# 常用字段
# ============================================

FIELDS_PRICE = 'open,high,low,close,pre_close'
FIELDS_VOLUME = 'volume,amt'
FIELDS_CHANGE = 'pct_chg,chg'
FIELDS_VALUATION = 'pe_ttm,pb_lf,ps_ttm'
FIELDS_MKT_CAP = 'mkt_cap_ard,total_shares,float_a_shares'

# 默认配置
DEFAULT_CONFIG = {
    'start_timeout': 120,
    'retry_times': 3,
    'date_format': '%Y%m%d',
    'use_cache': False,
}
