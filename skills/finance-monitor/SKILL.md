---
name: finance-monitor
description: 监控美股指数、个股实时行情及人民币汇率，并通过 QQ 机器人推送日报/定时播报。
metadata: {"openclaw":{"emoji":"📊"}}
---

# Finance Monitor - 金融行情监控

## 功能概述

- 📈 **美股指数**：道琼斯(DJIA)、标普500(SPX)、纳斯达克(NDX)
- 💹 **个股**：Google(GOOGL)、Apple(AAPL)、Tesla(TSLA)、SanDisk(SNDK)、Western Digital(WDC)、Nvidia(NVDA)、Intel(INTC)
- 💱 **人民币汇率**：离岸(CNH) + 在岸(CNY) 对美元

## 数据来源

- 股票/指数/汇率：Yahoo Finance 公开 API（直接 HTTP 调用，无需 yfinance）

## 监控标的

详细列表见 [targets.md](./targets.md)，包含：

- **美股指数**：道琼斯(DJIA)、标普500(SPX)、纳斯达克(NDX)
- **个股**：Google(GOOGL)、Apple(AAPL)、Tesla(TSLA)、SanDisk(SNDK)、Western Digital(WDC)、Nvidia(NVDA)、Intel(INTC)
- **汇率**：离岸人民币(CNH)、在岸人民币(CNY)

修改标的时：编辑 `targets.md` → 同步到 `scripts/fetch_data.py` 中的 STOCKS/CURRENCIES 字典

### 手动查询（通过 QQ 发送指令）

```
/finance today
```

→ 返回当日所有监控标的最新数据

### 自动定时推送

启动后自动按设定时间推送，用户通常设：
- 开盘前推送（如每天 09:25）
- 盘中整点推送（如 11:00、13:00、14:00、15:00）
- 盘后推送（如每天 16:00）

## 消息格式

```
📊 市场早报 - 2026-05-10 09:25

【指数】
 道琼斯: 42,876.50 ▲ +0.32%
 标普500: 5,842.75 ▲ +0.28%
 纳斯达克: 18,432.80 ▲ +0.45%

【个股】
 GOOGL: $182.35 ▲ +1.23%
 AAPL: $189.42 ▼ -0.15%
 TSLA: $248.60 ▲ +2.10%
 WDC:  $68.20 ▲ +0.88%
 NVDA: $875.30 ▲ +3.45%
 INTC: $42.15 ▼ -0.62%

【汇率】
 离岸人民币(CNH): 7.2450 ▲ +0.15%
 在岸人民币(CNY): 7.2380 ▲ +0.12%
```

## 脚本执行

```bash
# 查询当日行情
python3 ~/.openclaw/skills/finance-monitor/scripts/fetch_data.py

# 查询特定标的
python3 ~/.openclaw/skills/finance-monitor/scripts/fetch_data.py GOOGL AAPL TSLA

# 查看帮助
python3 ~/.openclaw/skills/finance-monitor/scripts/fetch_data.py --help
```

## 依赖安装

如果 yfinance 未安装，自动提示安装：
```bash
pip3 install yfinance
```

## Cron 定时任务示例

可通过 cron 定时触发，实现每日自动推送：
```json
{
  "schedule": { "kind": "cron", "expr": "0 9,11,13,14,15,16 * * 1-5", "tz": "Asia/Shanghai" },
  "payload": { "kind": "agentTurn", "message": "执行 fetch_data.py 并将结果通过 QQ 发送给用户" }
}
```

## 注意事项

- 美股交易时间（北京时间 22:30-05:00），盘后数据可能滞后
- 汇率 24 小时交易，实时更新
- 中国大陆访问 Yahoo Finance 可能需要代理