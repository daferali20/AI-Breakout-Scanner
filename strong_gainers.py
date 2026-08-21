"""Strong Gainers analyzer at project root to avoid Streamlit package import-cache errors."""
from __future__ import annotations
from typing import Any
import time, random
import pandas as pd
import streamlit as st
import yfinance as yf
from gainers_universe import get_universe, discover_market_gainers

MIN_PRICE=0.40; MAX_PRICE=50.00; BATCH_SIZE=80; BATCH_DELAY_SECONDS=2.5; RETRY_DELAYS=(8.0,20.0,45.0)

def _num(value:Any,default:float=0.0)->float:
    try:return float(value)
    except (TypeError,ValueError):return default

def _score_momentum(change,rsi,price_vs_high):
    score=min(100.0,max(0.0,change*1.5)); score += 15 if 55<=rsi<=80 else (-8 if rsi>90 else 0); score += 10 if price_vs_high>=0 else 0; return round(min(100.0,max(0.0,score)),1)

def _score_liquidity(volume,avg_volume,dollar_volume):
    rvol=volume/avg_volume if avg_volume>0 else 0.0; score=min(100.0,rvol*25); score += 25 if dollar_volume>=50_000_000 else (15 if dollar_volume>=10_000_000 else (8 if dollar_volume>=2_000_000 else 0)); return round(min(100.0,score),1),round(rvol,2)

def _gain_strength(change:float)->str:
    if change>=200:return "🌋 ارتفاع استثنائي +200%"
    if change>=100:return "🔥 ارتفاع هائل +100%"
    if change>=75:return "🚀 ارتفاع قوي جدًا +75%"
    if change>=50:return "⚡ ارتفاع قوي +50%"
    return "📈 ارتفاع واضح +40%"

def _extract(data,symbol):
    if isinstance(data.columns,pd.MultiIndex):
        try:return data[symbol].dropna(how="all")
        except Exception:return pd.DataFrame()
    return data.dropna(how="all")

def _download_batch(symbols,period):
    for attempt,delay in enumerate((0.0,*RETRY_DELAYS)):
        if delay:time.sleep(delay+random.uniform(0,1.5))
        try:return yf.download(symbols,period=period,interval="1d",group_by="ticker",auto_adjust=False,threads=False,progress=False)
        except Exception as exc:
            limited="RateLimit" in type(exc).__name__ or "Too Many Requests" in str(exc)
            if not limited or attempt==len(RETRY_DELAYS):return pd.DataFrame()
    return pd.DataFrame()

def analyze_gainers(symbols,threshold=40.0,period="3mo",min_price=MIN_PRICE,max_price=MAX_PRICE,market_snapshot=None):
    rows=[]; stats={"requested":0,"with_data":0,"price_range":0,"above_threshold":0,"prefiltered":len(market_snapshot) if isinstance(market_snapshot,pd.DataFrame) else 0}
    clean=list(dict.fromkeys(str(s).strip().upper() for s in symbols if str(s).strip())); stats["requested"]=len(clean)
    if not clean:return pd.DataFrame(),stats
    market_map=market_snapshot.set_index("symbol").to_dict("index") if isinstance(market_snapshot,pd.DataFrame) and not market_snapshot.empty else {}
    for start in range(0,len(clean),BATCH_SIZE):
        batch=clean[start:start+BATCH_SIZE]; data=_download_batch(batch,period)
        if data.empty:continue
        for symbol in batch:
            try:
                frame=_extract(data,symbol)
                if frame.empty or "Close" not in frame or len(frame)<2:continue
                close=pd.to_numeric(frame["Close"],errors="coerce").dropna(); volume=pd.to_numeric(frame.get("Volume",0),errors="coerce").fillna(0)
                if len(close)<2:continue
                stats["with_data"]+=1; price=_num(close.iloc[-1]); mr=market_map.get(symbol,{})
                if mr and _num(mr.get("market_price"),0)>0:price=_num(mr.get("market_price"))
                if not(min_price<=price<=max_price):continue
                stats["price_range"]+=1; live_change=_num(mr.get("market_change_pct"),0) if mr else 0; candidates=[("اليوم",live_change,1)] if live_change else []
                for label,days in (("اليوم",1),("3 أيام",3),("5 أيام",5),("20 يوم",20),("60 يوم",60)):
                    if len(close)>days:
                        base=_num(close.iloc[-days-1])
                        if base>0:candidates.append((label,((price/base)-1)*100,days))
                if not candidates:continue
                period_label,change,change_days=("اليوم",live_change,1) if live_change>=threshold else max(candidates,key=lambda x:x[1])
                if change<threshold:continue
                stats["above_threshold"]+=1; vol=_num(volume.iloc[-1]); avg_vol=_num(volume.iloc[:-1].tail(20).mean())
                if mr and _num(mr.get("market_volume"),0)>0:vol=_num(mr.get("market_volume"))
                dollar_volume=price*vol; high=_num(close.tail(252).max(),price); price_vs_high=((price/high)-1)*100 if high>0 else 0; returns=close.pct_change().dropna(); rsi=50.0
                if len(returns)>=14:
                    gains=returns.clip(lower=0).rolling(14).mean().iloc[-1]; losses=(-returns.clip(upper=0)).rolling(14).mean().iloc[-1]; rsi=100-(100/(1+gains/losses)) if losses>0 else 100.0
                momentum=_score_momentum(change,rsi,price_vs_high); liquidity,rvol=_score_liquidity(vol,avg_vol,dollar_volume); composite=round(momentum*.55+liquidity*.45,1)
                rows.append({"symbol":symbol,"price":round(price,2),"change_pct":round(change,2),"period":period_label,"period_days":change_days,"momentum_score":momentum,"liquidity_score":liquidity,"volume":int(vol),"relative_volume":rvol,"dollar_volume":round(dollar_volume,0),"rsi":round(rsi,1),"strength":_gain_strength(change),"gainer_score":composite,"exchange":mr.get("exchange","") if mr else "","source":"AI Market Engine"})
            except Exception:continue
        if start+BATCH_SIZE<len(clean):time.sleep(BATCH_DELAY_SECONDS+random.uniform(0,1))
    result=pd.DataFrame(rows)
    if result.empty:return result,stats
    return result.sort_values(["change_pct","gainer_score","liquidity_score"],ascending=False).reset_index(drop=True),stats

@st.cache_data(ttl=180,show_spinner=False)
def discover_strong_gainers(limit=250,threshold=40.0,period="3mo",min_price=MIN_PRICE,max_price=MAX_PRICE):
    candidates=discover_market_gainers(min_price=min_price,max_price=max_price,threshold=threshold)
    if not candidates.empty:
        symbols=candidates["symbol"].tolist()[:limit] if limit>0 else candidates["symbol"].tolist(); candidates=candidates[candidates["symbol"].isin(symbols)].copy(); return analyze_gainers(symbols,threshold,period,min_price,max_price,candidates)
    symbols=list(get_universe()); symbols=symbols[:limit] if limit>0 else symbols; result,stats=analyze_gainers(symbols,threshold,period,min_price,max_price); stats["prefiltered"]=0; return result,stats
