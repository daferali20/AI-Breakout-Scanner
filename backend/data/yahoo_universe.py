"""Yahoo Finance discovery with batching, retries, validation and cache safety."""

from __future__ import annotations

import time
from typing import Iterable, List

import pandas as pd
import yfinance as yf

DEFAULT_UNIVERSE = sorted(set("""
AAPL MSFT NVDA AMZN META GOOGL GOOG AVGO TSLA BRK-B JPM WMT LLY V MA HD COST NFLX CRM ORCL AMD INTC QCOM MU AMAT LRCX KLAC PANW CRWD PLTR NOW SNOW DDOG UBER ABNB SHOP COIN HOOD SQ PYPL SOFI BAC C GS MS BLK XOM CVX COP SLB CAT DE GE GEHC RTX LMT NOC UNH JNJ MRK ABBV PFE TMO ABT DHR ISRG NKE SBUX MCD CMG KO PEP PM DIS TGT LOW TJX MAR BKNG DAL UAL F DXCM ENPH FSLR RIVN LCID SMCI ARM AI IONQ RGTI RKLB ASTS SOUN TEM HIMS OKLO CELH CAVA DKNG ROKU ETSY PINS TOST AFRM PATH MDB NET ZS FTNT TTD APP DUOL CVNA MARA RIOT CLSK MSTR GLD SLV TLT IWM DIA SPY QQQ
""".split()))

# Known stale/changed symbols are skipped without noisy user-facing errors.
KNOWN_INVALID = {"BITF", "SQ"}


def normalize_symbols(symbols: Iterable[str]) -> List[str]:
    out, seen = [], set()
    for symbol in symbols:
        value = str(symbol).strip().upper().replace(".", "-")
        if not value or value in seen or value in KNOWN_INVALID:
            continue
        seen.add(value)
        out.append(value)
    return out


def _extract_frame(downloaded: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if downloaded is None or downloaded.empty:
        return pd.DataFrame()
    try:
        if isinstance(downloaded.columns, pd.MultiIndex):
            levels = [list(downloaded.columns.get_level_values(i)) for i in range(downloaded.columns.nlevels)]
            if symbol in levels[-1]:
                frame = downloaded.xs(symbol, axis=1, level=-1, drop_level=True).copy()
            elif symbol in levels[0]:
                frame = downloaded.xs(symbol, axis=1, level=0, drop_level=True).copy()
            else:
                return pd.DataFrame()
        else:
            frame = downloaded.copy()
        lookup = {str(c).strip().lower(): c for c in frame.columns}
        required = {"open", "high", "low", "close", "volume"}
        if not required.issubset(lookup):
            return pd.DataFrame()
        return frame.rename(columns={lookup[k]: k.title() for k in required})
    except Exception:
        return pd.DataFrame()


def _download_batch(batch: List[str], period: str, interval: str, max_retries: int, pause_seconds: float) -> pd.DataFrame:
    """Download one batch; retry transient Yahoo/yfinance failures."""
    for attempt in range(max_retries + 1):
        try:
            return yf.download(
                tickers=batch,
                period=period,
                interval=interval,
                group_by="column",
                auto_adjust=False,
                progress=False,
                threads=False,
            )
        except Exception as exc:
            message = str(exc).lower()
            transient = any(x in message for x in ("locked", "timeout", "429", "rate", "temporarily", "operationalerror"))
            if not transient or attempt >= max_retries:
                return pd.DataFrame()
            time.sleep(pause_seconds * (attempt + 1))
    return pd.DataFrame()


def download_batches(symbols: Iterable[str], period: str = "6mo", interval: str = "1d", batch_size: int = 25, pause_seconds: float = 1.5, max_retries: int = 3) -> dict[str, pd.DataFrame]:
    """Safely download Yahoo data in small sequential batches."""
    symbols = normalize_symbols(symbols)
    result: dict[str, pd.DataFrame] = {}
    for start in range(0, len(symbols), max(1, batch_size)):
        batch = symbols[start:start + batch_size]
        data = _download_batch(batch, period, interval, max_retries, pause_seconds)
        if data is not None and not data.empty:
            for symbol in batch:
                frame = _extract_frame(data, symbol)
                if len(frame) >= 50:
                    clean = frame.dropna(subset=["High", "Low", "Close", "Volume"])
                    if len(clean) >= 50:
                        result[symbol] = clean
        if start + batch_size < len(symbols):
            time.sleep(pause_seconds)
    return result


def rank_discovery_candidates(frames: dict[str, pd.DataFrame], limit: int = 30) -> pd.DataFrame:
    rows = []
    for symbol, df in frames.items():
        try:
            if df.empty or len(df) < 21:
                continue
            close, volume = df["Close"].astype(float), df["Volume"].astype(float)
            price, prev = float(close.iloc[-1]), float(close.iloc[-2])
            avg_volume = float(volume.iloc[-21:-1].mean())
            if price <= 0 or avg_volume <= 0:
                continue
            day_change = (price / prev - 1) * 100 if prev else 0
            five_day = (price / float(close.iloc[-6]) - 1) * 100
            rvol = float(volume.iloc[-1] / avg_volume)
            high20 = float(close.iloc[-21:-1].max())
            proximity = price / high20 if high20 else 0
            score = min(100, max(0, 35 + day_change * 3 + five_day * 1.5 + min(rvol, 4) * 8 + proximity * 20))
            rows.append({"symbol": symbol, "price": round(price, 2), "day_change_pct": round(day_change, 2), "five_day_pct": round(five_day, 2), "relative_volume": round(rvol, 2), "resistance_proximity": round(proximity, 4), "discovery_score": round(score, 2)})
        except Exception:
            continue
    return pd.DataFrame(rows).sort_values("discovery_score", ascending=False).head(limit).reset_index(drop=True) if rows else pd.DataFrame()
