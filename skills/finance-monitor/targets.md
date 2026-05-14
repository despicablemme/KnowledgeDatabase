# Finance Monitor - 监控标的列表

## 美股指数

| 代码 | 名称 | 类型 |
|------|------|------|
| ^DJI | 道琼斯 | index |
| ^GSPC | 标普500 | index |
| ^IXIC | 纳斯达克 | index |

## 个股

| 代码 | 名称 | 类型 |
|------|------|------|
| GOOGL | Google | stock |
| AAPL | Apple | stock |
| TSLA | Tesla | stock |
| SNDK | SanDisk | stock |
| WDC | Western Digital（西部数据） | stock |
| NVDA | Nvidia | stock |
| INTC | Intel | stock |

## 汇率

| 代码 | 名称 | 类型 |
|------|------|------|
| CNH=X | 离岸人民币(CNH) | fx |
| CNY=X | 在岸人民币(CNY) | fx |

---

如需修改标的，编辑此文件后同步到 `scripts/fetch_data.py` 中的 STOCKS 和 CURRENCIES 字典。