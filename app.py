import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime
import warnings
import importlib.util

# ============================================================================
# إعداد الصفحة الأولي لـ Streamlit
# ============================================================================
st.set_page_config(
    page_title="AI Breakout Scanner | ماسح الانفجار السعري",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)
warnings.filterwarnings('ignore')

# ============================================================================
# إعداد المسارات
# ============================================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = PROJECT_ROOT

BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
OPPORTUNITY_DIR = os.path.join(BACKEND_DIR, "opportunity")
PAGES_DIR = os.path.join(PROJECT_ROOT, "pages")

for path in [PROJECT_ROOT, BACKEND_DIR, OPPORTUNITY_DIR, PAGES_DIR]:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)

# ============================================================================
# تحميل إعدادات المشروع مباشرة من config.py
# نتجنب اسم module عام مثل "config" حتى لا يتعارض مع حزمة مثبتة
# في بيئة Streamlit Cloud.
# ============================================================================
def _load_project_config():
    config_path = os.path.join(PROJECT_ROOT, "config.py")
    if not os.path.isfile(config_path):
        return None

    spec = importlib.util.spec_from_file_location(
        "ai_breakout_project_config", config_path
    )
    if spec is None or spec.loader is None:
        return None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


try:
    _project_config = _load_project_config()
    if _project_config is None:
        raise ImportError("Project config.py was not found")
    STOCK_SYMBOLS = _project_config.STOCK_SYMBOLS
    APP_SETTINGS = _project_config.APP_SETTINGS
except (ImportError, AttributeError, OSError, TypeError, ValueError) as exc:
    # Fallback آمن حتى لا تتوقف الصفحة بالكامل بسبب ملف إعدادات.
    STOCK_SYMBOLS = {
        'الكل': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD'],
        'التكنولوجيا': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD']
    }
    APP_SETTINGS = {'title': 'AI Breakout Scanner'}
    print(f"Config fallback activated: {exc}")

# ============================================================================
# استيراد BreakoutScanner بشكل متأخر (لتجنب Deadlock)
# ============================================================================
_BreakoutScanner = None

def get_breakout_scanner():
    global _BreakoutScanner
    if _BreakoutScanner is None:
        from backend.scanner.breakout_scanner import BreakoutScanner
        _BreakoutScanner = BreakoutScanner
    return _BreakoutScanner

# بقية واجهة التطبيق في الملف الأصلي تستمر بعد هذا الجزء.
