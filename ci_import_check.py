"""Dependency-light smoke test for core application imports."""
import importlib

MODULES = (
    "gainers_universe",
    "strong_gainers",
    "live_market_leaders",
    "supabase_auth",
    "backend.analysis.breakout_features",
    "backend.ml.breakout_model",
    "backend.ml.dataset_builder",
    "backend.ml.multisymbol_dataset",
    "backend.ml.model_validation",
    "backend.ml.leave_symbol_out",
    "backend.ml.backtest_report",
    "backend.ranking.opportunity_ranker",
    "backend.ranking.explanations",
    "backend.market.regime",
)

for module_name in MODULES:
    importlib.import_module(module_name)
    print(f"IMPORT OK: {module_name}")
