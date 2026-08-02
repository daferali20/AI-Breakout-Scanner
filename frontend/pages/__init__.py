# frontend/pages/__init__.py
"""
صفحات التطبيق
"""

from .dashboard import render as render_dashboard
from .scanner import render as render_scanner
from .analyze import render as render_analyze
from .market_data import render as render_market_data

__all__ = [
    'render_dashboard',
    'render_scanner',
    'render_analyze',
    'render_market_data'
]
