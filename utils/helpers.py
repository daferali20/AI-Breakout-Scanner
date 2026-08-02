# utils/helpers.py
"""
دوال مساعدة للتطبيق
"""

import streamlit as st
import pandas as pd
import yfinance as yf
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def load_css():
    """تحميل ملف التصميم"""
    css_path = os.path.join(ROOT_DIR, "frontend", "assets", "style.css")
    
    if os.path.exists(css_path):
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
        except:
            load_inline_css()
    else:
        load_inline_css()

def load_inline_css():
    """تصميم مضمن"""
    st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%); }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px 30px;
        border-radius: 16px;
        margin-bottom: 25px;
        color: white;
        box-shadow: 0 8px 32px rgba(102,126,234,0.25);
    }
    .main-header h1 { color: #ffffff; font-size: 2rem; font-weight: 800; margin: 0; }
    .main-header p { color: rgba(255,255,255,0.9); font-size: 1rem; margin-top: 6px; }
    [data-testid="stSidebar"] {
        background: rgba(20,20,40,0.92) !important;
        backdrop-filter: blur(15px);
    }
    .metric-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 18px 20px;
        border-radius: 14px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        border-color: rgba(102,126,234,0.3);
    }
    .metric-card .value { font-size: 1.8rem; font-weight: 800; color: #ffffff; }
    .metric-card .label { font-size: 0.85rem; color: rgba(255,255,255,0.55); }
    .metric-card .icon { font-size: 1.6rem; margin-bottom: 4px; }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True)

def format_currency(value):
    """تنسيق العملة"""
    return f"${value:,.2f}" if value else "$0.00"

def format_percentage(value):
    """تنسيق النسبة"""
    return f"{value:.2f}%" if value else "0%"

def format_number(value):
    """تنسيق الأرقام"""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    return str(value)
