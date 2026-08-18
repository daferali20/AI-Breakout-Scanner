"""Main breakout scanner with pre-breakout, confirmation and ML scoring."""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import yfinance as yf

from backend.analysis.indicators import TechnicalIndicators
from backend.analysis.squeeze_detector import SqueezeDetector
from backend.ml.breakout_model import BreakoutProbabilityModel, FEATURES

try:
    from backend.ml.model_registry import ModelRegistry
except (ImportError, ModuleNotFoundError, KeyError):
    ModelRegistry = None


class BreakoutScanner:
    """Detect compression, breakout-ready setups and confirmed breakouts."""

    def __init__(self, model_path: str = "models/breakout_model.joblib") -> None:
        self.squeeze = SqueezeDetector()
        self.indicators = TechnicalIndicators()
        self.model = None
        if ModelRegistry is not None:
            try:
                self.model = ModelRegistry(model_path).load()
            except Exception:
                self.model = None
        self.model = self.model or BreakoutProbabilityModel()

    def scan_stock(self, symbol: str, df: Optional[pd.DataFrame] = None) -> Dict:
        if df is None:
            try:
                df = yf.Ticker(symbol).history(period="1y", auto_adjust=False)
            except Exception as exc:
                return {"error": f"لا يمكن جلب بيانات السهم {symbol}: {exc}"}
        if df is None or df.empty or len(df) < 50:
            return {"error": f"بيانات غير كافية للسهم {symbol}"}
        try:
            df = df.copy().dropna(subset=["High", "Low", "Close", "Volume"])
            squeeze_result = self.squeeze.detect(df)
            if "error" in squeeze_result:
                return squeeze_result
            indicators = self.indicators.calculate_all(df)
            features = {**squeeze_result, **indicators, "current_price": float(df["Close"].iloc[-1])}
            score = self._calculate_score(features)
            phase = self._classify_phase(features)
            levels = self._calculate_levels(df)
            risk = self._false_breakout_risk(features)
            try:
                ml_result = self.model.predict(self._model_features(features))
            except Exception:
                ml_result = {
                    "breakout_probability": 0.0,
                    "model_type": "fallback",
                    "trained": False,
                    "metrics": {},
                }
            probability = float(ml_result.get("breakout_probability", 0.0))
            confirmation = self._confirmation_score(features)
            signal = self._signal_label(phase, score, confirmation, risk)
            explanation = self._explain(features, phase, confirmation, risk)
            return {
                "symbol": symbol.upper(), "score": score, "phase": phase, "signal": signal,
                "confirmation_score": confirmation, "breakout_probability": probability,
                "model_type": ml_result.get("model_type", "fallback"),
                "model_trained": ml_result.get("trained", False), "model_metrics": ml_result.get("metrics", {}),
                "false_breakout_risk": round(risk, 2),
                "breakout_confirmed": bool(features.get("breakout_confirmed", False)),
                "squeeze": squeeze_result, "indicators": indicators, "levels": levels,
                "explanation": explanation, "recommendation": self._get_recommendation(score, phase, risk),
            }
        except Exception as exc:
            return {"error": str(exc)}

    def _model_features(self, x: Dict) -> Dict:
        return {name: x.get(name, 0.0) for name in FEATURES}

    def _calculate_score(self, x: Dict) -> float:
        squeeze = float(x.get("squeeze_score", 50)); volume = float(x.get("volume_score", 40))
        rsi = float(x.get("rsi_score", 50)); trend = float(x.get("trend_strength", 0.5)) * 100
        breakout = float(x.get("breakout_score", 50)); position = float(x.get("price_position", 0.5)) * 100
        risk = self._false_breakout_risk(x)
        score = squeeze * .18 + volume * .18 + rsi * .10 + trend * .14 + breakout * .25 + position * .10 + (100-risk) * .05
        return round(float(np.clip(score, 0, 100)), 2)

    @staticmethod
    def _confirmation_score(x: Dict) -> float:
        rvol = float(x.get("relative_volume", x.get("volume_ratio", 1.0))); momentum = float(x.get("momentum_5d", 0.0))
        distance = float(x.get("resistance_distance", 1.0)); confirmed = bool(x.get("breakout_confirmed", False)); trend = float(x.get("trend_strength", .5))
        volume_score = np.clip((rvol-.8)/1.7*100, 0, 100); momentum_score = np.clip(50+momentum*10, 0, 100)
        proximity_score = np.clip((1-distance/.08)*100, 0, 100); trend_score = np.clip(trend*100, 0, 100)
        return round(float(np.clip(volume_score*.35 + momentum_score*.20 + proximity_score*.20 + trend_score*.15 + (20 if confirmed else 0), 0, 100)), 2)

    @staticmethod
    def _signal_label(phase: str, score: float, confirmation: float, risk: float) -> str:
        if phase == "BREAKOUT_CONFIRMED" and confirmation >= 70 and risk < 50: return "🔥 BREAKOUT_CONFIRMED"
        if phase == "BREAKOUT_READY" and confirmation >= 65 and score >= 65 and risk < 55: return "🎯 BREAKOUT_READY"
        if phase == "BUILDING" and confirmation >= 55: return "🏗️ BUILDING"
        return "👀 WATCH"

    @staticmethod
    def _explain(x: Dict, phase: str, confirmation: float, risk: float) -> str:
        reasons=[]; rvol=float(x.get("relative_volume",x.get("volume_ratio",1.0))); momentum=float(x.get("momentum_5d",0)); distance=float(x.get("resistance_distance",1)); trend=float(x.get("trend_strength",.5))
        if rvol>=2: reasons.append(f"حجم تداول مرتفع ({rvol:.1f}x)")
        elif rvol>=1.5: reasons.append(f"حجم داعم ({rvol:.1f}x)")
        if distance<=.02: reasons.append("قريب جدًا من المقاومة")
        if momentum>2: reasons.append("زخم صاعد")
        if trend>=.7: reasons.append("اتجاه صاعد قوي")
        if phase=="BREAKOUT_CONFIRMED": reasons.append("تم تأكيد الاختراق")
        if risk>=65: reasons.append("مخاطرة اختراق كاذب مرتفعة")
        if not reasons: reasons.append("لا توجد إشارة اختراق قوية حاليًا")
        return " + ".join(reasons)+f" | تأكيد {confirmation:.0f}/100"

    @staticmethod
    def _classify_phase(x: Dict) -> str:
        if bool(x.get("breakout_confirmed",False)): return "BREAKOUT_CONFIRMED"
        distance=float(x.get("resistance_distance",1)); rvol=float(x.get("relative_volume",x.get("volume_ratio",1))); squeeze=bool(x.get("is_squeeze",x.get("squeeze_on",False))); momentum=float(x.get("momentum_5d",0))
        if distance<=.02 and rvol>=1.5 and momentum>0: return "BREAKOUT_READY"
        if squeeze and distance<=.06: return "BUILDING"
        return "WATCH"

    @staticmethod
    def _false_breakout_risk(x: Dict) -> float:
        rvol=float(x.get("relative_volume",1)); trend=float(x.get("trend_strength",.5)); rsi=float(x.get("rsi",50)); momentum=float(x.get("momentum_5d",0)); risk=45.
        if rvol<1.2: risk+=20
        elif rvol>=2: risk-=12
        if trend<.35: risk+=18
        elif trend>.70: risk-=10
        if rsi>78: risk+=12
        if momentum<0: risk+=15
        return float(np.clip(risk,0,100))

    @staticmethod
    def _calculate_levels(df: pd.DataFrame) -> Dict:
        close=pd.to_numeric(df["Close"],errors="coerce"); high=pd.to_numeric(df["High"],errors="coerce"); low=pd.to_numeric(df["Low"],errors="coerce"); current=float(close.iloc[-1]); prev=close.shift(1)
        tr=pd.concat([high-low,(high-prev).abs(),(low-prev).abs()],axis=1).max(axis=1); atr=float(tr.ewm(alpha=1/14,adjust=False).mean().iloc[-1]); atr=atr if np.isfinite(atr) and atr>0 else current*.02
        resistance=float(high.iloc[-21:-1].max()); support=float(low.iloc[-21:-1].min()); entry=resistance+.1*atr; stop=min(current-1.5*atr,resistance-atr)
        return {"current":round(current,2),"resistance":round(resistance,2),"support":round(support,2),"entry":round(entry,2),"stop_loss":round(max(0,stop),2),"target_1":round(current+2*atr,2),"target_2":round(current+3.5*atr,2),"atr":round(atr,2)}

    @staticmethod
    def _get_recommendation(score: float, phase: str, risk: float) -> Dict:
        if phase=="BREAKOUT_CONFIRMED" and score>=75 and risk<45: return {"action":"🟢 اختراق مؤكد","risk":"متوسط"}
        if phase=="BREAKOUT_READY" and score>=70 and risk<55: return {"action":"🎯 جاهز للاختراق","risk":"متوسط"}
        if score>=65: return {"action":"🟡 مراقبة قوية","risk":"متوسط"}
        if score>=50: return {"action":"🔍 مراقبة","risk":"مرتفع"}
        return {"action":"🔴 تجنب","risk":"مرتفع"}

    def scan_symbols(self, symbols: List[str], min_score: float=0) -> pd.DataFrame:
        results=[]
        for symbol in symbols:
            result=self.scan_stock(symbol)
            if "error" not in result and result.get("score",0)>=min_score:
                results.append({"symbol":symbol.upper(),"score":result["score"],"phase":result["phase"],"signal":result["signal"],"confirmation_score":result["confirmation_score"],"breakout_probability":result["breakout_probability"],"false_breakout_risk":result["false_breakout_risk"],"model_type":result["model_type"],"squeeze":result["squeeze"].get("squeeze_score",0),"rvol":result["indicators"].get("relative_volume",1),"recommendation":result["recommendation"]["action"],"risk":result["recommendation"]["risk"],"price":result["levels"]["current"],"target":result["levels"]["target_1"],"explanation":result["explanation"]})
        return pd.DataFrame(results).sort_values("score",ascending=False) if results else pd.DataFrame()

    def scan_market(self, symbols: List[str], min_score: float=60) -> pd.DataFrame:
        return self.scan_symbols(symbols,min_score=min_score)
