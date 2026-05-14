#!/usr/bin/env python3
"""
Finance Monitor - 美股/指数/汇率详细行情
支持：开盘价、收盘价、日趋势、周趋势、月趋势
"""

import sys
import json
import requests
from datetime import datetime, timedelta

# ==================== 配置 ====================
STOCKS = {
    "^DJI":  {"name": "道琼斯",      "type": "index"},
    "^GSPC": {"name": "标普500",     "type": "index"},
    "^IXIC": {"name": "纳斯达克",    "type": "index"},
    "GOOGL": {"name": "Google",      "type": "stock"},
    "AAPL":  {"name": "Apple",       "type": "stock"},
    "TSLA":  {"name": "Tesla",       "type": "stock"},
    "SNDK":  {"name": "SanDisk",     "type": "stock"},
    "WDC":   {"name": "Western Digital", "type": "stock"},
    "NVDA":  {"name": "Nvidia",      "type": "stock"},
    "INTC":  {"name": "Intel",       "type": "stock"},
}

CURRENCIES = {
    "CNH=X": {"name": "离岸人民币(CNH)", "type": "fx"},
    "CNY=X": {"name": "在岸人民币(CNY)", "type": "fx"},
}

HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}


def fetch_intraday(symbol: str) -> dict:
    """获取当日分时数据：开盘价、盘中高低、当前价"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        result = data["chart"]["result"]
        if not result:
            return {"symbol": symbol, "error": "No data"}

        r_data = result[0]
        timestamps = r_data["timestamp"]
        quotes = r_data["indicators"]["quote"][0]

        closes = [c for c in quotes["close"] if c is not None]
        highs = [h for h in quotes["high"] if h is not None]
        lows = [l for l in quotes["low"] if l is not None]
        opens = [o for o in quotes["open"] if o is not None]

        if not closes:
            return {"symbol": symbol, "error": "No valid data"}

        current_price = closes[-1]
        day_open = opens[0] if opens else closes[0]
        day_high = max(highs) if highs else current_price
        day_low = min(lows) if lows else current_price
        prev_close = closes[0]  # 第一个数据点作为昨日收盘参考

        change = current_price - prev_close
        change_pct = (change / prev_close * 100) if prev_close else 0

        return {
            "symbol": symbol,
            "price": round(current_price, 2),
            "open": round(day_open, 2),
            "high": round(day_high, 2),
            "low": round(day_low, 2),
            "prev_close": round(prev_close, 2),
            "change": round(change, 2),
            "change_pct": round(change_pct, 2),
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def fetch_historical(symbol: str, days: int = 5) -> dict:
    """获取历史数据：日、周、月趋势"""
    try:
        range_str = f"{days}d" if days <= 30 else "1mo"
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range={range_str}"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        result = data["chart"]["result"]
        if not result:
            return None

        r_data = result[0]
        timestamps = r_data["timestamp"]
        quotes = r_data["indicators"]["quote"][0]

        closes = [c for c in quotes["close"] if c is not None]
        timestamps_valid = [t for t, c in zip(timestamps, quotes["close"]) if c is not None]

        if not closes:
            return None

        # 计算趋势：起始 vs 当前
        period_start = closes[0]
        period_end = closes[-1]
        period_change = period_end - period_start
        period_change_pct = (period_change / period_start * 100) if period_start else 0

        # 最高/最低
        period_high = max(c for c in closes if c is not None)
        period_low = min(c for c in closes if c is not None)

        # 近 N 日数据列表
        recent = []
        for i, (t, c) in enumerate(zip(timestamps_valid, closes)):
            dt = datetime.fromtimestamp(t)
            emoji = "▲" if i > 0 and c > closes[i-1] else "▼" if i > 0 and c < closes[i-1] else "—"
            recent.append({
                "date": dt.strftime("%m-%d"),
                "close": round(c, 2),
                "emoji": emoji
            })

        return {
            "start_price": round(period_start, 2),
            "end_price": round(period_end, 2),
            "change": round(period_change, 2),
            "change_pct": round(period_change_pct, 2),
            "high": round(period_high, 2),
            "low": round(period_low, 2),
            "recent": recent
        }
    except Exception as e:
        return None


def fetch_fx(symbol: str) -> dict:
    """获取汇率数据"""
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        result = data["chart"]["result"]
        if not result:
            return {"symbol": symbol, "error": "No data"}

        closes = result[0]["indicators"]["quote"][0]["close"]
        valid = [c for c in closes if c is not None]

        if len(valid) >= 2:
            current = valid[-1]
            prev = valid[-2]
        elif len(valid) == 1:
            current = prev = valid[-1]
        else:
            return {"symbol": symbol, "error": "No valid data"}

        change = current - prev
        change_pct = (change / prev * 100) if prev else 0

        return {
            "symbol": symbol,
            "price": round(current, 4),
            "prev_close": round(prev, 4),
            "change": round(change, 4),
            "change_pct": round(change_pct, 2),
            "period": "5日"
        }
    except Exception as e:
        return {"symbol": symbol, "error": str(e)}


def format_stock_detail(symbol: str, info: dict, weekly: dict, monthly: dict) -> str:
    """格式化个股/指数详细数据"""
    meta = STOCKS[symbol]
    emoji = "▲" if info["change"] >= 0 else "▼"
    sign = "+" if info["change"] >= 0 else ""

    lines = []
    lines.append(f"{meta['name']}({symbol})")
    lines.append(f"  当前: {info['price']} {emoji} {sign}{info['change_pct']}%")

    # 今日开盘/收盘数据
    emoji_open = "▲" if info["open"] >= info["prev_close"] else "▼"
    lines.append(f"  今日开盘: {info['open']} (昨收: {info['prev_close']})")
    lines.append(f"  日内高点: {info['high']} / 日内低点: {info['low']}")

    # 分隔线
    lines.append(f"  ─── 趋势 ───")

    # 周趋势
    if weekly:
        we = "▲" if weekly["change"] >= 0 else "▼"
        ws = "+" if weekly["change"] >= 0 else ""
        lines.append(f"  周趋势({weekly['recent'][0]['date']}→{weekly['recent'][-1]['date']}): {weekly['start_price']}→{weekly['end_price']} {we}{ws}{weekly['change_pct']}%  高{weekly['high']} 低{weekly['low']}")

    # 月趋势
    if monthly:
        me = "▲" if monthly["change"] >= 0 else "▼"
        ms = "+" if monthly["change"] >= 0 else ""
        lines.append(f"  月趋势({monthly['recent'][0]['date']}→{monthly['recent'][-1]['date']}): {monthly['start_price']}→{monthly['end_price']} {me}{ms}{monthly['change_pct']}%  高{monthly['high']} 低{monthly['low']}")

    return "\n".join(lines)


def format_fx_detail(symbol: str, info: dict) -> str:
    """格式化汇率数据"""
    meta = CURRENCIES[symbol]
    emoji = "▲" if info["change"] >= 0 else "▼"
    sign = "+" if info["change"] >= 0 else ""
    return f"{meta['name']}: {info['price']} {emoji} {sign}{info['change_pct']}% (昨收: {info['prev_close']})"


def main():
    results = []
    for sym in list(STOCKS.keys()) + list(CURRENCIES.keys()):
        if sym in CURRENCIES:
            results.append(("fx", sym, fetch_fx(sym)))
        else:
            # 股票/指数：同时获取日、周、月数据
            intraday = fetch_intraday(sym)
            weekly = fetch_historical(sym, 5)
            monthly = fetch_historical(sym, 30)
            results.append(("stock", sym, intraday, weekly, monthly))

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    print(f"📊 市场详细播报 - {now}")
    print()

    # 指数
    print("【指数】")
    for sym in ["^DJI", "^GSPC", "^IXIC"]:
        _, _, info, weekly, monthly = next(r for r in results if r[1] == sym)
        if "error" not in info:
            print(format_stock_detail(sym, info, weekly, monthly))
    print()

    # 个股
    stock_symbols = ["GOOGL", "AAPL", "TSLA", "SNDK", "WDC", "NVDA", "INTC"]
    print("【个股】")
    for sym in stock_symbols:
        _, _, info, weekly, monthly = next(r for r in results if r[1] == sym)
        if "error" not in info:
            print(format_stock_detail(sym, info, weekly, monthly))
    print()

    # 汇率
    print("【汇率】")
    for sym in CURRENCIES.keys():
        _, _, info = next(r for r in results if r[1] == sym)
        if "error" not in info:
            print(f"  {format_fx_detail(sym, info)}")


if __name__ == "__main__":
    main()