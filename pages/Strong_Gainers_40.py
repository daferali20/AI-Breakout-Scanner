"""🚀 +40% gainers: pure gain leaderboard + elite quality shortlist."""
from __future__ import annotations
import os,sys
PROJECT_ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:sys.path.insert(0,PROJECT_ROOT)
import pandas as pd
import streamlit as st
from access_control import require_access
from backend.gainers_universe import get_universe,universe_status
from backend.strong_gainers import MIN_PRICE,MAX_PRICE,analyze_gainers,discover_strong_gainers
st.set_page_config(page_title="الأسهم الأكثر ارتفاعًا",page_icon="🚀",layout="wide"); require_access("free")
def _cats(r):
    out=[]; rv=float(r.get("relative_volume",0) or 0); m=float(r.get("momentum_score",0) or 0); l=float(r.get("liquidity_score",0) or 0); ch=float(r.get("change_pct",0) or 0); dv=float(r.get("dollar_volume",0) or 0)
    if rv>=3:out.append("🔥 حجم استثنائي")
    elif rv>=2:out.append("💧 RVOL مرتفع")
    if l>=80:out.append("💎 سيولة قوية جدًا")
    elif l>=65:out.append("💧 سيولة قوية")
    if m>=80:out.append("🚀 زخم قوي جدًا")
    elif m>=70:out.append("📈 زخم قوي")
    if dv>=20_000_000:out.append("💵 تداول نقدي كبير")
    if ch>=100:out.append("⚡ تسارع سعري استثنائي")
    elif ch>=60:out.append("⚡ تسارع سعري قوي")
    return out
def _elite(df):
    if df.empty:return df.copy()
    w=df.copy()
    for c in ("change_pct","momentum_score","liquidity_score","relative_volume","dollar_volume"):w[c]=pd.to_numeric(w[c],errors="coerce").fillna(0)
    w["catalysts"]=w.apply(_cats,axis=1); w["catalyst_count"]=w["catalysts"].map(len); w["elite_score"]=(w["momentum_score"]*.30+w["liquidity_score"]*.35+w["change_pct"].clip(upper=150)/150*20+w["relative_volume"].clip(upper=5)/5*10+w["catalyst_count"].clip(upper=5)/5*5).round(1)
    return w[(w.momentum_score>=65)&(w.liquidity_score>=60)&((w.relative_volume>=1.5)|(w.dollar_volume>=5_000_000))&(w.catalyst_count>=2)].sort_values(["elite_score","liquidity_score","momentum_score"],ascending=False).reset_index(drop=True)
st.title("🚀 الأسهم الأكثر ارتفاعًا في السوق")
st.caption("القائمة الأولى = نسبة الارتفاع فقط. القائمة الثانية = أفضل المتصدرين من حيث السيولة والزخم والمحـفز.")
status=universe_status(); a,b,c=st.columns(3); a.metric("🇺🇸 الكون المستقل",f"{status['count']:,} رمز"); b.metric("🎯 الحد الأدنى","+40%"); c.metric("💵 السعر","$0.40 – $50")
c1,c2,c3,c4=st.columns(4); auto=c1.toggle("🤖 اكتشاف تلقائي",value=True); manual=c2.text_input("🔎 رموز إضافية",placeholder="RFAI, USDE, SDOT"); limit=c3.selectbox("حد المرشحين",[50,100,150,300,600],index=2); price_range=c4.selectbox("نطاق السعر",["$0.40 – $50","$0.40 – $10","$1 – $50","مخصص"])
if price_range=="$0.40 – $10":min_price,max_price=.40,10.
elif price_range=="$1 – $50":min_price,max_price=1.,50.
elif price_range=="مخصص":
    p1,p2=st.columns(2); min_price=p1.number_input("أقل سعر",.01,value=.40,step=.10); max_price=p2.number_input("أعلى سعر",.02,value=50.,step=1.)
else:min_price,max_price=MIN_PRICE,MAX_PRICE
def _scan():
    if auto:return discover_strong_gainers(limit=limit,threshold=40.,min_price=min_price,max_price=max_price)
    syms=[x.strip().upper() for x in manual.replace("\n",",").split(",") if x.strip()]; return analyze_gainers(syms or list(get_universe(limit)),threshold=40.,min_price=min_price,max_price=max_price)
