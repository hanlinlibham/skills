# WindPy 常用字段速查

## 行情字段 (w.wsd / w.wss)

### 价格与成交
| 字段 | 含义 | 函数 |
|------|------|------|
| `open` | 开盘价 | wsd/wss |
| `high` | 最高价 | wsd/wss |
| `low` | 最低价 | wsd/wss |
| `close` | 收盘价 | wsd/wss |
| `pre_close` | 昨收价 | wsd/wss |
| `volume` | 成交量(股) | wsd/wss |
| `amt` | 成交额(元) | wsd/wss |
| `pct_chg` | 涨跌幅(%) | wsd/wss |
| `turn` | 换手率(%) | wsd/wss |
| `vwap` | 均价 | wsd/wss |
| `adjfactor` | 复权因子 | wsd |
| `maxupordown` | 涨跌停标记(1/-1/0) | wss |
| `trade_status` | 交易状态 | wss |
| `susp_reason` | 停牌原因 | wss |

### 市值指标
| 字段 | 含义 | 函数 |
|------|------|------|
| `mkt_cap` | 总市值 | wss |
| `mkt_cap_ard` | 总市值(元) | wss |
| `mkt_cap_float` | 流通市值(元) | wss |
| `total_shares` | 总股本 | wss |
| `float_a_shares` | A股流通股本 | wss |

### 区间指标
| 字段 | 含义 | options |
|------|------|---------|
| `pct_chg_per` | 区间涨跌幅 | `startDate=...;endDate=...` |
| `swing` | 振幅 | wsd |

### 实时行情 (w.wsq)
| 字段 | 含义 |
|------|------|
| `rt_last` | 最新价 |
| `rt_open` | 今开 |
| `rt_high` | 最高 |
| `rt_low` | 最低 |
| `rt_pre_close` | 昨收 |
| `rt_pct_chg` | 涨跌幅 |
| `rt_chg` | 涨跌额 |
| `rt_vol` | 成交量 |
| `rt_amt` | 成交额 |
| `rt_last_vol` | 最新成交量 |
| `rt_bid1~rt_bid5` | 买1~5价 |
| `rt_bsize1~rt_bsize5` | 买1~5量 |
| `rt_ask1~rt_ask5` | 卖1~5价 |
| `rt_asize1~rt_asize5` | 卖1~5量 |

---

## 基本面字段 (w.wss)

### 公司信息
| 字段 | 含义 |
|------|------|
| `sec_name` | 证券简称 |
| `sec_englishname` | 英文名称 |
| `sec_type` | 证券类型 |
| `industry_sw` | 申万一级行业 |
| `industry_sw_level2` | 申万二级行业 |
| `industry_sw_level3` | 申万三级行业 |
| `listdate` | 上市日期 |
| `delist_date` | 退市日期 |
| `ipo_date` | IPO日期 |
| `ipo_price` | IPO发行价 |
| `province` | 省份 |
| `city` | 城市 |
| `chairman` | 董事长 |
| `mng_ceomember` | CEO |
| `employees` | 员工人数 |
| `office_address` | 办公地址 |
| `address` | 地址 |
| `phone` | 电话 |
| `website` | 网站 |
| `founddate` | 成立日期 |
| `main_business` | 主营业务 |
| `businessscope` | 经营范围 |
| `regcapital` | 注册资本 |

### 股本结构
| 字段 | 含义 |
|------|------|
| `total_shares` | 总股本 |
| `float_a_shares` | A股流通股本 |
| `free_float_shares` | 自由流通股本 |
| `holder_num` | 股东户数 |

### 估值指标
| 字段 | 含义 |
|------|------|
| `pe_ttm` | 市盈率(TTM) |
| `pe_lyr` | 市盈率(LYR) |
| `pb_lf` | 市净率(LF) |
| `pb_mrq` | 市净率(MRQ) |
| `ps_ttm` | 市销率(TTM) |
| `pcf_ocf_ttm` | 市现率(TTM) |
| `ev` | 企业价值 |
| `ev_ebitda` | EV/EBITDA |
| `nav` | 每股净资产(基金/股票) |
| `dividendyield` | 股息率 |

### 盈利能力
| 字段 | 含义 |
|------|------|
| `roe_ttm` | ROE(TTM) |
| `roe_diluted` | ROE(摊薄) |
| `roe_avg` | ROE(平均) |
| `roa_ttm` | ROA(TTM) |
| `roic_ttm` | ROIC(TTM) |
| `grossprofit_margin` | 毛利率 |
| `netprofit_margin` | 净利率 |
| `operating_margin` | 营业利润率 |
| `ebitda_margin` | EBITDA利润率 |
| `eps_ttm` | 每股收益(TTM) |
| `eps_lyr` | 每股收益(LYR) |
| `eps_basic` | 基本每股收益 |
| `eps_diluted` | 稀释每股收益 |
| `bps` | 每股净资产 |

### 成长性
| 字段 | 含义 |
|------|------|
| `yoynetprofit` | 净利润同比(%) |
| `yoyrevenue` | 营收同比(%) |
| `yoyeps_basic` | EPS同比(%) |
| `yoy_tr` | 总收入同比 |
| `yoy_or` | 营业收入同比 |

### 偿债/运营
| 字段 | 含义 |
|------|------|
| `current_ratio` | 流动比率 |
| `quick_ratio` | 速动比率 |
| `debttoassets` | 资产负债率 |
| `longdebttolongcapital` | 长期负债/长期资本 |
| `turnover_ttm` | 总资产周转率 |
| `invturn_ttm` | 存货周转率 |
| `arturn_ttm` | 应收账款周转率 |

---

## 技术指标字段 (w.wsd)

