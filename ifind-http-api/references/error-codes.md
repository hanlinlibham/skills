# iFinD HTTP API 错误码完整列表

| 错误码 | 错误信息 | 中文提示 |
|--------|--------|--------|
| 0 | Success | 成功 |
| -1010 | your account has been logged out | token 已失效 |
| -1000 | datasvr error! | 数据服务器错误 |
| -1001 | gwsvr error! | 网关服务器错误 |
| -1002 | timeout! | 超时 |
| -1003 | access-token can not be empty! | 传值不能为空 |
| -1004 | datasvrhq error! | 数据服务器错误 |
| -1005 | auth user error! | 用户验证错误 |
| -1201 | failed, please change your input condition | 查询失败 |
| -1202 | there are errors in your parameters | 参数错误 |
| -1203 | parsing failed | 解析失败 |
| -1300 | Not legal User | token 无效 |
| -1301 | Refresh_Token is expired or illegal | refresh_token 无效 |
| -1302 | Access_Token is expired or illegal | access_token 无效 |
| -1303 | Device exceed limit | access_token 绑定超过 20 个 IP |
| -1305 | Exceeded the maximum number of token acquisitions for the day | 每天请求 token 次数超过限制 |
| -4001 | no data | 数据为空 |
| -4100 | please log in first! | 请先登录 iFind |
| -4101 | database execution error | 数据库执行错误 |
| -4102 | server internal error | 服务端请求超时 |
| -4103 | unreasonable request! your account has been locked | 超时请求过多，账号被锁 |
| -4201 | the data server is incorrect | 数据服务器取值错误 |
| -4203 | request format is wrong | 请求格式错误 |
| -4204 | wrong time format | 错误的时间格式 |
| -4205 | the start time can not be greater than the end time | 开始时间不能大于结束时间 |
| -4206 | include the wrong thscode | 含有错误的同花顺代码 |
| -4207 | currently we do not support bonds of this market | 不支持银行间债券 |
| -4208 | currently we just support SSE, SZSE and CFFEX | 仅支持上交所/深交所 |
| -4209 | startDate and endDate of Snapshot should be the same | snap_shot 起始结束日期要求同一天 |
| -4210 | error happen with input parameters | 输入参数错误 |
| -4211 | there is no trading date in the date range | 时间区间内无交易日 |
| -4212 | the input endDate is earlier than the listDates | 时间区间内股票未上市 |
| -4213 | startDate can't later than endDate | 开始日期大于截止日期 |
| -4230 | no permission for real-time US stock market quotes | 没有美股实时行情权限 |
| -4301 | basic data has exceeded 5 million this week | 本周基础数据提取超 500 万条 |
| -4302 | quote data has exceeded 150 million this week | 本周报价数据提取超 1.5 亿条 |
| -4303 | EDB data has exceeded 5 million this week | 本周 EDB 数据提取超 500 万条 |
| -4304 | HighFrequenceSequence can support 200W data at most | 高频序列单条命令数据量过大 |
| -4305 | BasicData can support 20W data at most | 基础数据单条命令数据量过大 |
| -4306 | Snapshot can support 200W data at most | 快照单条命令数据量过大 |
| -4307 | data extraction is overrun | 数据提取量超限 |
| -4308 | range between startDate and endDate must be smaller than 1 month | 请求区间不能超过一个月 |
| -4309 | trial account can get 1 year data for authority limited | 试用账号超出时间限制（1年） |
| -4310 | trial account can get 1 month data for authority limited | 试用账号超出时间限制（1个月） |
| -4311 | trial account can get 5 year data for authority limited | 试用账号超出时间限制（5年） |
| -4312 | HistoryQuotes can support 200W data at most | 历史行情超出 200W 限制 |
| -4313 | interval should be smaller than 3 years | 开始与结束时间间隔不能超过 3 年 |
| -4314 | interval should be smaller than 6 months | 间隔不能超过 6 个月 |
| -4315 | interval should be smaller than 3 months | 间隔不能超过 3 个月 |
| -4316 | interval should be smaller than 1 year | 间隔不能超过 1 年 |
| -4317 | usage of data has exceeded 1w this week | 本周数据量超过 1 万 |
| -4318 | usage of data has exceeded this month | 本月使用量已经超限 |
| -4319 | free Account can support 5W data at most | 免费用户单条命令数据量过大（5W） |
| -4320 | your account must use the corresponding client | 账户必须使用对应客户端 |
| -4321 | free Account can support 10W data at most | 免费账号单次提取限制 10 万 |
| -4322 | free Account can support 1W data at most | 免费用户单条命令请求数据量过大（1W） |
| -4400 | we just support 600 requests per minute | 每分钟最多支持 600 条请求 |
| -5001 | data server parameter error | 远程服务器参数错误 |
| -5002 | data server is busy now | 查询失败 |
| -5003 | does not support the stock box selection calculation | 不支持该股权查询 |
| -5004 | data process waiting timeout | 等待超时 |
| -5005 | data calculation error | 计算错误 |
| -5006 | data process query failed | 查询失败 |
| -5007 | data process Waiting for calculation | 等待计算 |
| -5008 | data process calculating | 正在计算 |
| -5009 | must complete the last instruction request | 必须完成上一次计算请求 |
| -5010 | only supports single code incoming | 仅支持单代码传入 |
| -5000 | please enter a reasonable expected dividend growth rate | 请输入合理的预期红利增长率数值 |
| -5100 | account type is not supported | 账户类型不支持 |
| -5101 | please confirm you have not used the amount of date for the month | 请确认尚未使用本月的数据量 |
| -5102 | you have exceeded the maximum number of clears | 已超过最大清零次数 |
| -5103 | Do not allow accounts to operate in unbound mac code environments | 不允许账户在非绑定 mac 代码环境中运行 |
| -5104 | this mac code has been bound | 该机器的 mac 已被绑定 |
