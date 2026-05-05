from __future__ import annotations

import threading as _th
import time as _tm

import numpy as np
import pandas as pd
import requests
import streamlit as st


class _TokenBucket:
    def __init__(self, capacity: int = 30, refill_every: float = 60.0):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_every = refill_every
        self.updated_at = _tm.time()
        self.lock = _th.Lock()

    def acquire(self) -> None:
        with self.lock:
            now = _tm.time()
            elapsed = now - self.updated_at
            refill = int(elapsed / self.refill_every * self.capacity)
            if refill > 0:
                self.tokens = min(self.capacity, self.tokens + refill)
                self.updated_at = now
            if self.tokens <= 0:
                _tm.sleep(1.0)
                self.acquire()
                return
            self.tokens -= 1


@st.cache_resource
def get_bucket() -> _TokenBucket:
    return _TokenBucket()


def throttled_get(url: str, timeout: int = 10):
    get_bucket().acquire()
    return requests.get(url, timeout=timeout)


@st.cache_data(ttl=300, max_entries=50)
def fetch_yahoo_series(symbol: str, period: str, interval: str):
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?range={period}&interval={interval}&includePrePost=false"
    )
    response = throttled_get(url, timeout=10)
    response.raise_for_status()
    return response.json()


@st.cache_data(ttl=60, max_entries=100)
def fetch_quote(symbol: str) -> dict:
    try:
        raw = fetch_yahoo_series(symbol, "1d", "1d")
        result = raw["chart"]["result"][0]
        meta = result.get("meta", {})
        price = meta.get("regularMarketPrice")
        previous = meta.get("previousClose") or meta.get("chartPreviousClose")
        pct = ((price - previous) / previous * 100) if price and previous else 0.0
        return {
            "symbol": symbol,
            "name": meta.get("shortName") or meta.get("longName") or symbol,
            "price": price,
            "pct": round(pct, 2),
            "currency": meta.get("currency", "USD"),
        }
    except Exception:
        return {}


def fetch_multi_quotes(symbols: list[str]) -> dict[str, dict]:
    return {symbol: quote for symbol in symbols if (quote := fetch_quote(symbol))}


@st.cache_data(ttl=120)
def fetch_stock_fundamentals(symbol: str) -> dict:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        "?range=1d&interval=1d&includePrePost=false"
    )
    try:
        response = throttled_get(url, timeout=10)
        response.raise_for_status()
        data = response.json()["chart"]["result"][0]
        meta = data.get("meta", {})
        quote = data["indicators"]["quote"][0]
        closes = [value for value in quote.get("close", []) if value]
        price = meta.get("regularMarketPrice") or (closes[-1] if closes else None)
        prev = meta.get("chartPreviousClose") or meta.get("previousClose")
        pct = ((price - prev) / prev * 100) if price and prev else 0.0
        return {
            "price": round(price, 4) if price else None,
            "prev_close": round(prev, 4) if prev else None,
            "pct": round(pct, 3),
            "52w_high": round(meta.get("fiftyTwoWeekHigh", 0) or 0, 2),
            "52w_low": round(meta.get("fiftyTwoWeekLow", 0) or 0, 2),
            "mkt_cap": meta.get("marketCap"),
            "currency": meta.get("currency", "USD"),
            "symbol": meta.get("symbol", symbol),
            "short_name": meta.get("shortName") or meta.get("longName") or symbol,
        }
    except Exception:
        return {}


@st.cache_data(ttl=300, max_entries=25)
def fetch_stock_history_1y(symbol: str) -> pd.DataFrame:
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        "?range=1y&interval=1d&includePrePost=false&events=div,splits"
    )
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        result = response.json()["chart"]["result"][0]
        timestamps = result["timestamp"]
        quote = result["indicators"]["quote"][0]
        frame = pd.DataFrame(
            {
                "open": quote.get("open", []),
                "high": quote.get("high", []),
                "low": quote.get("low", []),
                "close": quote.get("close", []),
                "volume": quote.get("volume", []),
            },
            index=pd.to_datetime(timestamps, unit="s", utc=True).tz_convert("America/New_York"),
        )
        return frame.dropna(subset=["close"])
    except Exception:
        return pd.DataFrame()


def compute_technicals(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 20:
        return {}
    closes = df["close"].astype(float).values
    def sma(arr, window):
        return float(np.mean(arr[-window:])) if len(arr) >= window else None
    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50)
    sma200 = sma(closes, 200)

    deltas = np.diff(closes[-15:])
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains) if gains.size else 0
    avg_loss = np.mean(losses) if losses.size else 1e-9
    rs = avg_gain / avg_loss if avg_loss else 0
    rsi14 = round(100 - 100 / (1 + rs), 1)

    if len(closes) >= 64:
        returns = np.diff(np.log(closes[-63:]))
        vol_annual = round(float(np.std(returns) * np.sqrt(252) * 100), 1)
    else:
        vol_annual = 0.0
    return {
        "sma20": round(sma20, 2) if sma20 else None,
        "sma50": round(sma50, 2) if sma50 else None,
        "sma200": round(sma200, 2) if sma200 else None,
        "rsi14": rsi14,
        "vol_annual": vol_annual,
    }


