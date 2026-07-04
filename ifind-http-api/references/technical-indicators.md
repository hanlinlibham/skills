# iFinD 高频序列技术指标参数参考

在 high_frequency 接口中使用技术指标时，需在 `functionpara.calculate` 中为每个技术指标设置参数。

## 使用方式

```python
"functionpara": {
    "Interval": "5",
    "calculate": {
        "MACD": "12,26,9,MACD",   # 参数用半角逗号拼接
        "KDJ": "9,3,3,K"
    }
}
```

技术指标需同时出现在 `indicators` 字段中。

## 趋势指标

| 指标名 | 说明 | 参数格式 |
|--------|------|---------|
| BBI | BBI多空指数 | {周期1},{周期2},{周期3},{周期4} |
| MA | MA简单移动平均 | {周期} |
| EXPMA | EXPMA指数平均数 | {周期} |
| DMA | DMA平均线差 | {短周期},{长周期},{周期},{DDD or AMA} |
| BOLL | BOLL布林线 | {宽带},{MID or UPPER or LOWER} |
| BBIBOLL | BBIBOLL多空布林线 | {周期},{宽带},{BBIBOLL or UPR or DWN} |
| ENV | ENV指标 | {周期},{UPPER or LOWER} |
| MIKE | MIKE麦克指标 | {周期},{WR or MR or SR or WS or MS or SS} |

## 震荡指标

| 指标名 | 说明 | 参数格式 |
|--------|------|---------|
| MACD | MACD指数平滑异同平均 | {短周期},{长周期},{周期},{DIFF or DEA or MACD} |
| KDJ | KDJ随机指标 | {周期},{周期1},{周期2},{K or D or J} |
| RSI | RSI相对强弱指标 | {周期} |
| CCI | CCI顺势指标 | {周期} |
| BIAS | BIAS乖离率 | {周期} |
| WR | WR威廉指标 | {周期} |
| MTM | MTM动力指标 | {间隔周期},{周期},{MTM or MTMMA} |
| ROC | ROC变动速率 | {间隔周期},{周期},{ROC or ROCMA} |
| DDI | DDI方向标准离差指数 | {周期1},{周期2},{平滑因子},{周期3},{DDI or ADDI or AD} |
| TRIX | TRIX三重指数平滑平均 | {周期1},{周期2},{TRIX or TRMA} |
| DBCD | DBCD异同离差乖离率 | {周期1},{周期2},{周期3},{DBCD or MM} |
| DPO | DPO区间震荡线 | {周期1},{周期2},{DPO or MADPO} |
| LWR | LWR威廉指标 | {周期},{周期1},{周期2},{LWR1 or LWR2} |
| SI | SI摆动指标 | （无参数） |
| PRICEOSC | PRICEOSC价格振荡指标 | {短周期},{长周期} |

## 量能指标

| 指标名 | 说明 | 参数格式 |
|--------|------|---------|
| VR | VR成交量比率 | {周期} |
| OBV | OBV能量潮 | {OBV or OBV_XZ} |
| PVT | PVT量价趋势指标 | （无参数） |
| VROC | VROC量变动速率 | {周期} |
| VRSI | VRSI量相对强弱 | {周期} |
| WVAD | WVAD威廉变异离散量 | {周期1},{周期2},{WVAD or MAWVAD} |
| MFI | MFI资金流向指标 | {周期} |
| WAD | WAD威廉聚散指标 | {周期},{WAD or MAWAD} |
| VMA | VMA量简单移动平均 | {周期} |
| VMACD | VMACD量指数平滑异同平均 | {短周期},{长周期},{周期},{DIFF or DEA or MACD} |
| VOSC | VOSC成交量震荡 | {短周期},{长周期} |
| LB | 量比 | {周期} |
| VSTD | VSTD成交量标准差 | {周期} |

## 人气意愿指标

| 指标名 | 说明 | 参数格式 |
|--------|------|---------|
| ARBR | ARBR人气意愿指标 | {周期},{AR or BR} |
| CR | CR能量指标 | {周期} |
| PSY | PSY心理指标 | {周期1},{周期2},{PSY or MAPSY} |
| SRDM | SRDM动向速度比率 | {周期},{SRDM or ASRDM} |

## 其他指标

| 指标名 | 说明 | 参数格式 |
|--------|------|---------|
| TAPI | TAPI加权指数成交值 | {周期},{TAPI or MATAPI} |
| ADTM | ADTM动态买卖气指标 | {周期},{周期1},{ADTM or MAADTM} |
| MI | MI动量指标 | {周期},{A or MI} |
| MICD | MICD异同离差动力指数 | {周期},{周期1},{周期2},{DIF or MICD} |
| RC | RC变化率指数 | {周期} |
| RCCD | RCCD异同离差变化率指数 | {周期},{周期1},{周期2},{DIF or RCCD} |
| SRMI | SRMI(MI修正指标) | {周期} |
| DPTB | DPTB大盘同步指标 | {周期},{000001 or 000010 or 399001 or 000300} |
| JDQS | JDQS阶段强势指标 | {周期},{000001 or 000010 or 399001 or 000300} |
| JDRS | JDRS阶段弱势指标 | {周期},{000001 or 000010 or 399001 or 000300} |
| ZDZB | ZDZB筑底指标 | {周期},{周期1},{周期2},{B or D} |
| ATR | ATR真实波幅 | {周期},{TR or ATR} |
| MASS | MASS梅丝线 | {周期1},{周期2} |
| STD | STD标准差 | {周期} |
| VHF | VHF纵横指标 | {周期} |
| CVLT | CVLT佳庆离散指标 | {周期} |
| CDP | CDP逆势操作 | {CDP or AH or AL or NH or NL} |

## 资金流向指标（分时）

| 指标名 | 说明 | 适用 |
|--------|------|------|
| large_amt_timeline | 主力净流入金额(分时) | 股票 |
| active_buy_large_volume | 主动买入特大单量 | 股票,同花顺指数 |
| active_sell_large_volume | 主动卖出特大单量 | 股票,同花顺指数 |
| active_buy_main_volume | 主动买入大单量 | 股票,同花顺指数 |
| active_sell_main_volume | 主动卖出大单量 | 股票,同花顺指数 |
| active_buy_middle_volume | 主动买入中单量 | 股票,同花顺指数 |
| active_sell_middle_volume | 主动卖出中单量 | 股票,同花顺指数 |
| possitive_buy_large_volume | 被动买入特大单量 | 股票,同花顺指数 |
| possitive_sell_large_volume | 被动卖出特大单量 | 股票,同花顺指数 |
| active_buy_large_amount | 主动买入特大单金额 | 股票,同花顺指数 |
| active_sell_large_amount | 主动卖出特大单金额 | 股票,同花顺指数 |
| openInterest | 持仓量 | 期权,期货 |
| changeRatio_periodical | 涨跌幅(阶段) | 期权专用 |
