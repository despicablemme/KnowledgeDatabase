---
name: accounting
description: 记账技能。当用户提到收入、支出、工资、消费、花了多少钱、结余、每月支出、年度总结等财务相关话题时使用此技能。支持：(1) 记录收入（如"本月收入5000"、"工资8000"）；(2) 记录支出（如"买衣服花了200"、"吃饭支出50元"）；(3) 自动分类支出（饮食/娱乐/学习/交通等）；(4) 查询余额、每月/每年收支报告、支出分类占比；(5) 支出分类统计和趋势分析。
---

# 记账技能 (Accounting)

## 数据库结构

数据库位置：`~/.openclaw/workspace/skills/accounting/scripts/accounting.db`

**表结构：**
- `transactions` - 每笔收支明细（type/amount/category/description/date）
- `balance` - 储蓄余额记录（按日期追踪）
- `weekly_summary` - 周收支汇总（year/week/total_income/total_expense/category_expenses）
- `monthly_summary` - 月收支汇总（year/month/total_income/total_expense/category_expenses）
- `yearly_summary` - 年收支汇总（year/total_income/total_expense/category_expenses）

## 核心脚本

**主脚本：** `scripts/accounting.py`

```bash
# 初始化数据库
python3 scripts/accounting.py init

# 记录收入
python3 scripts/accounting.py income <金额> [描述] [日期]

# 记录支出（自动分类）
python3 scripts/accounting.py expense <金额> [描述] [日期]

# 查询余额
python3 scripts/accounting.py balance [日期]

# 月度报告
python3 scripts/accounting.py month [年] [月]

# 年度报告
python3 scripts/accounting.py year [年]

# 周报告
python3 scripts/accounting.py week [年] [周]

# 最近记录
python3 scripts/accounting.py recent [条数]
```

## 自然语言识别规则

### 收入记录
当用户说"本月收入**"、"这个月工资**"、"工资**"、"收入**"时：
1. 提取金额
2. 调用 `accounting.py income <金额> [描述]`
3. 返回当前余额

### 支出记录
当用户说"买**支出¥**"、"做什么花了**钱"、"花了**元"、"消费**"时：
1. 提取金额和用途描述
2. 调用 `accounting.py expense <金额> [描述]`
3. 自动根据描述分类（饮食/娱乐/学习/交通/购物/医疗/住房/通讯/社交/运动/其他）
4. 返回当前余额

### 查询请求
- "结余多少" → `balance`
- "本月支出" → `month`（当前年月）
- "这个月花了多少钱" → `month`
- "每月支出" → `month` 当前月
- "年度总结" → `year` 当前年
- "某年支出" → `year <年份>`

## 记账规则

- 发薪方式：**月薪制**（不是周薪）
- 发薪时用户会提醒你，你来记录收入
- 没有周收入，汇总时收入那边为0或等于月薪
- 所有金额单位：元
- 日期不填默认当天

## 自动分类逻辑

脚本 `accounting.py` 内置 `CATEGORY_KEYWORDS` 映射，根据描述关键词自动分类：

| 分类 | 关键词 |
|------|--------|
| 饮食 | 吃饭、外卖、餐厅、食物、零食、水果、饮料、买菜 |
| 娱乐 | 电影、游戏、音乐、演出、展览、旅游、KTV、酒吧 |
| 学习 | 书、课程、培训、学费、文具、教育、考试、资料 |
| 交通 | 打车、地铁、公交、火车、飞机、停车、油费 |
| 购物 | 衣服、鞋子、化妆品、电器、日用品、网购 |
| 医疗 | 医院、药品、体检、牙科、药店 |
| 住房 | 房租、水电、物业、房贷、装修 |
| 通讯 | 手机、话费、网络、宽带、流量 |
| 社交 | 请客、送礼、红包、份子、朋友、聚会 |
| 运动 | 健身、跑步、游泳、瑜伽 |

## 输出格式

查询结果以格式化表格/文字输出，包含：
- 收入/支出/结余金额
- 支出分类占比（含可视化条形图）
- 月度/年度趋势

## 注意事项

1. **首次使用需初始化数据库**：`python3 scripts/accounting.py init`
2. 所有金额单位为"元"
3. 日期格式：`YYYY-MM-DD`（不填默认今天）
4. 支出描述尽量写清楚用途，便于自动分类
5. 主人可随时查询任意时间范围的收支情况