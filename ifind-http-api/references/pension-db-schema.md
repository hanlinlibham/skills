# 养老金产品数据库 Schema

## 数据库文件

`data/pension_products.db` — SQLite 3，使用 WAL 模式。

## 表结构

### pension_products（主表）

| 列名 | 类型 | 说明 |
|------|------|------|
| code | TEXT PK | 产品代码，如 `PAA001.YLJ` |
| name | TEXT | 基金简称 |
| official_name | TEXT | 官方简称 |
| manager_prefix | TEXT | 管理人前缀，如 `PA` |
| manager_name | TEXT | 管理人名称，如 `平安养老` |
| product_type | TEXT | 类型字母：A/B/C/D |
| product_type_name | TEXT | 类型名称：权益型/混合型/债券型/货币型 |
| bond_subtype | TEXT | 债券子类：Ca/Cb/Cc/Cf/Cg/Ch（仅 C 类有值） |
| bond_subtype_name | TEXT | 债券子类名称 |
| establishment_date | TEXT | 成立日期 |
| expiry_date | TEXT | 到期日期 |
| last_updated | TEXT | 最后更新时间 |

### pension_fts（FTS5 全文搜索虚拟表）

索引字段：code, name, official_name, manager_name, product_type_name

与 pension_products 通过触发器自动同步。

## 索引

| 索引名 | 列 |
|--------|------|
| idx_name | name |
| idx_manager | manager_prefix |
| idx_type | product_type |

## 管理人前缀对照

| 前缀 | 管理人 |
|------|--------|
| 00 | 全国社保基金理事会 |
| 02 | 博时基金 |
| 05 | 大成基金 |
| 07 | 工银瑞信 |
| 10 | 海富通基金 |
| 11 | 华夏基金 |
| 15 | 嘉实基金 |
| 18 | 南方基金 |
| 20 | 鹏华基金 |
| 48 | 易方达基金 |
| 51 | 银华基金 |
| CJ | 长江养老 |
| CL | 长城人寿 |
| HT | 华泰资产 |
| JX | 建信养老金 |
| LC | 长量基金 |
| PA | 平安养老 |
| RB | 人保资产 |
| TP | 太平养老 |
| TZ | 泰康资产 |
| XH | 新华养老 |
| ZJ | 中金公司 |
| ZX | 中信证券 |

## 数据构建

```bash
# 首次构建
export IFIND_REFRESH_TOKEN="your_token"
python scripts/build_pension_db.py

# 指定源文件和输出路径
python scripts/build_pension_db.py --source ~/Space/ifind/基础信息数据.md --db-path data/pension_products.db

# 直接使用 access_token
python scripts/build_pension_db.py --access-token "your_access_token"
```

构建脚本会自动从 `基础信息数据.md` 提取 1722 个 `.YLJ` 代码，分批（每批 50 个）调用 `basic_data_service` 获取基金简称、官方简称、成立日、到期日，并通过代码模式解析管理人和产品类型。

## 常用查询示例

```sql
-- 搜索包含"增值"的产品
SELECT code, name, manager_name FROM pension_products WHERE name LIKE '%增值%';

-- 平安养老的权益型产品
SELECT code, name FROM pension_products WHERE manager_prefix = 'PA' AND product_type = 'A';

-- 各管理人产品数量统计
SELECT manager_name, COUNT(*) as cnt FROM pension_products GROUP BY manager_prefix ORDER BY cnt DESC;

-- 各类型产品数量
SELECT product_type_name, COUNT(*) FROM pension_products GROUP BY product_type;

-- 拼接代码串供 API 调用
SELECT GROUP_CONCAT(code) FROM pension_products WHERE manager_prefix = 'PA' AND product_type = 'A';
```
