from backend.opportunity import PhaseDetector


def test_phase_detector_is_importable_and_classifies():
    result = PhaseDetector().get_phase_metrics(
        {
            "relative_volume": 2.0,
            "price_change": 0.03,
            "smart_money_score": 70,
            "compression_level": 0.2,
            "resistance_break": 1.02,
            "trend_strength": 0.7,
        },
        "TEST",
    )
    assert result.phase == "breakout"
    assert result.days_in_phase >= 0