def portfolio_summary(portfolio: dict) -> dict:
    if not portfolio:
        return {"total_value": 0, "total_cost": 0, "total_pnl": 0, "total_pnl_pct": 0, "holdings": []}
    holdings = []
    total_value = 0.0
    total_cost = 0.0
    for symbol, position in portfolio.items():
        info = fetch_stock_fundamentals(symbol)
        price = info.get("price") or 0.0
        shares = position.get("shares", 0.0)
        avg_cost = position.get("avg_cost", price)
        market_value = price * shares
        cost_value = avg_cost * shares
        pnl = market_value - cost_value
        pnl_pct = (pnl / cost_value * 100) if cost_value else 0.0
        total_value += market_value
        total_cost += cost_value
        holdings.append(
            {
                "sym": symbol,
                "shares": shares,
                "avg_cost": avg_cost,
                "price": price,
                "pct": info.get("pct", 0.0),
                "mkt_val": market_value,
                "cost_val": cost_value,
                "pnl": pnl,
                "pnl_pct": pnl_pct,
                "short_name": info.get("short_name", symbol),
                "currency": info.get("currency", "USD"),
            }
        )
    holdings.sort(key=lambda row: row["mkt_val"], reverse=True)
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost else 0.0
    for holding in holdings:
        holding["weight"] = round(holding["mkt_val"] / total_value * 100, 1) if total_value else 0.0
    return {
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_pnl": round(total_pnl, 2),
        "total_pnl_pct": round(total_pnl_pct, 2),
        "holdings": holdings,
    }


@st.cache_data(ttl=1800, max_entries=50, show_spinner=False)
def _fetch_beta(symbol: str) -> float:
    try:
        spy = fetch_stock_history_1y("SPY")
        target = fetch_stock_history_1y(symbol)
        if spy.empty or target.empty or len(spy) < 60:
            return 1.0
        spy_returns = spy["close"].pct_change().dropna()
        target_returns = target["close"].pct_change().dropna()
        common = spy_returns.index.intersection(target_returns.index)
        if len(common) < 30:
            return 1.0
        covariance = float(np.cov(target_returns.loc[common].values, spy_returns.loc[common].values)[0, 1])
        variance = float(np.var(spy_returns.loc[common].values))
        return round(covariance / variance, 3) if variance else 1.0
    except Exception:
        return 1.0


def calculate_portfolio_beta(summary: dict) -> float:
    total_value = summary.get("total_value") or 1.0
    holdings = sorted(summary.get("holdings", []), key=lambda row: row["mkt_val"], reverse=True)[:8]
    top_value = sum(row["mkt_val"] for row in holdings) or total_value
    beta = 0.0
    for holding in holdings:
        beta += (holding["mkt_val"] / top_value) * _fetch_beta(holding["sym"])
    return round(beta, 3)


def calculate_var(summary: dict, confidence: float = 0.95) -> float:
    z_map = {0.90: 1.282, 0.95: 1.645, 0.99: 2.326}
    z_score = z_map.get(confidence, 1.645)
    total_value = summary.get("total_value") or 1.0
    holdings = sorted(summary.get("holdings", []), key=lambda row: row["mkt_val"], reverse=True)[:8]
    if not holdings:
        return 0.0
    top_value = sum(row["mkt_val"] for row in holdings) or total_value
    weighted_vol = 0.0
    for holding in holdings:
        technicals = compute_technicals(fetch_stock_history_1y(holding["sym"]))
        annual_vol = technicals.get("vol_annual", 30.0) / 100.0
        weighted_vol += (holding["mkt_val"] / top_value) * (annual_vol / np.sqrt(252))
    return round(total_value * z_score * weighted_vol, 2)


def calculate_sharpe_ratio(summary: dict, risk_free: float = 0.053) -> float:
    total_value = summary.get("total_value") or 1.0
    total_cost = summary.get("total_cost") or 1.0
    holdings = sorted(summary.get("holdings", []), key=lambda row: row["mkt_val"], reverse=True)[:8]
    if not holdings:
        return 0.0
    top_value = sum(row["mkt_val"] for row in holdings) or total_value
    weighted_vol = 0.0
    for holding in holdings:
        technicals = compute_technicals(fetch_stock_history_1y(holding["sym"]))
        weighted_vol += (holding["mkt_val"] / top_value) * (technicals.get("vol_annual", 30.0) / 100.0)
    if weighted_vol < 0.001:
        return 0.0
    annual_return = total_value / total_cost - 1.0
    return round((annual_return - risk_free) / weighted_vol, 3)


def calculate_diversification(summary: dict) -> int:
    holdings = summary.get("holdings", [])
    if not holdings:
        return 0
    total = summary.get("total_value") or 1.0
    count_score = min(30, len(holdings) * 4)
    sector_score = min(40, len({holding["sym"].split(".")[-1] for holding in holdings}) * 8)
    hhi = sum((holding["mkt_val"] / total) ** 2 for holding in holdings)
    concentration_score = int((1 - hhi) * 30)
    return min(100, count_score + sector_score + concentration_score)

