# AI-Breakout-Scanner
ai_breakout_scanner/
├── app.py                          # التطبيق الرئيسي
├── requirements.txt
├── README.md
├── config.py                       # الإعدادات العامة
├── backend/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── market_data.py          # جلب بيانات السوق
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── squeeze_detector.py     # كشف الانضغاط
│   │   ├── volatility.py           # تحليل التقلبات
│   │   ├── compression.py          # تحليل الانضغاط
│   │   └── indicators.py           # مؤشرات فنية
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── predictor.py            # نموذج الذكاء الاصطناعي
│   │   └── scorer.py               # نظام التقييم
│   └── scanner/
│       ├── __init__.py
│       └── breakout_scanner.py     # الماسح الرئيسي
├── frontend/
│   ├── __init__.py
│   ├── assets/
│   │   └── style.css               # التصميم ثلاثي الأبعاد
│   ├── components/
│   │   ├── __init__.py
│   │   ├── sidebar.py              # الشريط الجانبي
│   │   ├── charts.py               # الرسوم البيانية
│   │   └── cards.py                # بطاقات المعلومات
│   └── pages/
│       ├── __init__.py
│       ├── dashboard.py            # لوحة التحكم
│       ├── scanner.py              # صفحة المسح
│       └── analyze.py              # تحليل سهم
└── utils/
    ├── __init__.py
    └── helpers.py                  # دوال مساعدة
