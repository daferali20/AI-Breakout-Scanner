# config.py
"""
الإعدادات العامة للمشروع - AI Breakout Scanner
"""

import os
from datetime import datetime

# ============================================================================
# إعدادات المشروع الأساسية
# ============================================================================

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
VERSION = '1.0.0'
APP_NAME = 'AI Breakout Scanner'

# ============================================================================
# قائمة الأسهم الأمريكية - موسعة ومصنفة
# ============================================================================

STOCK_SYMBOLS = {
    # التكنولوجيا
    'التكنولوجيا': [
        'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD',
        'INTC', 'NFLX', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM', 'CSCO',
        'QCOM', 'TXN', 'AVGO', 'INTU', 'AMAT', 'LRCX', 'MU', 'NOW',
        'PANW', 'SNPS', 'CDNS', 'MCHP', 'ADI', 'NXPI'
    ],
    # المالية
    'المالية': [
        'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'V', 'MA', 'AXP', 'BLK'
    ],
    # الرعاية الصحية
    'الرعاية الصحية': [
        'JNJ', 'UNH', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR',
        'LLY', 'AMGN', 'GILD', 'BMY'
    ],
    # الاستهلاك
    'الاستهلاك': [
        'WMT', 'PG', 'KO', 'PEP', 'COST', 'MCD', 'NKE', 'SBUX',
        'HD', 'LOW', 'TGT'
    ],
    # الطاقة والصناعة
    'الطاقة والصناعة': [
        'XOM', 'CVX', 'COP', 'BA', 'CAT', 'GE', 'HON', 'LMT',
        'RTX', 'UPS', 'UNP'
    ],
    # الاتصالات
    'الاتصالات': [
        'T', 'VZ', 'TMUS', 'CHTR'
    ],
    # العقارات
    'العقارات': [
        'AMT', 'PLD', 'CCI', 'EQIX', 'PSA'
    ]
}
[theme]
primaryColor="#667eea"
backgroundColor="#0f0f1a"
secondaryBackgroundColor="#1a1a2e"
textColor="#ffffff"
base="dark"
# قائمة مسطحة لجميع الرموز (للمسح السريع)
ALL_SYMBOLS = []
for sector, symbols in STOCK_SYMBOLS.items():
    ALL_SYMBOLS.extend(symbols)

# قائمة الرموز الرئيسية (الأكثر تداولاً)
MAIN_SYMBOLS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'AMD',
    'JPM', 'BAC', 'JNJ', 'UNH', 'WMT', 'PG', 'XOM', 'CVX'
]

# ============================================================================
# إعدادات الذكاء الاصطناعي
# ============================================================================

AI_SETTINGS = {
    'n_estimators': 100,
    'max_depth': 12,
    'min_samples_split': 5,
    'random_state': 42,
    'test_size': 0.2,
    'model_path': os.path.join(ROOT_DIR, 'models', 'breakout_model.pkl')
}

# ============================================================================
# إعدادات التحليل الفني
# ============================================================================

TECHNICAL_SETTINGS = {
    'bb_period': 20,
    'bb_std': 2.0,
    'kc_period': 20,
    'kc_atr_multiplier': 1.5,
    'rsi_period': 14,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'atr_period': 14,
    'volume_period': 20
}

# ============================================================================
# إعدادات المسح
# ============================================================================

SCAN_SETTINGS = {
    'default_min_score': 60,
    'default_min_prob': 55,
    'default_max_symbols': 20,
    'min_bars_required': 50,
    'lookback_period': '6mo',
    'intraday_period': '5d'
}

# ============================================================================
# إعدادات التطبيق
# ============================================================================

APP_SETTINGS = {
    'title': 'AI Breakout Scanner',
    'icon': '🚀',
    'layout': 'wide',
    'sidebar_state': 'expanded',
    'theme': 'dark',
    'cache_ttl': 300,  # 5 دقائق
    'max_results': 50
}

# ============================================================================
# إعدادات التصميم والألوان
# ============================================================================

COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#00E676',
    'danger': '#FF5252',
    'warning': '#FFC107',
    'info': '#29B6F6',
    'dark': '#1a1a2e',
    'light': '#f0f0f5'
}

# ============================================================================
# إعدادات قاعدة البيانات (اختياري)
# ============================================================================

DATABASE_SETTINGS = {
    'enabled': False,
    'path': os.path.join(ROOT_DIR, 'data', 'scanner.db'),
    'backup_enabled': True,
    'backup_interval': 86400  # 24 ساعة
}

# ============================================================================
# دوال مساعدة
# ============================================================================

def get_symbols_by_sector(sector: str = None) -> list:
    """
    الحصول على رموز الأسهم حسب القطاع
    
    Args:
        sector: اسم القطاع (اختياري)
    
    Returns:
        list: قائمة الرموز
    """
    if sector is None or sector == 'الكل':
        return ALL_SYMBOLS
    return STOCK_SYMBOLS.get(sector, [])

def get_sectors() -> list:
    """الحصول على قائمة القطاعات المتاحة"""
    return ['الكل'] + list(STOCK_SYMBOLS.keys())

def get_main_symbols(limit: int = 20) -> list:
    """الحصول على الرموز الرئيسية"""
    return MAIN_SYMBOLS[:limit]

def get_scan_settings() -> dict:
    """الحصول على إعدادات المسح الحالية"""
    return {
        'min_score': SCAN_SETTINGS['default_min_score'],
        'min_prob': SCAN_SETTINGS['default_min_prob'],
        'max_symbols': SCAN_SETTINGS['default_max_symbols'],
        'lookback': SCAN_SETTINGS['lookback_period']
    }

def get_technical_settings() -> dict:
    """الحصول على إعدادات التحليل الفني"""
    return TECHNICAL_SETTINGS.copy()

def get_ai_settings() -> dict:
    """الحصول على إعدادات الذكاء الاصطناعي"""
    return AI_SETTINGS.copy()

def get_app_settings() -> dict:
    """الحصول على إعدادات التطبيق"""
    return APP_SETTINGS.copy()

# ============================================================================
# التحقق من صحة الإعدادات
# ============================================================================

def validate_settings():
    """التحقق من صحة الإعدادات"""
    errors = []
    
    # التحقق من وجود المجلدات المطلوبة
    required_dirs = ['models', 'data']
    for dir_name in required_dirs:
        dir_path = os.path.join(ROOT_DIR, dir_name)
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path, exist_ok=True)
            except:
                errors.append(f'لا يمكن إنشاء المجلد: {dir_name}')
    
    return errors

# ============================================================================
# معلومات النظام
# ============================================================================

def get_system_info() -> dict:
    """الحصول على معلومات النظام"""
    return {
        'app_name': APP_NAME,
        'version': VERSION,
        'python_version': os.sys.version.split()[0],
        'os': os.name,
        'root_dir': ROOT_DIR,
        'timestamp': datetime.now().isoformat()
    }

# ============================================================================
# تصدير المتغيرات
# ============================================================================

__all__ = [
    'ROOT_DIR',
    'VERSION',
    'APP_NAME',
    'STOCK_SYMBOLS',
    'ALL_SYMBOLS',
    'MAIN_SYMBOLS',
    'AI_SETTINGS',
    'TECHNICAL_SETTINGS',
    'SCAN_SETTINGS',
    'APP_SETTINGS',
    'COLORS',
    'get_symbols_by_sector',
    'get_sectors',
    'get_main_symbols',
    'get_scan_settings',
    'get_technical_settings',
    'get_ai_settings',
    'get_app_settings',
    'validate_settings',
    'get_system_info'
]

# ============================================================================
# تنفيذ التحقق عند استيراد الملف
# ============================================================================

# التحقق من صحة الإعدادات
validation_errors = validate_settings()
if validation_errors:
    print(f"⚠️ تحذير: {len(validation_errors)} خطأ في الإعدادات:")
    for error in validation_errors:
        print(f"   - {error}")
