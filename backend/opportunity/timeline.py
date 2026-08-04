from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from .models import MarketPhase, TimelineEvent, PHASE_PROPERTIES

class TimelineBuilder:
    def build_timeline(self, current_phase: MarketPhase, 
                      next_phase: Optional[MarketPhase],
                      current_days: int,
                      expected_days: Optional[int],
                      data: Dict[str, Any]) -> List[TimelineEvent]:
        events = []
        current_event = TimelineEvent(
            phase=current_phase,
            date=datetime.now() - timedelta(days=current_days),
            confidence=self._get_phase_confidence(current_phase, data),
            metrics=data,
            days_until=0
        )
        events.append(current_event)
        previous_phases = self._get_previous_phases(current_phase)
        for i, phase in enumerate(reversed(previous_phases)):
            days_back = PHASE_PROPERTIES.get(phase, {}).get('avg_duration', 10)
            event = TimelineEvent(
                phase=phase,
                date=datetime.now() - timedelta(days=current_days + (i + 1) * days_back),
                confidence=0.6 + (i * 0.05),
                metrics={},
                days_until=-(i + 1) * days_back
            )
            events.insert(0, event)
        if next_phase and expected_days:
            next_event = TimelineEvent(
                phase=next_phase,
                date=datetime.now() + timedelta(days=expected_days),
                confidence=self._get_phase_confidence(next_phase, data) * 0.8,
                metrics={},
                days_until=expected_days
            )
            events.append(next_event)
        return events
    
    def _get_previous_phases(self, current_phase: MarketPhase) -> List[MarketPhase]:
        sequence = [
            MarketPhase.DECLINE, MarketPhase.ACCUMULATION, MarketPhase.COMPRESSION,
            MarketPhase.MOMENTUM, MarketPhase.BREAKOUT_READY, MarketPhase.BREAKOUT,
            MarketPhase.TREND_CONTINUATION, MarketPhase.DISTRIBUTION,
        ]
        try:
            idx = sequence.index(current_phase)
            return sequence[:idx]
        except ValueError:
            return [MarketPhase.ACCUMULATION]
    
    def _get_phase_confidence(self, phase: MarketPhase, data: Dict[str, Any]) -> float:
        base_confidence = {
            MarketPhase.ACCUMULATION: 0.85, MarketPhase.COMPRESSION: 0.90,
            MarketPhase.MOMENTUM: 0.80, MarketPhase.BREAKOUT_READY: 0.85,
            MarketPhase.BREAKOUT: 0.75, MarketPhase.TREND_CONTINUATION: 0.70,
            MarketPhase.DISTRIBUTION: 0.60, MarketPhase.DECLINE: 0.50,
        }.get(phase, 0.70)
        if data.get('volume_trend', 1) > 1.5:
            base_confidence += 0.05
        if data.get('trend_strength', 0.5) > 0.7:
            base_confidence += 0.05
        return min(0.95, base_confidence)