| 字段 | 含义 | 默认参数 |
|------|------|----------|
| `MACD` | MACD指标 | (12,26,9) |
| `RSI` | RSI相对强弱指标 | (14) |
| `KDJ` | KDJ随机指标 | (9,3,3) |
| `BOLL` | 布林带 | (20,2) |
| `CCI` | CCI顺势指标 | (14) |
| `WR` | 威廉指标 | (14) |

**注意：** 默认参数版本可用，自定义参数（如 `RSI(6)`）可能需要额外权限。

**使用示例：**
```python
err, df = w.wsd("600519.SH", "MACD,RSI,KDJ", "-30D", "", "", usedf=True)
# 列名: ['MACD', 'RSI', 'KDJ']
```

---

## 利润表字段 (w.wss, rptDate=xxx)

| 字段 | 含义 |
|------|------|
| `tot_oper_rev` | 营业总收入 |
| `oper_rev` | 营业收入 |
| `int_inc` | 利息收入 |
| `comm_inc` | 手续费收入 |
| `tot_oper_cost` | 营业总成本 |
| `oper_cost` | 营业成本 |
| `oper_tax_surcharges` | 税金及附加 |
| `selling_dist_exp` | 销售费用 |
| `gerl_admin_exp` | 管理费用 |
| `rd_exp` | 研发费用 |
| `fin_exp_is` | 财务费用 |
| `oper_profit` | 营业利润 |
| `tot_profit` | 利润总额 |
| `net_profit_is` | 净利润 |
| `net_profit_parent_comp_is` | 归母净利润 |
| `minority_int_is` | 少数股东损益 |
| `eps_basic` | 基本每股收益 |
| `eps_diluted` | 稀释每股收益 |

---

## 资产负债表字段 (w.wss, rptDate=xxx)

| 字段 | 含义 |
|------|------|
| `tot_assets` | 总资产 |
| `tot_cur_assets` | 流动资产合计 |
| `cash_equivalents` | 货币资金 |
| `tradable_fin_assets` | 交易性金融资产 |
| `notes_receiv` | 应收票据 |
| `acct_receiv` | 应收账款 |
| `prepay` | 预付款项 |
| `inventories` | 存货 |
| `tot_non_cur_assets` | 非流动资产合计 |
| `fix_assets` | 固定资产 |
| `const_in_prog` | 在建工程 |
| `intang_assets` | 无形资产 |
| `goodwill` | 商誉 |
| `tot_liab` | 负债合计 |
| `tot_cur_liab` | 流动负债合计 |
| `st_borrow` | 短期借款 |
| `notes_payable` | 应付票据 |
| `acct_payable` | 应付账款 |
| `adv_from_cust` | 预收款项 |
| `tot_non_cur_liab` | 非流动负债合计 |
| `lt_borrow` | 长期借款 |
| `bonds_payable` | 应付债券 |
| `tot_equity` | 所有者权益合计 |
| `cap_stk` | 股本 |
| `cap_rsrv` | 资本公积 |
| `surplus_rsrv` | 盈余公积 |
| `undist_profit` | 未分配利润 |
| `minority_int` | 少数股东权益 |

---

## 现金流量表字段 (w.wss, rptDate=xxx)

| 字段 | 含义 |
|------|------|
| `net_cash_flows_oper_act` | 经营活动净现金流 |
| `cash_recp_sg_and_rs` | 销售商品收到的现金 |
| `cash_pay_goods_purch_serv_rec` | 购买商品支付的现金 |
| `net_cash_flows_inv_act` | 投资活动净现金流 |
| `cash_recp_disp_withdrwl_invest` | 收回投资收到的现金 |
| `cash_pay_acq_const_fiolta` | 购建固定资产支付的现金 |
| `net_cash_flows_fnc_act` | 筹资活动净现金流 |
| `cash_recp_cap_contrib` | 吸收投资收到的现金 |
| `cash_pay_dist_dpcp_int_exp` | 分配股利支付的现金 |
| `net_incr_cash_cash_equ` | 现金净增加额 |
| `free_cash_flow` | 自由现金流 |

---

## 资金流向字段 (w.wsd)

| 字段 | 含义 |
|------|------|
| `mfd_inflow_xl` | 超大单净流入(元) |
| `mfd_inflow_l` | 大单净流入 |
| `mfd_inflow_m` | 中单净流入 |
| `mfd_inflow_s` | 小单净流入 |
| `mfd_inflow` | 主力净流入 |
| `mfd_vol_xl` | 超大单成交量 |
| `mfd_vol_l` | 大单成交量 |
| `mfd_vol_m` | 中单成交量 |
| `mfd_vol_s` | 小单成交量 |

---

## 业绩预告字段 (w.wss, year=xxx)

| 字段 | 含义 |
|------|------|
| `profitnotice_date` | 预告日期 |
| `profitnotice_style` | 预告类型(预增/预减/扭亏等) |
| `profitnotice_netprofitmin` | 预告净利润下限(万) |
| `profitnotice_netprofitmax` | 预告净利润上限(万) |
| `profitnotice_changemin` | 变动幅度下限(%) |
| `profitnotice_changemax` | 变动幅度上限(%) |
| `profitnotice_reason` | 变动原因 |

## 业绩快报字段 (w.wss, rptDate=xxx)

| 字段 | 含义 |
|------|------|
| `expr_discdate` | 披露日期 |
| `expr_oper_rev` | 营业收入 |
| `expr_oper_profit` | 营业利润 |
| `expr_tot_profit` | 利润总额 |
| `expr_net_profit_parent_comp` | 归母净利润 |
| `expr_eps_basic` | 基本每股收益 |
| `expr_bps` | 每股净资产 |
| `expr_roe_diluted` | ROE(摊薄) |
| `expr_yoy_oper_rev` | 营收同比(%) |
| `expr_yoy_net_profit` | 净利润同比(%) |
