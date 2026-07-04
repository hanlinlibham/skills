# iFinD 历史行情 (cmd_history_quotation) 指标完整列表

## 通用指标（股票/基金/指数/债券/期货/期权）

| 指标名 | 说明 | 备注 |
|--------|------|------|
| preClose | 前收盘价 | |
| open | 开盘价 | |
| high | 最高价 | |
| low | 最低价 | |
| close | 收盘价 | |
| avgPrice | 均价 | |
| change | 涨跌 | |
| changeRatio | 涨跌幅 | |
| volume | 成交量 | |
| amount | 成交额 | |
| turnoverRatio | 换手率 | |
| transactionAmount | 成交笔数 | |

## 股票专用

| 指标名 | 说明 |
|--------|------|
| totalShares | 总股本 |
| totalCapital | 总市值 |
| floatSharesOfAShares | A股流通股本 |
| floatSharesOfBShares | B股流通股本 |
| floatCapitalOfAShares | A股流通市值 |
| floatCapitalOfBShares | B股流通市值 |
| pe_ttm | 市盈率（TTM）|
| pe | PE市盈率 |
| pb | PB市净率 |
| ps | PS市销率 |
| pcf | PCF市现率 |
| ths_trading_status_stock | 交易状态 |
| ths_up_and_down_status_stock | 涨跌停状态 |
| ths_af_stock | 复权因子 |
| ths_vol_after_trading_stock | 盘后成交量 |
| ths_trans_num_after_trading_stock | 盘后成交笔数 |
| ths_amt_after_trading_stock | 盘后成交额 |
| ths_vaild_turnover_stock | 有效换手率 |

## 基金专用

| 指标名 | 说明 |
|--------|------|
| netAssetValue | 单位净值 |
| adjustedNAV | 复权单位净值 |
| accumulatedNAV | 累计单位净值 |
| premium | 贴水 |
| premiumRatio | 贴水率 |
| estimatedPosition | 估算仓位 |

## 指数专用

| 指标名 | 说明 |
|--------|------|
| floatCapital | 流通市值 |
| pe_ttm_index | PE(TTM) |
| pb_mrq | PB(MRQ) |
| pe_indexPublisher | PE(指数发布方) |

## 债券专用

| 指标名 | 说明 |
|--------|------|
| yieldMaturity | 到期收益率 |
| remainingTerm | 剩余期限 |
| maxwellDuration | 麦氏久期 |
| modifiedDuration | 修正久期 |
| convexity | 凸性 |

## 外汇专用

| 指标名 | 说明 |
|--------|------|
| close_2330 | 收盘价（23:30）|

## 期货/期权专用

| 指标名 | 说明 |
|--------|------|
| openInterest | 持仓量 |
| positionChange | 持仓变动 |
| preSettlement | 前结算价 |
| settlement | 结算价 |
| change_settlement | 涨跌（结算价）|
| chg_settlement | 涨跌幅（结算价）|
| amplitude | 振幅 |

## functionpara 参数

| 名称 | key | 值说明 | 默认 |
|------|-----|--------|------|
| 时间周期 | Interval | D-日 W-周 M-月 Q-季 S-半年 Y-年（返回周期汇总统计值） | D |
| 抽样周期 | SampleInterval | D W M Q S Y（返回周期最后一个交易日数据） | D |
| 复权方式 | CPS | 1-不复权 2-前复权(分红再投) 3-后复权(分红再投) 4-全流通前复权(分红再投) 5-全流通后复权(分红再投) 6-前复权(现金分红) 7-后复权(现金分红) | 1(不复权) |
| 报价类型 | PriceType | 1-全价 2-净价（仅债券生效） | 1(全价) |
| 非交易间隔处理 | Fill | Previous-沿用前值 Blank-空值 具体数值 Omit-缺省值 | Previous |
| 复权基点日期 | BaseDate | "YYYY-MM-DD" | 后复权按上市日，前复权按最新日 |
| 货币 | Currency | MHB-美元 GHB-港元 RMB-人民币 YSHB-原始货币 | YSHB(原始货币) |
