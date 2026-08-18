"""Yahoo Finance market discovery with batching, caching and rate-limit safety."""

from __future__ import annotations

import time
from typing import Iterable, List

import pandas as pd
import yfinance as yf


# A compact liquid universe used when an external index-membership feed is unavailable.
# It is deliberately deduplicated and biased toward liquid US-listed names.
DEFAULT_UNIVERSE = sorted(set("""
AAPL MSFT NVDA AMZN META GOOGL GOOGL GOOG AVGO TSLA BRK-B JPM WMT LLY V MA HD
COST NFLX CRM ORCL AMD INTC QCOM MU AMAT LRCX KLAC PANW CRWD PLTR NOW SNOW DDOG
UBER ABNB SHOP COIN HOOD SQ PYPL SOFI BAC C C GS MS BLK XOM CVX COP SLB CAT DE
GE GEHC RTX LMT NOC UNH JNJ MRK ABBV PFE TMO ABT DHR ISRG NKE SBUX MCD CMG
KO PEP PM WBD DIS TGT LOW TJX MAR BKNG DAL UAL F DXCM ENPH FSLR RIVN LCID
SMCI ARM MU AI IONQ RGTI RKLB ASTS SOUN TEM HIMS OKLO CELH CAVA DKNG ROKU
ETSY PINS TOST AFRM PATH MDB NET ZS FTNT TTD APP DUOL CVNA MARA RIOT CLSK
BITF MSTR GLD SLV TLT IWM DIA SPY QQQ
""".split()))


def normalize_symbols(symbols: Iterable[str]) -> List[str]:
    """Normalize Yahoo symbols and remove duplicates/invalid entries."""
    out: List[str] = []
    seen = set()
    for symbol in symbols:
        value = str(symbol).strip().upper().replace(".", "-")
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


def _extract_frame(downloaded: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Extract one ticker from both single-level and MultiIndex Yahoo output."""
    if downloaded is None or downloaded.empty:
        return pd.DataFrame()
    if isinstance(downloaded.columns, pd.MultiIndex):
        # yfinance may use either (Price, Ticker) or (Ticker, Price).
        if symbol in downloaded.columns.get_level_values(-1):
            frame = downloaded.xs(symbol, axis=1, level=-1, drop_level=True).copy()
        elif symbol in downloaded.columns.get_level_values(0):
            frame = downloaded.xs(symbol, axis=1, level=0, drop_level=True).copy()
        else:
            return pd.DataFrame()
    else:
        frame = downloaded.copy()
    rename = {str(c).lower(): c for c in frame.columns}
    required = {"open", "high", "low", "close", "volume"}
    if not required.issubset(rename):
        return pd.DataFrame()
    return frame.rename(columns={rename[k]: k.title() for k in required})


def download_batches(
    symbols: Iterable[str],
    period: str = "6mo",
    interval: str = "1d",
    batch_size: int = 40,
    pause_seconds: float = 1.0,
    max_retries: int = 2,
) -> dict[str, pd.DataFrame]:
    """Download market data in small batches to reduce Yahoo request pressure.

    Failures are isolated per batch. The function never raises because one Yahoo
    response failed; callers can continue with the symbols that were returned.
    """
    symbols = normalize_symbols(symbols)
    result: dict[str, pd.DataFrame] = {}
    for start in range(0, len(symbols), max(1, batch_size)):
        batch = symbols[start : start + batch_size]
        data = None
        for attempt in range(max_retries + 1):
            try:
                data = yf.download(
                    tickers=batch,
                    period=period,
                    interval=interval,
                    group_by="column",
                    auto_adjust=False,
                    progress=False,
                    threads=False,
                )
                break
            except Exception:
                if attempt >= max_retries:
                    break
                time.sleep(pause_seconds * (attempt + 1))
        if data is not None and not data.empty:
            for symbol in batch:
                frame = _extract_frame(data, symbol)
                if len(frame) >= 50:
                    result[symbol] = frame.dropna(subset=["High", "Low", "Close", "Volume"])
        if start + batch_size < len(symbols):
            time.sleep(pause_seconds)
    return result


def rank_discovery_candidates(frames: dict[str, pd.DataFrame], limit: int = 30) -> pd.DataFrame:
    """Cheap first-pass ranking before expensive deep breakout analysis."""
    rows = []
    for symbol, df in frames.items():
        if df.empty or len(df) < 21:
            continue
        close = df["Close"].astype(float)
        volume = df["Volume"].astype(float)
        price = float(close.iloc[-1])
        prev = float(close.iloc[-2])
        avg_volume = float(volume.iloc[-21:-1].mean())
        if price <= 0 or avg_volume <= 0:
            continue
        day_change = (price / prev - 1) * 100 if prev else 0
        five_day = (price / float(close.iloc[-6]) - 1) * 100 if len(close) >= 6 else 0
        rvol = float(volume.iloc[-1] / avg_volume)
        high20 = float(close.iloc[-21:-1].max())
        proximity = (price / high20) if high20 else 0
        score = min(100, max(0, 35 + day_change * 3 + five_day * 1.5 + min(rvol, 4) * 8 + proximity * 20))
        rows.append({
            "symbol": symbol,
            "price": round(price, 2),
            "day_change_pct": round(day_change, 2),
            "five_day_pct": round(five_day, 2),
            "relative_volume": round(rvol, 2),
            "resistance_proximity": round(proximity, 4),
            "discovery_score": round(score, 2),
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("discovery_score", ascending=False).head(limit).reset_index(drop=True)