if st.button("🔄 تحديث أعلى الأسهم ارتفاعًا",type="primary",width="stretch"):
    with st.spinner("جاري البحث عن أعلى الأسهم ارتفاعًا..."):df,stats=_scan(); st.session_state["strong_gainers_40"]=df; st.session_state["strong_gainers_40_stats"]=stats
if "strong_gainers_40" not in st.session_state and auto:
    with st.spinner("جاري اكتشاف المتصدرين..."):df,stats=_scan(); st.session_state["strong_gainers_40"]=df; st.session_state["strong_gainers_40_stats"]=stats
df=st.session_state.get("strong_gainers_40"); stats=st.session_state.get("strong_gainers_40_stats",{})
if df is None:st.info("اضغط تحديث لبدء الفحص.");st.stop()
if df.empty:st.warning("لا توجد نتائج +40% في البيانات المتاحة حاليًا.");st.stop()
market=df.copy(); market["change_pct"]=pd.to_numeric(market["change_pct"],errors="coerce").fillna(0); market=market[market.change_pct>=40].sort_values("change_pct",ascending=False).reset_index(drop=True); elite=_elite(market); st.session_state["strong_gainers_40_elite"]=elite
m1,m2,m3,m4=st.columns(4); m1.metric("🚀 متصدرون +40%",len(market)); m2.metric("🥇 الأعلى",f"+{market.change_pct.max():.1f}%"); m3.metric("🏆 النخبة",len(elite)); m4.metric("💵 أعلى Dollar Volume",f"${market.dollar_volume.max()/1_000_000:.1f}M")
t1,t2=st.tabs(["🚀 الأعلى ارتفاعًا","🏆 الأفضل للتداول"])
with t1:
    st.info("هذه القائمة مرتبة حصريًا حسب نسبة الارتفاع. السيولة والزخم لا يغيران ترتيبها.")
    for i,(_,r) in enumerate(market.head(60).iterrows(),1):
        with st.container(border=True):
            rank,sym,gain,price,vol=st.columns([.55,1.2,1.25,1,1.2]); rank.markdown(f"## #{i}"); sym.markdown(f"## {r.symbol}"); gain.metric("📈 الارتفاع",f"+{r.change_pct:.2f}%"); price.metric("السعر",f"${r.price:.2f}"); vol.metric("الحجم",f"{int(r.volume):,}")
            st.caption(f"{r.strength} · Dollar Volume: ${r.dollar_volume:,.0f} · المصدر: {r.get('source','Market discovery')}")
with t2:
    st.caption("هنا فقط نستخدم السيولة والزخم وRVOL والمحـفز لاستخراج أفضل الأسهم من قائمة المتصدرين.")
    if elite.empty:st.info("لا توجد أسهم تحقق شروط النخبة حاليًا.")
    else:
        for i,(_,r) in enumerate(elite.head(25).iterrows(),1):
            with st.container(border=True):
                rank,sym,score,gain,liq,mom=st.columns([.5,1,1,1,1,1]); rank.markdown(f"## #{i}"); sym.markdown(f"## {r.symbol}"); score.metric("🏆 Elite",f"{r.elite_score:.1f}"); gain.metric("📈 الارتفاع",f"+{r.change_pct:.1f}%"); liq.metric("💧 السيولة",f"{r.liquidity_score:.0f}"); mom.metric("🚀 الزخم",f"{r.momentum_score:.0f}")
                st.markdown(" · ".join(r.catalysts)); st.caption(f"RVOL {r.relative_volume:.2f}x · الحجم {int(r.volume):,} · Dollar Volume ${r.dollar_volume:,.0f}")
with st.expander("🔎 تشخيص المسح"):
    x1,x2,x3,x4=st.columns(4); x1.metric("مرشحو السوق",stats.get("prefiltered",0)); x2.metric("تم تحليلها",stats.get("requested",0)); x3.metric("بيانات صالحة",stats.get("with_data",0)); x4.metric("+40%",stats.get("above_threshold",0))
