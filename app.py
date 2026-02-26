from __future__ import annotations
"""
app.py  —  Financial RAG Assistant  v5 (ORGANIZED)
===============================================================================
A single-file financial RAG system with:
  • Global search bar above market indicators
  • Multi-format upload (PDF/XLSX/XLS/CSV/DOCX/TXT)
  • Auto-generated analytics after ingest
  • Doc vs Market comparison in Analytics Dashboard
  • Live market data (stocks, forex, crypto, commodities)
  • News feeds with carousels
===============================================================================
"""

import os
import re
import json
import math
import io
import html
import datetime as dt
import threading
import time
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path

import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

# ============================================================================
# SECTION 1: INITIALIZATION & CONFIGURATION
# ============================================================================

load_dotenv()

# Page config must be first Streamlit command
st.set_page_config(
    page_title="Financial RAG Assistant",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# 1.1 Session State Initialization
# ----------------------------------------------------------------------------
def init_session_state():
    """Initialize all session state variables"""
    defaults = {
        "messages": [],
        "vectorstore": None,
        "uploaded_docs": 0,
        "chunk_count": 0,
        "file_names": [],
        "show_upload": False,
        "doc_full_text": "",
        "auto_metrics": [],
        "auto_generated": False,
        "search_query": "",
        "search_results": [],
        "fx_select_syms": ["USDINR=X", "USDJPY=X", "USDCNY=X", "EURUSD=X", "GBPUSD=X", "USDCHF=X"],
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

init_session_state()

# ----------------------------------------------------------------------------
# 1.2 Constants & Configuration
# ----------------------------------------------------------------------------
class Config:
    """Application configuration"""
    APP_NAME = "Financial RAG Assistant"
    VERSION = "5.0"
    
    # Paths
    DATA_DIR = Path("./data")
    CACHE_DIR = DATA_DIR / "cache"
    
    # Model settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # API settings
    YAHOO_FINANCE_BASE = "https://query1.finance.yahoo.com/v8/finance/chart"
    FEAR_GREED_API = "https://api.alternative.me/fng/"
    
    # Rate limiting
    RATE_LIMIT_CAPACITY = 30
    RATE_LIMIT_REFILL = 60.0

# Create directories
Config.DATA_DIR.mkdir(exist_ok=True)
Config.CACHE_DIR.mkdir(exist_ok=True)

# ============================================================================
# SECTION 2: STYLING & UI THEME
# ============================================================================

def inject_custom_css():
    """Inject all custom CSS styles"""
    st.markdown("""
    <style>
    /* Hide Streamlit chrome */
    #MainMenu, footer, header, [data-testid="stToolbar"],
    [data-testid="stDecoration"], .stDeployButton {
        display: none !important;
    }
    
    /* Responsive sidebar */
    [data-testid="collapsedControl"] {
        background: rgba(107,45,107,.18) !important;
        border: 1px solid rgba(139,58,139,.45) !important;
        border-radius: 8px !important;
        color: #C084C8 !important;
        top: 0.9rem !important;
    }
    
    /* Main theme colors */
    :root {
        --black: #07060C;
        --card: #0D0B12;
        --card-2: #120E1A;
        --panel: #0F0C16;
        --border: rgba(139,58,139,.22);
        --border-l: rgba(176,107,176,.45);
        --velvet: #6B2D6B;
        --velvet-gl: #B06BB0;
        --accent: #C084C8;
        --lilac: #D4A8D8;
        --text: #EDE8F5;
        --text-dim: #9A8AAA;
        --text-ghost: #4A3858;
        --green: #4ADE80;
        --red: #F87171;
        --gold: #F0C040;
    }
    
    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif !important;
        color: var(--text) !important;
    }
    
    .stApp, [data-testid="stAppViewContainer"] {
        background: 
            radial-gradient(ellipse 110% 55% at 0% 0%, rgba(107,45,107,.20) 0%, transparent 55%),
            radial-gradient(ellipse 80% 50% at 100% 100%, rgba(107,45,107,.14) 0%, transparent 55%),
            var(--black) !important;
    }
    
    /* Typography */
    h1, h2, h3, h4 {
        font-family: 'Cormorant Garamond', serif !important;
        color: var(--text) !important;
    }
    
    code, pre {
        font-family: 'Space Mono', monospace !important;
    }
    
    /* Components */
    [data-testid="stMetric"] {
        background: var(--card) !important;
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        padding: 0.9rem 1rem !important;
    }
    
    .stButton > button {
        background: transparent !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        color: var(--text-dim) !important;
        transition: all 0.22s ease !important;
    }
    
    .stButton > button:hover {
        background: rgba(107,45,107,.14) !important;
        border-color: var(--velvet-gl) !important;
        color: var(--accent) !important;
    }
    
    /* Global search bar */
    .gsearch-wrap {
        position: sticky;
        top: 0;
        z-index: 1000;
        background: linear-gradient(180deg, rgba(7,6,12,.97) 82%, transparent);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        padding: 0.55rem 0 0.3rem;
        margin-bottom: 0.9rem;
    }
    
    /* Analytics banner */
    .analytics-banner {
        background: linear-gradient(135deg, rgba(74,222,128,.07) 0%, rgba(107,45,107,.10) 100%);
        border: 1px solid rgba(74,222,128,.22);
        border-radius: 10px;
        padding: 0.7rem 1.1rem;
        margin-bottom: 1rem;
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }
    
    /* Search results */
    .sr-hit {
        background: var(--card-2);
        border: 1px solid var(--border);
        border-left: 3px solid var(--accent);
        border-radius: 0 8px 8px 0;
        padding: 0.55rem 0.9rem;
        margin-bottom: 0.4rem;
    }
    
    /* Comparison table */
    .cmp-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.75rem;
    }
    
    .cmp-table th {
        background: rgba(107,45,107,.18);
        border: 1px solid var(--border);
        padding: 0.45rem 0.8rem;
        font-family: 'Space Mono', monospace;
        color: var(--velvet-gl);
    }
    
    .cmp-table td {
        border: 1px solid var(--border);
        padding: 0.4rem 0.8rem;
        color: var(--text-dim);
    }
    
    .td-doc { color: var(--accent) !important; }
    .td-mkt { color: #86efac !important; }
    .td-pos { color: #4ade80 !important; }
    .td-neg { color: #f87171 !important; }
    .td-neu { color: var(--text-ghost) !important; }
    
    /* Hero header */
    .rag-header {
        position: relative;
        padding: 2rem 2.2rem;
        background: linear-gradient(135deg, rgba(107,45,107,.22) 0%, rgba(13,11,18,.98) 55%, rgba(107,45,107,.12) 100%);
        border: 1px solid rgba(255,255,255,.08);
        border-radius: 18px;
        margin-bottom: 1.4rem;
        overflow: hidden;
    }
    
    .rag-kicker {
        font-family: 'Space Mono', monospace;
        font-size: 0.6rem;
        letter-spacing: 0.3em;
        color: var(--velvet-gl);
        text-transform: uppercase;
        margin-bottom: 0.9rem;
    }
    
    .badge-row {
        display: flex;
        gap: 0.4rem;
        margin-top: 0.9rem;
        flex-wrap: wrap;
    }
    
    .badge {
        font-family: 'Space Mono', monospace;
        font-size: 0.62rem;
        padding: 0.2rem 0.55rem;
        border-radius: 999px;
        border: 1px solid var(--border);
        color: var(--text-ghost);
        background: rgba(255,255,255,.04);
    }
    
    .badge.v {
        border-color: rgba(139,58,139,.5);
        color: var(--accent);
        background: rgba(107,45,107,.12);
    }
    
    /* Stat strip */
    .stat-strip {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1px;
        background: rgba(107,45,107,.22);
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid rgba(107,45,107,.22);
        margin-bottom: 1.4rem;
    }
    
    .stat-cell {
        background: var(--card);
        padding: 1rem 1.2rem;
        position: relative;
    }
    
    .stat-lbl {
        font-family: 'Space Mono', monospace;
        font-size: 0.52rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--text-ghost);
        margin-bottom: 0.4rem;
    }
    
    .stat-val {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.7rem;
        font-weight: 300;
        color: var(--text);
    }
    
    /* Footer */
    .vfooter {
        text-align: center;
        padding: 1.8rem 0 0.5rem;
        position: relative;
        margin-top: 2.5rem;
    }
    
    .vfooter-text {
        font-family: 'Space Mono', monospace;
        font-size: 0.56rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--text-ghost);
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================================
# SECTION 3: DATA MODELS
# ============================================================================

class Document:
    """Document model for uploaded files"""
    def __init__(self, filename: str, content: str, metadata: Dict[str, Any] = None):
        self.filename = filename
        self.content = content
        self.metadata = metadata or {}
        self.uploaded_at = dt.datetime.now()
        self.doc_type = filename.split('.')[-1].upper() if '.' in filename else 'TXT'

class FinancialMetric:
    """Extracted financial metric"""
    def __init__(self, label: str, value: float, unit: str, category: str, raw_text: str):
        self.label = label
        self.value = value
        self.unit = unit
        self.category = category
        self.raw_text = raw_text

# ============================================================================
# SECTION 4: API & DATA FETCHING
# ============================================================================

class RateLimiter:
    """Token bucket rate limiter for API calls"""
    def __init__(self, capacity: int = 30, refill_every: float = 60.0):
        self.capacity = capacity
        self.tokens = float(capacity)
        self.refill_interval = refill_every / capacity
        self.lock = threading.Lock()
        self.last_refill = time.monotonic()
    
    def acquire(self, timeout: float = 5.0) -> bool:
        deadline = time.monotonic() + timeout
        while True:
            with self.lock:
                now = time.monotonic()
                earned = (now - self.last_refill) / self.refill_interval
                self.tokens = min(self.capacity, self.tokens + earned)
                self.last_refill = now
                
                if self.tokens >= 1.0:
                    self.tokens -= 1.0
                    return True
            
            if time.monotonic() >= deadline:
                return False
            time.sleep(0.05)

class MarketDataFetcher:
    """Fetch real-time market data from various sources"""
    
    HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    # Symbol definitions
    COMMODITIES = {
        "GC=F": ("Gold", "$/oz", "🪙", 2),
        "SI=F": ("Silver", "$/oz", "⚪", 3),
        "CL=F": ("Crude Oil", "$/bbl", "🛢️", 2),
        "PL=F": ("Platinum", "$/oz", "💎", 2),
        "PA=F": ("Palladium", "$/oz", "✨", 2),
        "HG=F": ("Copper", "$/lb", "🟤", 3),
    }
    
    CRYPTO = {
        "BTC-USD": ("Bitcoin", "BTC", "₿", 2),
        "ETH-USD": ("Ethereum", "ETH", "Ξ", 2),
        "BNB-USD": ("BNB", "BNB", "🔶", 2),
        "SOL-USD": ("Solana", "SOL", "◎", 2),
        "XRP-USD": ("XRP", "XRP", "✕", 4),
        "DOGE-USD": ("Dogecoin", "DOGE", "🐕", 5),
        "ADA-USD": ("Cardano", "ADA", "🔵", 4),
        "AVAX-USD": ("Avalanche", "AVAX", "🔺", 2),
    }
    
    INDICES = {
        "^GSPC": {"name": "S&P 500", "flag": "🇺🇸"},
        "^IXIC": {"name": "NASDAQ", "flag": "🇺🇸"},
        "^FTSE": {"name": "FTSE 100", "flag": "🇬🇧"},
        "^NSEI": {"name": "NIFTY 50", "flag": "🇮🇳"},
        "^N225": {"name": "Nikkei", "flag": "🇯🇵"},
        "^GDAXI": {"name": "DAX", "flag": "🇩🇪"},
    }
    
    FX = {
        "USDINR=X": {"label": "USD/INR", "flag": "🇮🇳", "name": "Indian Rupee", "invert": False},
        "USDJPY=X": {"label": "USD/JPY", "flag": "🇯🇵", "name": "Japanese Yen", "invert": False},
        "USDCNY=X": {"label": "USD/CNY", "flag": "🇨🇳", "name": "Chinese Yuan", "invert": False},
        "EURUSD=X": {"label": "EUR/USD", "flag": "🇪🇺", "name": "Euro", "invert": True},
        "GBPUSD=X": {"label": "GBP/USD", "flag": "🇬🇧", "name": "British Pound", "invert": True},
        "USDCHF=X": {"label": "USD/CHF", "flag": "🇨🇭", "name": "Swiss Franc", "invert": False},
        "USDCAD=X": {"label": "USD/CAD", "flag": "🇨🇦", "name": "Canadian Dollar", "invert": False},
        "USDAUD=X": {"label": "USD/AUD", "flag": "🇦🇺", "name": "Australian Dollar", "invert": False},
    }
    
    def __init__(self):
        self.rate_limiter = RateLimiter(
            Config.RATE_LIMIT_CAPACITY,
            Config.RATE_LIMIT_REFILL
        )
    
    def _throttled_get(self, url: str, timeout: int = 10) -> requests.Response:
        """Make throttled GET request"""
        if not self.rate_limiter.acquire(timeout=4.0):
            raise RuntimeError("Rate limit reached - wait a few seconds")
        return requests.get(url, headers=self.HEADERS, timeout=timeout)
    
    @st.cache_data(ttl=60)
    def fetch_quote(self, symbol: str) -> Optional[Dict[str, float]]:
        """Fetch current quote for a symbol"""
        url = f"{Config.YAHOO_FINANCE_BASE}/{symbol}?range=2d&interval=1d"
        try:
            response = self._throttled_get(url, timeout=8)
            response.raise_for_status()
            data = response.json()
            
            quotes = data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            prices = [q for q in quotes if q is not None]
            
            if len(prices) >= 2:
                return {
                    "price": prices[-1],
                    "pct": (prices[-1] - prices[-2]) / prices[-2] * 100
                }
            elif len(prices) == 1:
                return {"price": prices[-1], "pct": 0.0}
        except Exception:
            return None
    
    @st.cache_data(ttl=60)
    def fetch_multi_quotes(self, symbols: Tuple[str]) -> Dict[str, Dict]:
        """Fetch quotes for multiple symbols"""
        return {s: q for s in symbols if (q := self.fetch_quote(s))}
    
    @st.cache_data(ttl=300)
    def fetch_historical(self, symbol: str, period: str, interval: str) -> Optional[pd.Series]:
        """Fetch historical price data"""
        url = f"{Config.YAHOO_FINANCE_BASE}/{symbol}?range={period}&interval={interval}"
        try:
            response = self._throttled_get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            result = data["chart"]["result"][0]
            
            timestamps = result["timestamp"]
            closes = result["indicators"]["quote"][0]["close"]
            
            index = pd.to_datetime(timestamps, unit="s", utc=True).tz_convert("US/Eastern")
            series = pd.Series(closes, index=index, name=symbol).dropna()
            return series
        except Exception:
            return None
    
    @st.cache_data(ttl=300)
    def fetch_fear_greed(self) -> Dict[str, Any]:
        """Fetch Fear & Greed index"""
        try:
            response = self._throttled_get(f"{Config.FEAR_GREED_API}?limit=1", timeout=8)
            data = response.json()["data"][0]
            return {
                "value": int(data["value"]),
                "label": data["value_classification"]
            }
        except Exception:
            return {"value": 50, "label": "Neutral"}

# ============================================================================
# SECTION 5: DOCUMENT PROCESSING
# ============================================================================

class DocumentProcessor:
    """Handle document extraction and processing"""
    
    @staticmethod
    def extract_text_from_file(file) -> str:
        """Extract text from various file formats"""
        filename = file.name.lower()
        content = file.read()
        
        # PDF
        if filename.endswith(".pdf"):
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(content))
            return " ".join(page.extract_text() or "" for page in reader.pages)
        
        # Excel
        if filename.endswith((".xlsx", ".xls")):
            try:
                dfs = pd.read_excel(io.BytesIO(content), sheet_name=None, dtype=str)
                parts = []
                for sheet_name, df in dfs.items():
                    parts.append(f"=== Sheet: {sheet_name} ===")
                    parts.append(df.fillna("").to_string(index=False))
                return "\n".join(parts)
            except Exception as e:
                return f"[Excel parse error: {e}]"
        
        # CSV
        if filename.endswith(".csv"):
            try:
                df = pd.read_csv(io.BytesIO(content), dtype=str)
                return df.fillna("").to_string(index=False)
            except Exception as e:
                return f"[CSV parse error: {e}]"
        
        # DOCX
        if filename.endswith(".docx"):
            try:
                import zipfile
                import xml.etree.ElementTree as ET
                
                with zipfile.ZipFile(io.BytesIO(content)) as zip_file:
                    xml_content = zip_file.read("word/document.xml")
                
                tree = ET.fromstring(xml_content)
                namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
                
                paragraphs = []
                for paragraph in tree.iter(f"{namespace}p"):
                    texts = [t.text or "" for t in paragraph.iter(f"{namespace}t")]
                    line = "".join(texts).strip()
                    if line:
                        paragraphs.append(line)
                
                return "\n".join(paragraphs)
            except Exception as e:
                return f"[DOCX parse error: {e}]"
        
        # TXT / plain text
        for encoding in ("utf-8", "latin-1", "cp1252"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        
        return content.decode("utf-8", errors="ignore")
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        return splitter.split_text(text)

# ============================================================================
# SECTION 6: FINANCIAL METRICS EXTRACTION
# ============================================================================

class MetricsExtractor:
    """Extract financial metrics from document text"""
    
    # Financial taxonomy for categorization
    TAXONOMY = {
        "Income Statement": [
            "revenue", "net revenue", "total revenue", "net sales", "gross profit",
            "gross margin", "operating income", "ebit", "ebitda", "net income",
            "net profit", "earnings", "eps", "earnings per share", "diluted eps",
            "operating expense", "cost of revenue", "cogs", "research and development",
            "r&d", "sg&a", "tax", "income tax", "interest expense"
        ],
        "Balance Sheet": [
            "total assets", "total liabilities", "shareholders equity",
            "stockholders equity", "book value", "cash and equivalents",
            "accounts receivable", "inventory", "goodwill", "long-term debt",
            "current liabilities", "current assets", "retained earnings"
        ],
        "Cash Flow": [
            "operating cash flow", "cash from operations", "free cash flow", "fcf",
            "capital expenditure", "capex", "investing activities",
            "financing activities", "dividends paid", "share repurchase",
            "buyback", "depreciation", "amortization"
        ],
        "Ratios": [
            "p/e ratio", "price to earnings", "p/b ratio", "price to book",
            "roe", "return on equity", "roa", "return on assets",
            "debt to equity", "current ratio", "quick ratio",
            "gross margin", "net margin", "operating margin",
            "ebitda margin", "dividend yield", "payout ratio"
        ],
        "Risk Factors": [
            "risk", "uncertainty", "competition", "regulatory", "litigation",
            "geopolitical", "macroeconomic", "supply chain", "inflation",
            "interest rate risk", "credit risk", "liquidity risk", "cyber"
        ],
    }
    
    # Metric extraction patterns
    METRIC_PATTERNS = [
        ("Revenue", "USD", r"(?:total\s+)?(?:net\s+)?revenue[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
        ("Net Income", "USD", r"net\s+income[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
        ("Gross Profit", "USD", r"gross\s+profit[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
        ("Operating Income", "USD", r"operating\s+income[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
        ("EBITDA", "USD", r"ebitda[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
        ("Free Cash Flow", "USD", r"free\s+cash\s+flow[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
        ("CapEx", "USD", r"capital\s+expenditures?[^\n]{0,60}?\$\s*([\d,\.]+)\s*(billion|million|B|M)?"),
        ("EPS (Basic)", "USD", r"basic\s+(?:earnings|eps)[^\n]{0,60}?\$\s*([\d,\.]+)"),
        ("EPS (Diluted)", "USD", r"diluted\s+(?:earnings|eps)[^\n]{0,60}?\$\s*([\d,\.]+)"),
        ("Gross Margin", "%", r"gross\s+margin[^\n]{0,60}?([\d\.]+)\s*%"),
        ("Net Margin", "%", r"net\s+(?:profit\s+)?margin[^\n]{0,60}?([\d\.]+)\s*%"),
        ("Operating Margin", "%", r"operating\s+margin[^\n]{0,60}?([\d\.]+)\s*%"),
        ("ROE", "%", r"return\s+on\s+equity[^\n]{0,60}?([\d\.]+)\s*%"),
        ("ROA", "%", r"return\s+on\s+assets[^\n]{0,60}?([\d\.]+)\s*%"),
        ("Debt/Equity", "x", r"debt[- ]to[- ]equity[^\n]{0,60}?([\d\.]+)"),
        ("Current Ratio", "x", r"current\s+ratio[^\n]{0,60}?([\d\.]+)"),
    ]
    
    SCALE_FACTORS = {
        "billion": 1e9, "b": 1e9,
        "million": 1e6, "m": 1e6,
        None: 1.0, "": 1.0
    }
    
    CATEGORY_COLORS = {
        "Income Statement": "#C084C8",
        "Balance Sheet": "#60a5fa",
        "Cash Flow": "#4ade80",
        "Ratios": "#F0C040",
        "Per Share": "#fb923c",
        "Risk Factors": "#f87171",
        "Other": "#9A8AAA"
    }
    
    @classmethod
    def tag_chunk(cls, text: str) -> List[str]:
        """Tag text chunk with financial categories"""
        text_lower = text.lower()
        return [
            category for category, keywords in cls.TAXONOMY.items()
            if any(keyword in text_lower for keyword in keywords)
        ]
    
    @classmethod
    def extract_metrics(cls, text: str) -> List[FinancialMetric]:
        """Extract financial metrics from text"""
        text_lower = text.lower()
        results = []
        seen = set()
        
        for label, unit, pattern in cls.METRIC_PATTERNS:
            for match in re.finditer(pattern, text_lower, re.IGNORECASE):
                # Extract numeric value
                value_str = match.group(1).replace(",", "")
                
                # Extract scale (billion/million)
                scale_key = None
                if match.lastindex and match.lastindex >= 2:
                    scale_key = (match.group(2) or "").lower()
                
                try:
                    value = float(value_str) * cls.SCALE_FACTORS.get(scale_key, 1.0)
                except ValueError:
                    continue
                
                # Avoid duplicates
                if label in seen:
                    continue
                seen.add(label)
                
                # Determine category
                category = cls._get_category(label)
                
                results.append(FinancialMetric(
                    label=label,
                    value=value,
                    unit=unit,
                    category=category,
                    raw_text=match.group(0).strip()[:120]
                ))
        
        return results
    
    @classmethod
    def _get_category(cls, label: str) -> str:
        """Get category for a metric label"""
        label_lower = label.lower()
        
        if any(k in label_lower for k in ["eps", "diluted", "basic"]):
            return "Per Share"
        if any(k in label_lower for k in ["margin", "roe", "roa", "ratio", "debt"]):
            return "Ratios"
        if any(k in label_lower for k in ["cash flow", "fcf", "capex"]):
            return "Cash Flow"
        if any(k in label_lower for k in ["revenue", "income", "profit", "ebitda"]):
            return "Income Statement"
        
        return "Other"
    
    @classmethod
    def format_value(cls, value: float, unit: str) -> str:
        """Format metric value for display"""
        if unit == "USD":
            if value >= 1e9:
                return f"${value/1e9:.2f}B"
            if value >= 1e6:
                return f"${value/1e6:.1f}M"
            if value >= 1e3:
                return f"${value/1e3:.1f}K"
            return f"${value:.2f}"
        
        if unit == "%":
            return f"{value:.1f}%"
        
        if unit == "x":
            return f"{value:.2f}x"
        
        return f"{value:,.2f}"

# ============================================================================
# SECTION 7: RAG ENGINE
# ============================================================================

class RAGEngine:
    """Retrieval-Augmented Generation engine"""
    
    def __init__(self):
        from sentence_transformers import SentenceTransformer
        import chromadb
        from chromadb.config import Settings
        
        self.embedding_model = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.chroma_client = chromadb.PersistentClient(
            path=str(Config.DATA_DIR / "chromadb")
        )
        
        # Create or get collection
        try:
            self.collection = self.chroma_client.get_collection("financial_docs")
        except:
            self.collection = self.chroma_client.create_collection(
                name="financial_docs",
                metadata={"hnsw:space": "cosine"}
            )
    
    def add_documents(self, documents: List[Document], chunks: List[str], chunk_metadatas: List[Dict]):
        """Add document chunks to vector store"""
        if not chunks:
            return
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(
            chunks,
            normalize_embeddings=True
        ).tolist()
        
        # Generate IDs
        ids = [f"{doc.filename}_{i}" for doc in documents for i in range(len(chunks))]
        
        # Add to collection
        self.collection.add(
            embeddings=embeddings,
            documents=chunks,
            metadatas=chunk_metadatas,
            ids=ids
        )
    
    def search(self, query: str, n_results: int = 5) -> Dict:
        """Search for relevant chunks"""
        query_embedding = self.embedding_model.encode(
            [query],
            normalize_embeddings=True
        ).tolist()
        
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        return results

# ============================================================================
# SECTION 8: UI COMPONENTS
# ============================================================================

class UIComponents:
    """Reusable UI components"""
    
    @staticmethod
    def metric_card(metric: FinancialMetric) -> str:
        """Generate HTML for a metric card"""
        color = MetricsExtractor.CATEGORY_COLORS.get(metric.category, "#9A8AAA")
        value = MetricsExtractor.format_value(metric.value, metric.unit)
        
        return f"""
        <div style="background:#120E1A; border:1px solid rgba(139,58,139,.22);
                    border-top:2px solid {color}; border-radius:10px; padding:0.8rem 1rem;">
            <div style="font-family:Space Mono,monospace; font-size:0.52rem;
                        letter-spacing:0.15em; text-transform:uppercase;
                        color:#4A3858; margin-bottom:0.35rem;">
                {metric.label}
            </div>
            <div style="font-family:'Cormorant Garamond',serif; font-size:1.6rem;
                        font-weight:300; color:#EDE8F5; line-height:1;">
                {value}
            </div>
            <div style="font-family:Space Mono,monospace; font-size:0.46rem;
                        color:{color}; margin-top:0.3rem; text-transform:uppercase;">
                {metric.category}
            </div>
        </div>
        """
    
    @staticmethod
    def source_card(filename: str, score: float, preview: str) -> str:
        """Generate HTML for a source citation card"""
        return f"""
        <div style="background:#0D0B12; border:1px solid rgba(139,58,139,.22);
                    border-left:3px solid #C084C8; border-radius:0 8px 8px 0;
                    padding:0.7rem 0.9rem; margin:0.4rem 0;">
            <div style="font-family:Space Mono,monospace; font-size:0.7rem;
                        color:#C084C8; margin-bottom:0.15rem;">
                📄 {filename}
            </div>
            <div style="font-family:Space Mono,monospace; font-size:0.62rem;
                        color:#4A3858; margin-bottom:0.2rem;">
                relevance: {score}
            </div>
            <div style="font-size:0.82rem; color:#9A8AAA; line-height:1.55;">
                {preview}…
            </div>
        </div>
        """
    
    @staticmethod
    def price_chip(symbol: str, name: str, price: float, pct: float,
                   prefix: str = "$", suffix: str = "", decimals: int = 2,
                   icon: str = "") -> str:
        """Generate HTML for a price chip"""
        arrow = "▲" if pct > 0.005 else ("▼" if pct < -0.005 else "●")
        cls = "up" if pct > 0.005 else ("down" if pct < -0.005 else "flat")
        
        icon_html = f'<span style="font-size:1rem; margin-right:0.2rem;">{icon}</span>' if icon else ""
        
        return f"""
        <div style="background:#120E1A; border:1px solid rgba(139,58,139,.22);
                    border-radius:10px; padding:0.75rem 1rem;">
            <div style="font-size:0.6rem; color:#C084C8; font-weight:700;
                        white-space:nowrap;">
                {icon_html}{symbol}
            </div>
            <div style="font-size:0.5rem; color:#4A3858; margin-bottom:0.2rem;">
                {name}
            </div>
            <div style="font-family:'Cormorant Garamond',serif; font-size:1.5rem;
                        font-weight:300; color:#EDE8F5; line-height:1;">
                {prefix}{price:,.{decimals}f}{suffix}
            </div>
            <div style="font-size:0.58rem; color:{'#4ade80' if pct>0 else '#f87171' if pct<0 else '#4A3858'};">
                {arrow} {abs(pct):.2f}%
            </div>
        </div>
        """

# ============================================================================
# SECTION 9: NEWS & RSS
# ============================================================================

class NewsFetcher:
    """Fetch and process news from various sources"""
    
    # News sources configuration
    NEWS_SOURCES = {
        "📰 Business Standard": {
            "rss": "https://www.business-standard.com/rss/home_page_top_stories.rss",
            "tag": "Markets"
        },
        "📰 Economic Times": {
            "rss": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
            "tag": "Markets"
        },
        "📰 Mint": {
            "rss": "https://www.livemint.com/rss/markets",
            "tag": "Markets"
        },
        "🏛️ RBI Notifications": {
            "rss": "https://www.rbi.org.in/Scripts/Notifications_Rss.aspx",
            "tag": "Policy"
        },
        "🏛️ Finance Ministry": {
            "rss": "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=3",
            "tag": "Policy"
        },
    }
    
    # RSS feed URLs for carousels
    CAROUSEL_FEEDS = [
        ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg", "#4ADE80"),
        ("https://feeds.a.dj.com/rss/RSSMarketsMain.xml", "Wall Street Journal", "#F0C040"),
        ("https://www.ft.com/?format=rss", "Financial Times", "#FB923C"),
        ("https://www.cnbc.com/id/100003114/device/rss/rss.html", "CNBC", "#C084C8"),
    ]
    
    POLICY_FEEDS = [
        ("https://www.federalreserve.gov/feeds/press_all.xml", "Federal Reserve", "🇺🇸", "#60A5FA"),
        ("https://www.ecb.europa.eu/rss/press.html", "ECB", "🇪🇺", "#34D399"),
        ("https://www.imf.org/en/News/rss", "IMF", "🌐", "#A78BFA"),
    ]
    
    FALLBACK_IMAGES = {
        "Bloomberg": "https://assets.bbhub.io/company/sites/51/2019/08/BBG-Logo-Black.png",
        "Wall Street Journal": "https://s.wsj.net/media/wsj_logo_black_sm.png",
        "Financial Times": "https://about.ft.com/files/2020/04/ft_logo.png",
        "CNBC": "https://www.cnbc.com/2020/07/21/cnbc-social-card-2019.jpg",
    }
    
    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_rss(url: str, max_items: int = 6) -> List[Dict]:
        """Fetch and parse RSS feed"""
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; NewsBot/1.0)",
            "Accept": "application/rss+xml,*/*"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=12)
            response.raise_for_status()
            
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            
            items = root.findall(".//item")
            results = []
            
            for item in items[:max_items]:
                title = (item.findtext("title") or "").strip()
                link = (item.findtext("link") or "").strip()
                pub_date = (item.findtext("pubDate") or "").strip()
                
                # Parse date
                try:
                    from email.utils import parsedate_to_datetime
                    pub_date = parsedate_to_datetime(pub_date).strftime("%d %b, %H:%M")
                except:
                    pub_date = pub_date[:16]
                
                if title:
                    results.append({
                        "title": title,
                        "link": link,
                        "date": pub_date,
                    })
            
            return results
        except Exception:
            return []
    
    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_carousel_news() -> List[Dict]:
        """Fetch news for carousel display"""
        news = []
        
        for url, source, color in NewsFetcher.CAROUSEL_FEEDS:
            items = NewsFetcher._fetch_rss_with_images(url, source, color, max_items=4)
            news.extend(items)
        
        return news[:16]
    
    @staticmethod
    @st.cache_data(ttl=600)
    def fetch_policy_news() -> List[Dict]:
        """Fetch policy news for carousel"""
        policy = []
        
        for url, source, flag, color in NewsFetcher.POLICY_FEEDS:
            items = NewsFetcher._fetch_rss_with_images(url, source, color, max_items=3)
            for item in items:
                item["flag"] = flag
                item["policy"] = True
            policy.extend(items)
        
        return policy[:12]
    
    @staticmethod
    def _fetch_rss_with_images(url: str, source: str, accent: str, max_items: int = 6) -> List[Dict]:
        """Fetch RSS with image extraction"""
        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/rss+xml,*/*"}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            text = response.text
        except Exception:
            return []
        
        results = []
        
        # Extract items
        items = re.findall(r"<item[^>]*>(.*?)</item>", text, re.DOTALL) or \
                re.findall(r"<entry[^>]*>(.*?)</entry>", text, re.DOTALL)
        
        for item in items[:max_items]:
            # Extract title
            title_match = re.search(r"<title[^>]*>(.*?)</title>", item, re.DOTALL | re.IGNORECASE)
            if not title_match:
                continue
            
            raw_title = title_match.group(1).strip()
            
            # Clean CDATA
            cdata = re.match(r"<!\[CDATA\[(.*?)\]\]>", raw_title, re.DOTALL)
            title = cdata.group(1).strip() if cdata else raw_title
            title = re.sub(r"<[^>]+>", "", title).strip()
            
            if not title or len(title) < 10:
                continue
            
            # Extract link
            link_match = (re.search(r'<link[^>]*href=["\'](https?://[^"\'> ]+)["\']', item, re.IGNORECASE) or
                          re.search(r"<link>(.*?)</link>", item, re.DOTALL | re.IGNORECASE))
            link = link_match.group(1).strip() if link_match else "#"
            
            # Extract image
            image = ""
            media_match = re.search(r'<media:(?:content|thumbnail)[^>]+url=["\'](https?://[^"\']+)["\']', item, re.IGNORECASE)
            if media_match:
                image = media_match.group(1)
            
            if not image:
                enclosure_match = re.search(r'<enclosure[^>]+url=["\'](https?://[^"\']+(?:jpg|jpeg|png|webp))["\']', item, re.IGNORECASE)
                if enclosure_match:
                    image = enclosure_match.group(1)
            
            if not image:
                image = NewsFetcher.FALLBACK_IMAGES.get(source, "")
            
            results.append({
                "title": title,
                "link": link,
                "source": source,
                "accent": accent,
                "img_url": image
            })
        
        return results
    
    @staticmethod
    def build_carousel_html(items: List[Dict], is_policy: bool = False, height_px: int = 380) -> str:
        """Build HTML for news carousel"""
        accent = "linear-gradient(90deg,#3B82F6,#A78BFA)" if is_policy else "linear-gradient(90deg,#6B2D6B,#C084C8)"
        title = "Policy & Government Decisions" if is_policy else "Financial Headlines"
        color = "#3B82F6" if is_policy else "#C084C8"
        bg_color = "#0A0F1E" if is_policy else "#120E1A"
        border_color = "rgba(59,130,246,.3)" if is_policy else "rgba(139,58,139,.3)"
        
        slides_json = json.dumps([{
            "title": item["title"],
            "link": item.get("link", "#"),
            "source": item.get("source", ""),
            "accent": item.get("accent", "#C084C8"),
            "img": item.get("img_url", ""),
            "flag": item.get("flag", ""),
            "policy": item.get("policy", False)
        } for item in items])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                * {{ box-sizing: border-box; margin: 0; padding: 0; }}
                body {{
                    background: #0D0B12;
                    font-family: 'Segoe UI', system-ui, sans-serif;
                    color: #EDE8F5;
                    height: {height_px}px;
                    overflow: hidden;
                }}
                .carousel-wrapper {{
                    background: #0D0B12;
                    border: 1px solid {border_color};
                    border-radius: 14px;
                    height: {height_px}px;
                    display: flex;
                    flex-direction: column;
                    overflow: hidden;
                    position: relative;
                }}
                .carousel-header {{
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                    padding: 0.85rem 1.1rem 0.6rem;
                    border-bottom: 1px solid rgba(139,58,139,.12);
                }}
                .carousel-title {{
                    font-family: Georgia, serif;
                    font-size: 1rem;
                    font-weight: 300;
                    color: #EDE8F5;
                    display: flex;
                    align-items: center;
                    gap: 0.5rem;
                }}
                .carousel-title::before {{
                    content: '';
                    display: inline-block;
                    width: 3px;
                    height: 1rem;
                    background: {accent};
                    border-radius: 2px;
                }}
                .nav-button {{
                    background: rgba(107,45,107,.15);
                    border: 1px solid {border_color};
                    color: {color};
                    width: 26px;
                    height: 26px;
                    border-radius: 50%;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.2s;
                }}
                .nav-button:hover {{
                    background: rgba(107,45,107,.35);
                }}
                .dot {{
                    width: 6px;
                    height: 6px;
                    border-radius: 50%;
                    background: rgba(139,58,139,.3);
                    border: 1px solid rgba(139,58,139,.4);
                    cursor: pointer;
                    transition: all 0.2s;
                }}
                .dot.active {{
                    background: {color};
                    transform: scale(1.3);
                }}
                .slides-container {{
                    flex: 1;
                    position: relative;
                    overflow: hidden;
                }}
                .slide {{
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    display: flex;
                    flex-direction: column;
                    opacity: 0;
                    transform: translateX(40px);
                    transition: opacity 0.45s, transform 0.45s;
                    pointer-events: none;
                }}
                .slide.active {{
                    opacity: 1;
                    transform: translateX(0);
                    pointer-events: all;
                }}
                .slide-image {{
                    width: 100%;
                    height: 160px;
                    object-fit: cover;
                    background: #120E1A;
                }}
                .slide-content {{
                    padding: 0.7rem 1rem 0.5rem;
                    display: flex;
                    flex-direction: column;
                    gap: 0.3rem;
                    flex: 1;
                    background: {bg_color};
                }}
                .slide-source {{
                    font-family: 'Courier New', monospace;
                    font-size: 0.58rem;
                    letter-spacing: 0.14em;
                    text-transform: uppercase;
                    display: flex;
                    align-items: center;
                    gap: 0.4rem;
                }}
                .slide-title {{
                    font-size: 0.9rem;
                    font-weight: 500;
                    color: #EDE8F5;
                    line-height: 1.45;
                    text-decoration: none;
                    display: -webkit-box;
                    -webkit-line-clamp: 3;
                    -webkit-box-orient: vertical;
                    overflow: hidden;
                }}
                .slide-title:hover {{
                    color: {color};
                    text-decoration: underline;
                }}
                .progress-bar {{
                    height: 2px;
                    background: rgba(139,58,139,.12);
                    overflow: hidden;
                }}
                .progress-fill {{
                    height: 100%;
                    width: 0%;
                    background: {accent};
                    transition: width 3s linear;
                }}
                .carousel-footer {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: 0.3rem 1rem;
                    background: rgba(0,0,0,.3);
                    font-family: 'Courier New', monospace;
                    font-size: 0.48rem;
                    color: #4A3858;
                }}
            </style>
        </head>
        <body>
            <div class="carousel-wrapper" id="carousel">
                <div class="carousel-header">
                    <div class="carousel-title">{title}</div>
                    <div style="display: flex; align-items: center; gap: 0.4rem;">
                        <div id="dots" style="display: flex; gap: 4px;"></div>
                        <button class="nav-button" id="prev">‹</button>
                        <button class="nav-button" id="next">›</button>
                    </div>
                </div>
                <div class="slides-container" id="slides"></div>
                <div class="progress-bar">
                    <div class="progress-fill" id="progress"></div>
                </div>
                <div class="carousel-footer">
                    <span>● live · 10min cache</span>
                    <span id="counter">1/1</span>
                </div>
            </div>
            <script>
                (function() {{
                    const slides = {slides_json};
                    let currentIndex = 0;
                    let paused = false;
                    let timer = null;
                    
                    const slidesContainer = document.getElementById('slides');
                    const dotsContainer = document.getElementById('dots');
                    const counter = document.getElementById('counter');
                    const progress = document.getElementById('progress');
                    
                    // Create slides and dots
                    slides.forEach((slide, index) => {{
                        const slideDiv = document.createElement('div');
                        slideDiv.className = 'slide' + (index === 0 ? ' active' : '');
                        slideDiv.id = 'slide' + index;
                        
                        const imageHtml = slide.img 
                            ? `<img class="slide-image" src="$ {slide.img}" onerror="this.style.display='none';this.nextElementSibling.style.display='flex';">`
                            : '';
                        
                        slideDiv.innerHTML = `
                            $ {imageHtml}
                            <div class="slide-content">
                                <div class="slide-source">
                                    <span style="color:$ {slide.accent}">$ {slide.flag} $ {slide.source}</span>
                                </div>
                                <a class="slide-title" href="$ {slide.link}" target="_blank">$ {slide.title}</a>
                            </div>
                        `;
                        slidesContainer.appendChild(slideDiv);
                        
                        const dot = document.createElement('span');
                        dot.className = 'dot' + (index === 0 ? ' active' : '');
                        dot.id = 'dot' + index;
                        dot.onclick = () => goTo(index);
                        dotsContainer.appendChild(dot);
                    }});
                    
                    function goTo(n) {{
                        const prev = currentIndex;
                        currentIndex = ((n % slides.length) + slides.length) % slides.length;
                        if (prev === currentIndex) return;
                        
                        const oldSlide = document.getElementById('slide' + prev);
                        const newSlide = document.getElementById('slide' + currentIndex);
                        const oldDot = document.getElementById('dot' + prev);
                        const newDot = document.getElementById('dot' + currentIndex);
                        
                        if (oldSlide) oldSlide.className = 'slide';
                        if (newSlide) newSlide.className = 'slide active';
                        if (oldDot) oldDot.className = 'dot';
                        if (newDot) newDot.className = 'dot active';
                        
                        counter.textContent = (currentIndex + 1) + '/' + slides.length;
                        startProgress();
                    }}
                    
                    function startProgress() {{
                        progress.style.transition = 'none';
                        progress.style.width = '0%';
                        setTimeout(() => {{
                            progress.style.transition = 'width 3s linear';
                            progress.style.width = '100%';
                        }}, 40);
                    }}
                    
                    document.getElementById('next').onclick = () => goTo(currentIndex + 1);
                    document.getElementById('prev').onclick = () => goTo(currentIndex - 1);
                    
                    document.getElementById('carousel').addEventListener('mouseenter', () => { paused = true; });
                    document.getElementById('carousel').addEventListener('mouseleave', () => { paused = false; });
                    
                    counter.textContent = '1/' + slides.length;
                    startProgress();
                    
                    setInterval(() => {{
                        if (!paused) goTo(currentIndex + 1);
                    }}, 3000);
                }})();
            </script>
        </body>
        </html>
        """

# ============================================================================
# SECTION 10: ANALYTICS DASHBOARD
# ============================================================================

class AnalyticsDashboard:
    """Analytics dashboard components"""
    
    # Sector benchmarks for comparison
    SECTOR_BENCHMARKS = {
        "Gross Margin": {
            "Technology": 55, "Financials": 40, "Energy": 30, "Healthcare": 50,
            "Industrials": 33, "Consumer Discretionary": 30, "Consumer Staples": 28,
            "S&P 500 Avg": 38
        },
        "Net Margin": {
            "Technology": 22, "Financials": 18, "Energy": 8, "Healthcare": 14,
            "Industrials": 9, "Consumer Discretionary": 6, "Consumer Staples": 8,
            "S&P 500 Avg": 11.5
        },
        "Operating Margin": {
            "Technology": 28, "Financials": 20, "Energy": 12, "Healthcare": 16,
            "Industrials": 12, "Consumer Discretionary": 9, "Consumer Staples": 10,
            "S&P 500 Avg": 15
        },
        "ROE": {
            "Technology": 35, "Financials": 12, "Energy": 18, "Healthcare": 22,
            "Industrials": 20, "Consumer Discretionary": 28, "Consumer Staples": 25,
            "S&P 500 Avg": 19
        },
    }
    
    # Sector ETFs
    SECTOR_ETFS = {
        "XLK": "Technology", "XLF": "Financials", "XLE": "Energy", "XLV": "Healthcare",
        "XLI": "Industrials", "XLY": "Consumer Discretionary", "XLP": "Consumer Staples",
        "XLB": "Materials", "XLRE": "Real Estate", "XLU": "Utilities",
    }
    
    # Evaluation questions
    EVAL_QUESTIONS = [
        {
            "id": "fb_001",
            "question": "What was total revenue?",
            "expected_keywords": ["revenue", "billion", "million", "$"],
            "category": "Income Statement"
        },
        {
            "id": "fb_002",
            "question": "What was diluted EPS?",
            "expected_keywords": ["eps", "diluted", "$", "per share"],
            "category": "Per Share"
        },
        {
            "id": "fb_003",
            "question": "What was the gross margin?",
            "expected_keywords": ["gross margin", "%", "percent"],
            "category": "Ratios"
        },
        {
            "id": "fb_004",
            "question": "What was free cash flow?",
            "expected_keywords": ["free cash flow", "operating", "capex"],
            "category": "Cash Flow"
        },
        {
            "id": "fb_005",
            "question": "What are the main risk factors?",
            "expected_keywords": ["risk", "competition", "regulatory"],
            "category": "Risk Factors"
        },
    ]
    
    @staticmethod
    def render_metrics_dashboard(metrics: List[FinancialMetric]):
        """Render metrics dashboard"""
        if not metrics:
            st.info("No financial metrics extracted.")
            return
        
        # Group by category
        by_category = {}
        for metric in metrics:
            by_category.setdefault(metric.category, []).append(metric)
        
        # Render each category
        categories = ["Income Statement", "Per Share", "Cash Flow", "Ratios", "Balance Sheet", "Other"]
        for category in categories:
            items = by_category.get(category, [])
            if not items:
                continue
            
            color = MetricsExtractor.CATEGORY_COLORS.get(category, "#9A8AAA")
            
            st.markdown(f"""
            <div style="font-family:Space Mono,monospace; font-size:0.56rem;
                        letter-spacing:0.2em; text-transform:uppercase;
                        color:{color}; margin:1rem 0 0.5rem;
                        border-bottom:1px solid rgba(139,58,139,.2);">
                {category}
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns(min(len(items), 4))
            for i, metric in enumerate(items):
                with cols[i % 4]:
                    st.markdown(
                        UIComponents.metric_card(metric),
                        unsafe_allow_html=True
                    )
    
    @staticmethod
    def render_comparison_tab(metrics: List[FinancialMetric], api_key: str, fetcher: MarketDataFetcher):
        """Render document vs market comparison tab"""
        if not metrics:
            st.info("Upload documents first to see comparisons.")
            return
        
        # Extract percentage metrics
        pct_metrics = {m.label: m.value for m in metrics if m.unit == "%"}
        
        # Sector comparison
        st.markdown("### Document Margins vs Sector Benchmarks")
        
        sectors = list(AnalyticsDashboard.SECTOR_BENCHMARKS.get("Gross Margin", {}).keys())
        selected_sector = st.selectbox("Compare against sector", sectors)
        
        # Build comparison table
        comparison_data = []
        for metric_name, doc_value in pct_metrics.items():
            benchmark_row = AnalyticsDashboard.SECTOR_BENCHMARKS.get(metric_name, {})
            benchmark_value = benchmark_row.get(selected_sector)
            
            if benchmark_value is not None:
                delta = doc_value - benchmark_value
                comparison_data.append({
                    "Metric": metric_name,
                    "Document": f"{doc_value:.1f}%",
                    f"{selected_sector}": f"{benchmark_value:.1f}%",
                    "Delta": f"{delta:+.1f}%",
                    "_delta_value": delta
                })
        
        if comparison_data:
            df = pd.DataFrame(comparison_data).drop(columns=["_delta_value"])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No comparable metrics found")
        
        # Live market context
        st.markdown("### Live Market Context")
        
        # Fetch live indices
        indices = fetcher.fetch_multi_queries(("^GSPC", "^IXIC", "^NSEI", "^N225"))
        
        cols = st.columns(4)
        for i, (symbol, name) in enumerate([("^GSPC", "S&P 500"), ("^IXIC", "NASDAQ"),
                                            ("^NSEI", "NIFTY"), ("^N225", "Nikkei")]):
            if symbol in indices:
                data = indices[symbol]
                with cols[i]:
                    st.metric(
                        label=name,
                        value=f"{data['price']:,.0f}",
                        delta=f"{data['pct']:+.2f}%"
                    )
    
    @staticmethod
    def render_eval_dashboard(results: List[Dict]):
        """Render evaluation benchmark results"""
        if not results:
            return
        
        # Calculate average score
        avg_score = sum(r["score"]["score_pct"] for r in results) / len(results)
        
        # Display score
        color = "#4ade80" if avg_score >= 70 else "#f0c040" if avg_score >= 40 else "#f87171"
        
        st.markdown(f"""
        <div style="background:#120E1A; border:1px solid rgba(139,58,139,.22);
                    border-radius:10px; padding:1rem 1.2rem; margin-bottom:1rem;">
            <div style="font-family:Space Mono,monospace; font-size:0.54rem;
                        letter-spacing:0.15em; text-transform:uppercase; color:#4A3858;">
                Overall Recall Score
            </div>
            <div style="font-family:Cormorant Garamond,serif; font-size:2.2rem;
                        font-weight:300; color:{color};">
                {avg_score:.1f}%
            </div>
            <div style="font-family:Space Mono,monospace; font-size:0.5rem; color:#4A3858;">
                {len(results)} questions evaluated
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show results table
        df = pd.DataFrame([
            {
                "Question": r["question"][:60] + "...",
                "Category": r.get("category", "-"),
                "Score": f'{r["score"]["score_pct"]}%',
                "Hits": f'{r["score"]["hits"]}/{r["score"]["total"]}'
            }
            for r in results
        ])
        
        st.dataframe(df, use_container_width=True, hide_index=True)

# ============================================================================
# SECTION 11: CHAT & RAG INTEGRATION
# ============================================================================

class ChatEngine:
    """Handle chat interactions with RAG and live data"""
    
    def __init__(self, api_key: str, fetcher: MarketDataFetcher):
        self.api_key = api_key
        self.fetcher = fetcher
        self._init_openai()
    
    def _init_openai(self):
        """Initialize OpenAI client"""
        from openai import OpenAI
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.groq.com/openai/v1"
        )
    
    def build_live_context(self, selected_symbols: List[str]) -> str:
        """Build live market context string"""
        context_parts = []
        
        # Stock quotes
        if selected_symbols:
            quotes = self.fetcher.fetch_multi_quotes(tuple(selected_symbols))
            stock_lines = []
            for sym in selected_symbols:
                if sym in quotes:
                    q = quotes[sym]
                    arrow = "▲" if q["pct"] >= 0 else "▼"
                    stock_lines.append(
                        f"  {sym}: ${q['price']:,.2f} ({arrow}{abs(q['pct']):.2f}%)"
                    )
            if stock_lines:
                context_parts.append("STOCKS:\n" + "\n".join(stock_lines))
        
        # Commodities
        comm_lines = []
        for sym, (name, unit, _, dec) in MarketDataFetcher.COMMODITIES.items():
            quote = self.fetcher.fetch_quote(sym)
            if quote:
                comm_lines.append(
                    f"  {name}: ${quote['price']:,.{dec}f} ({quote['pct']:+.2f}%)"
                )
        if comm_lines:
            context_parts.append("COMMODITIES:\n" + "\n".join(comm_lines[:5]))
        
        # Crypto
        crypto_lines = []
        for sym, (name, ticker, _, dec) in MarketDataFetcher.CRYPTO.items():
            quote = self.fetcher.fetch_quote(sym)
            if quote:
                crypto_lines.append(
                    f"  {ticker}: ${quote['price']:,.{dec}f} ({quote['pct']:+.2f}%)"
                )
        if crypto_lines:
            context_parts.append("CRYPTO:\n" + "\n".join(crypto_lines[:5]))
        
        # Fear & Greed
        fng = self.fetcher.fetch_fear_greed()
        context_parts.append(f"MARKET MOOD: Fear & Greed = {fng['value']} ({fng['label']})")
        
        return "\n\n".join(context_parts)
    
    def process_question(self, question: str, messages: List[Dict],
                        vectorstore: Optional[Any] = None) -> Tuple[str, List[Dict]]:
        """Process user question and return answer with sources"""
        
        # Build context
        live_context = self.build_live_context(st.session_state.get("fx_select_syms", []))
        
        # Retrieve document context
        doc_context = ""
        sources = []
        
        if vectorstore:
            # Search for relevant chunks
            results = vectorstore.search(question, n_results=5)
            
            if results["documents"]:
                chunks = results["documents"][0]
                metadatas = results["metadatas"][0]
                distances = results["distances"][0]
                
                doc_parts = []
                for chunk, meta, dist in zip(chunks, metadatas, distances):
                    doc_parts.append(f"[{meta['filename']}]\n{chunk}")
                    sources.append({
                        "filename": meta["filename"],
                        "score": round(1 - dist/2, 3),
                        "preview": chunk[:220]
                    })
                
                doc_context = "\n---\n".join(doc_parts)
        
        # Build full context
        full_context = live_context
        if doc_context:
            full_context += f"\n\n=== DOCUMENT CONTEXT ===\n{doc_context}"
        
        # Prepare messages
        system_message = {
            "role": "system",
            "content": (
                "You are an expert financial analyst with real-time data access. "
                "You have live prices for stocks, gold, silver, oil, crypto, and FX rates. "
                "Use live data for market questions. For document questions, cite specific numbers. "
                "Be concise, precise, never fabricate numbers."
            )
        }
        
        # Add conversation history (last 6 messages for context)
        history = [
            {"role": m["role"], "content": m["content"]}
            for m in messages[-6:] if m["role"] != "system"
        ]
        
        # Add current question with context
        user_message = {
            "role": "user",
            "content": f"{full_context}\n\nQuestion: {question}"
        }
        
        # Get response
        response = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[system_message] + history + [user_message],
            temperature=0.15,
            max_tokens=1500,
        )
        
        answer = response.choices[0].message.content
        tokens = response.usage.total_tokens
        
        return answer, sources, tokens

# ============================================================================
# SECTION 12: MAIN APPLICATION
# ============================================================================

def main():
    """Main application entry point"""
    
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize components
    fetcher = MarketDataFetcher()
    
    # ------------------------------------------------------------------------
    # SIDEBAR
    # ------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("""
        <div style="padding:0 0 1rem;">
            <div style="font-family:'Cormorant Garamond',serif; font-size:1.4rem;
                        font-weight:300; color:#EDE8F5;">
                RAG <em style="color:#C084C8;">Assistant</em>
            </div>
            <div style="font-family:'Space Mono',monospace; font-size:0.52rem;
                        letter-spacing:0.22em; color:#4A3858; text-transform:uppercase;">
                Financial Intelligence · v5
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # API Key input
        st.markdown("### Configuration")
        default_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY", ""))
        
        if default_key:
            GROQ_API_KEY = default_key
            st.success("✓ API Key Active")
        else:
            GROQ_API_KEY = st.text_input(
                "Groq API Key",
                type="password",
                placeholder="gsk_...",
                help="Get your free key at console.groq.com"
            )
        
        # Rate limit indicator
        if GROQ_API_KEY:
            bucket = fetcher.rate_limiter
            token_pct = bucket.tokens / bucket.capacity
            color = "#4ade80" if token_pct > 0.5 else "#f0c040" if token_pct > 0.2 else "#f87171"
            
            st.markdown(f"""
            <div style="margin:0.6rem 0;">
                <div style="font-family:Space Mono,monospace; font-size:0.52rem;
                            color:#4A3858; margin-bottom:0.3rem;">
                    API Rate Limit
                </div>
                <div style="background:#0D0B12; border:1px solid rgba(139,58,139,.22);
                            border-radius:4px; height:5px; overflow:hidden;">
                    <div style="height:100%; width:{int(token_pct*100)}%;
                                background:{color}; border-radius:4px;"></div>
                </div>
                <div style="font-family:Space Mono,monospace; font-size:0.5rem;
                            color:#4A3858; margin-top:0.2rem;">
                    {int(bucket.tokens)}/{bucket.capacity} calls · 60s reset
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Document list
        if st.session_state.file_names:
            st.markdown("### Knowledge Base")
            col1, col2 = st.columns(2)
            col1.metric("Chunks", st.session_state.chunk_count)
            col2.metric("Docs", st.session_state.uploaded_docs)
            
            for filename in st.session_state.file_names:
                short_name = filename[:22] + "…" if len(filename) > 22 else filename
                st.markdown(f"📄 {short_name}")
        
        # Quick questions
        st.markdown("### Quick Ask")
        quick_questions = [
            "What is USD/INR today?",
            "Gold price today?",
            "Bitcoin vs Ethereum?",
            "What was total revenue?",
            "Main risk factors?"
        ]
        
        for q in quick_questions:
            if st.button(q, use_container_width=True, key=f"quick_{q[:10]}"):
                st.session_state["_prefill"] = q
        
        # Actions
        st.markdown("### Actions")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✕ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()
        with col2:
            if st.button("🗑 Clear Docs", use_container_width=True):
                for key in ["vectorstore", "file_names", "uploaded_docs",
                           "chunk_count", "doc_full_text", "auto_metrics"]:
                    if key in st.session_state:
                        if key == "vectorstore":
                            st.session_state[key] = None
                        elif key in ["file_names", "auto_metrics"]:
                            st.session_state[key] = []
                        elif key in ["uploaded_docs", "chunk_count"]:
                            st.session_state[key] = 0
                        else:
                            st.session_state[key] = ""
                st.rerun()
    
    # ------------------------------------------------------------------------
    # MAIN TABS
    # ------------------------------------------------------------------------
    tab1, tab2 = st.tabs(["📈 Markets & Chat", "📊 Analytics Dashboard"])
    
    with tab1:
        render_markets_chat_tab(fetcher, GROQ_API_KEY)
    
    with tab2:
        render_analytics_tab(fetcher, GROQ_API_KEY)

def render_markets_chat_tab(fetcher: MarketDataFetcher, api_key: str):
    """Render Markets & Chat tab"""
    
    # Global search bar
    st.markdown('<div class="gsearch-wrap">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([15, 1])
    with col1:
        search_query = st.text_input(
            "global_search",
            value=st.session_state.search_query,
            placeholder="🔍 Search across your documents...",
            label_visibility="collapsed",
            key="global_search"
        )
    with col2:
        if st.button("✕", key="clear_search"):
            st.session_state.search_query = ""
            st.session_state.search_results = []
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Execute search
    if search_query and search_query != st.session_state.search_query:
        st.session_state.search_query = search_query
        if st.session_state.vectorstore:
            results = st.session_state.vectorstore.search(search_query, n_results=5)
            hits = []
            if results["documents"]:
                for chunk, meta, dist in zip(results["documents"][0],
                                            results["metadatas"][0],
                                            results["distances"][0]):
                    hits.append({
                        "filename": meta["filename"],
                        "score": round(1 - dist/2, 3),
                        "snippet": chunk[:300]
                    })
            st.session_state.search_results = hits
    
    # Display search results
    if st.session_state.search_results:
        st.markdown(f"### {len(st.session_state.search_results)} results")
        for hit in st.session_state.search_results:
            st.markdown(f"""
            <div class="sr-hit">
                <div style="font-size:0.8rem; color:#C084C8;">
                    📄 {hit['filename']} ({hit['score']*100:.0f}% match)
                </div>
                <div style="font-size:0.9rem; color:#9A8AAA; margin-top:0.3rem;">
                    {hit['snippet']}…
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Hero header
    st.markdown("""
    <div class="rag-header">
        <div class="rag-kicker">Financial Intelligence Platform</div>
        <h1>Interrogate Your<br><em>Financial Documents</em></h1>
        <p>Semantic search and AI-powered analysis across Annual Reports,
           10-Ks &amp; Earnings Transcripts. Live markets always on.</p>
        <div class="badge-row">
            <span class="badge v">Semantic Retrieval</span>
            <span class="badge v">Source-backed Answers</span>
            <span class="badge v">Llama 3.3 · 70B</span>
            <span class="badge b">PDF · Excel · CSV · DOCX</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Auto-analytics banner
    if st.session_state.auto_generated:
        n_metrics = len(st.session_state.auto_metrics)
        st.markdown(f"""
        <div class="analytics-banner">
            <div style="font-size:1.4rem;">✅</div>
            <div>
                <div style="font-size:0.84rem; color:#86efac;">
                    Analytics auto-generated — {n_metrics} metrics extracted
                </div>
                <div style="font-size:0.52rem; color:#4A3858;">
                    Switch to Analytics Dashboard to view
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats strip
    chunks = st.session_state.chunk_count
    docs = st.session_state.uploaded_docs
    messages = len(st.session_state.messages) // 2
    
    st.markdown(f"""
    <div class="stat-strip">
        <div class="stat-cell">
            <div class="stat-lbl">Model</div>
            <div class="stat-val" style="font-size:0.9rem;">Llama 3.3</div>
        </div>
        <div class="stat-cell">
            <div class="stat-lbl">Chunks</div>
            <div class="stat-val">{chunks if chunks else '—'}</div>
        </div>
        <div class="stat-cell">
            <div class="stat-lbl">Documents</div>
            <div class="stat-val">{docs if docs else '—'}</div>
        </div>
        <div class="stat-cell">
            <div class="stat-lbl">Messages</div>
            <div class="stat-val">{messages if messages else '—'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Market mood
    fng = fetcher.fetch_fear_greed()
    color = "#f87171" if fng["value"] < 25 else "#fb923c" if fng["value"] < 45 else "#facc15" if fng["value"] < 55 else "#86efac" if fng["value"] < 75 else "#4ade80"
    
    st.markdown(f"""
    <div style="background:#0D0B12; border:1px solid rgba(139,58,139,.22);
                border-radius:12px; padding:1rem; margin-bottom:1.4rem;">
        <div style="display:flex; align-items:center; gap:1rem;">
            <div>
                <div style="font-size:2rem; color:{color};">{fng['value']}</div>
                <div style="font-size:0.6rem; color:#4A3858;">{fng['label']}</div>
            </div>
            <div style="flex:1;">
                <div style="height:6px; background:linear-gradient(90deg,#f87171,#fb923c,#facc15,#86efac,#4ade80);
                            border-radius:3px; position:relative;">
                    <div style="position:absolute; left:{fng['value']}%; top:-5px;
                                width:16px; height:16px; border-radius:50%;
                                background:white; border:2px solid {color};
                                transform:translateX(-50%);"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:0.5rem; color:#4A3858; margin-top:0.3rem;">
                    <span>Fear</span>
                    <span>Greed</span>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # News carousels
    col1, col2 = st.columns(2)
    with col1:
        news = NewsFetcher.fetch_carousel_news()
        if news:
            components.html(
                NewsFetcher.build_carousel_html(news, is_policy=False, height_px=400),
                height=400
            )
    with col2:
        policy = NewsFetcher.fetch_policy_news()
        if policy:
            components.html(
                NewsFetcher.build_carousel_html(policy, is_policy=True, height_px=400),
                height=400
            )
    
    # Live stock chart
    st.markdown("### Live Stock Chart")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        symbols = st.multiselect(
            "Symbols",
            options=["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "TSLA", "META"],
            default=["AAPL", "MSFT", "NVDA"],
            label_visibility="collapsed"
        )
    with col2:
        period = st.selectbox("Range", ["1D", "5D", "1M", "3M", "6M", "1Y"], index=2)
    
    period_map = {"1D": "1d", "5D": "5d", "1M": "1mo", "3M": "3mo", "6M": "6mo", "1Y": "1y"}
    interval_map = {"1D": "5m", "5D": "30m", "1M": "1d", "3M": "1d", "6M": "1d", "1Y": "1wk"}
    
    if symbols:
        # Current prices
        quotes = fetcher.fetch_multi_quotes(tuple(symbols))
        price_chips = []
        for sym in symbols:
            if sym in quotes:
                q = quotes[sym]
                price_chips.append(
                    UIComponents.price_chip(sym, sym, q["price"], q["pct"])
                )
        
        if price_chips:
            st.markdown(
                '<div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:1rem;">' +
                "".join(price_chips) +
                '</div>',
                unsafe_allow_html=True
            )
        
        # Historical chart
        chart_data = pd.DataFrame()
        for sym in symbols:
            series = fetcher.fetch_historical(sym, period_map[period], interval_map[period])
            if series is not None:
                chart_data[sym] = series
        
        if not chart_data.empty:
            # Normalize to percentage change
            normalized = (chart_data / chart_data.iloc[0] - 1) * 100
            st.line_chart(normalized, height=300)
            st.caption(f"Percentage change from {period} start")
    
    # Upload drawer
    if st.session_state.show_upload:
        with st.container():
            st.markdown("### Upload Documents")
            st.caption("Supported: PDF · XLSX · XLS · CSV · DOCX · TXT")
            
            files = st.file_uploader(
                "Upload",
                type=["pdf", "txt", "xlsx", "xls", "csv", "docx"],
                accept_multiple_files=True,
                label_visibility="collapsed",
                key="uploader"
            )
            
            col1, col2 = st.columns([3, 1])
            with col1:
                if files and st.button("📥 Ingest Documents", use_container_width=True):
                    if not api_key:
                        st.error("Please enter your Groq API key in the sidebar")
                    else:
                        with st.spinner("Processing documents..."):
                            success = process_uploaded_files(files)
                            if success:
                                st.session_state.show_upload = False
                                st.rerun()
            with col2:
                if st.button("✕ Close", use_container_width=True):
                    st.session_state.show_upload = False
                    st.rerun()
    
    # Chat interface
    upload_button = st.button("＋ Upload", key="upload_btn", help="Upload documents")
    if upload_button:
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()
    
    # Display chat messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"Sources ({len(msg['sources'])})"):
                    for src in msg["sources"]:
                        st.markdown(
                            UIComponents.source_card(
                                src["filename"],
                                src["score"],
                                src["preview"]
                            ),
                            unsafe_allow_html=True
                        )
    
    # Chat input
    prefill = st.session_state.pop("_prefill", None)
    question = st.chat_input("Ask about stocks, gold, crypto, currencies, or your documents...")
    
    if prefill or question:
        q = prefill or question
        
        if not api_key:
            st.error("Please enter your Groq API key in the sidebar")
            st.stop()
        
        # Add user message
        with st.chat_message("user"):
            st.markdown(q)
        st.session_state.messages.append({"role": "user", "content": q})
        
        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    chat_engine = ChatEngine(api_key, fetcher)
                    answer, sources, tokens = chat_engine.process_question(
                        q,
                        st.session_state.messages,
                        st.session_state.vectorstore
                    )
                    
                    st.markdown(answer)
                    if sources:
                        with st.expander(f"Sources ({len(sources)})"):
                            for src in sources:
                                st.markdown(
                                    UIComponents.source_card(
                                        src["filename"],
                                        src["score"],
                                        src["preview"]
                                    ),
                                    unsafe_allow_html=True
                                )
                    
                    st.caption(f"llama-3.3-70b-versatile · {tokens} tokens")
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    
                except Exception as e:
                    st.error(f"Error: {str(e)}")

def render_analytics_tab(fetcher: MarketDataFetcher, api_key: str):
    """Render Analytics Dashboard tab"""
    
    if not st.session_state.vectorstore and not st.session_state.doc_full_text:
        st.info("Upload documents to unlock analytics")
        return
    
    # Get metrics
    metrics = st.session_state.auto_metrics
    if not metrics and st.session_state.doc_full_text:
        with st.spinner("Extracting metrics..."):
            metrics = MetricsExtractor.extract_metrics(st.session_state.doc_full_text)
            st.session_state.auto_metrics = metrics
    
    # Create sub-tabs
    subtabs = st.tabs([
        "📊 Metrics Dashboard",
        "📈 Doc vs Market",
        "📋 Templates",
        "🔍 Search",
        "🧪 Evaluation"
    ])
    
    with subtabs[0]:
        AnalyticsDashboard.render_metrics_dashboard(metrics)
    
    with subtabs[1]:
        AnalyticsDashboard.render_comparison_tab(metrics, api_key, fetcher)
    
    with subtabs[2]:
        render_templates_tab()
    
    with subtabs[3]:
        render_search_tab()
    
    with subtabs[4]:
        render_evaluation_tab(api_key)

def render_templates_tab():
    """Render analysis templates tab"""
    
    templates = {
        "Revenue Summary": {
            "icon": "💰",
            "category": "Income Statement",
            "prompt": "Extract and summarise revenue figures: total revenue, segment breakdown, YoY growth, guidance."
        },
        "Profitability Deep-Dive": {
            "icon": "📊",
            "category": "Income Statement",
            "prompt": "Analyse profitability: gross profit & margin, operating income & margin, EBITDA, net income."
        },
        "EPS Analysis": {
            "icon": "📈",
            "category": "Per Share",
            "prompt": "What is basic and diluted EPS? Change YoY? What drove it?"
        },
        "Balance Sheet Snapshot": {
            "icon": "🏦",
            "category": "Balance Sheet",
            "prompt": "Total assets, liabilities, shareholders equity, cash, debt."
        },
        "Cash Flow Analysis": {
            "icon": "🌊",
            "category": "Cash Flow",
            "prompt": "Operating cash flow, CapEx, FCF, FCF conversion rate."
        },
        "Risk Factors": {
            "icon": "⚠️",
            "category": "Risk Factors",
            "prompt": "Top 5 material risk factors: name, description, financial impact."
        }
    }
    
    # Category filter
    categories = sorted({t["category"] for t in templates.values()})
    selected_category = st.selectbox("Filter by category", ["All"] + categories)
    
    # Display templates
    filtered = {
        k: v for k, v in templates.items()
        if selected_category == "All" or v["category"] == selected_category
    }
    
    cols = st.columns(3)
    for i, (name, template) in enumerate(filtered.items()):
        with cols[i % 3]:
            color = MetricsExtractor.CATEGORY_COLORS.get(template["category"], "#9A8AAA")
            
            st.markdown(f"""
            <div style="background:#120E1A; border:1px solid rgba(139,58,139,.22);
                        border-top:2px solid {color}; border-radius:10px;
                        padding:0.8rem; margin-bottom:1rem;">
                <div style="font-size:1.2rem;">{template['icon']}</div>
                <div style="font-size:0.9rem; font-weight:600; margin:0.3rem 0;">
                    {name}
                </div>
                <div style="font-size:0.7rem; color:{color}; text-transform:uppercase;">
                    {template['category']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Use Template", key=f"template_{name}", use_container_width=True):
                st.session_state["_prefill"] = template["prompt"]
                st.switch_page(tab1)

def render_search_tab():
    """Render hybrid search tab"""
    
    if not st.session_state.vectorstore:
        st.info("Upload documents first")
        return
    
    st.markdown("### Hybrid Search")
    st.caption("BM25 + Dense Retrieval with Cross-Encoder Re-ranking")
    
    query = st.text_input("Search query", placeholder="e.g., free cash flow 2023")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        bm25_weight = st.slider("BM25 weight", 0.0, 1.0, 0.35, 0.05)
    with col2:
        n_results = st.slider("Results", 3, 15, 8)
    with col3:
        use_rerank = st.checkbox("Cross-encoder re-rank", value=True)
    
    if query:
        with st.spinner("Searching..."):
            # Get all chunks
            collection = st.session_state.vectorstore.collection
            all_data = collection.get(include=["documents", "embeddings", "metadatas"])
            
            chunks = all_data["documents"]
            embeddings = all_data["embeddings"]
            metadatas = all_data["metadatas"]
            
            # Simple hybrid scoring
            query_embedding = st.session_state.vectorstore.embedding_model.encode(
                [query],
                normalize_embeddings=True
            )[0]
            
            # Calculate scores
            scores = []
            for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                # Dense score (cosine similarity)
                import numpy as np
                dense_score = np.dot(query_embedding, emb) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(emb) + 1e-9
                )
                
                # BM25-like score (simplified - term overlap)
                query_terms = set(query.lower().split())
                chunk_terms = set(chunk.lower().split())
                overlap = len(query_terms & chunk_terms)
                bm25_score = overlap / (len(query_terms) + len(chunk_terms) + 1e-9)
                
                # Hybrid score
                hybrid_score = (1 - bm25_weight) * dense_score + bm25_weight * bm25_score
                
                scores.append({
                    "idx": i,
                    "chunk": chunk,
                    "metadata": metadatas[i],
                    "dense": dense_score,
                    "bm25": bm25_score,
                    "hybrid": hybrid_score
                })
            
            # Sort by hybrid score
            scores.sort(key=lambda x: x["hybrid"], reverse=True)
            
            # Display results
            for i, hit in enumerate(scores[:n_results], 1):
                tags = MetricsExtractor.tag_chunk(hit["chunk"])
                
                st.markdown(f"""
                <div style="background:#0D0B12; border:1px solid rgba(139,58,139,.22);
                            border-left:3px solid #C084C8; border-radius:0 8px 8px 0;
                            padding:0.7rem; margin-bottom:0.5rem;">
                    <div style="display:flex; justify-content:space-between;">
                        <div style="font-size:0.7rem; color:#C084C8;">
                            #{i} · 📄 {hit['metadata']['filename']}
                        </div>
                        <div style="font-size:0.6rem; color:#4A3858;">
                            score: {hit['hybrid']:.3f}
                        </div>
                    </div>
                    <div style="font-size:0.8rem; color:#9A8AAA; margin-top:0.3rem;">
                        {hit['chunk'][:300]}...
                    </div>
                    <div style="margin-top:0.3rem; display:flex; gap:0.2rem;">
                        {''.join(f'<span style="background:rgba(139,58,139,.15); font-size:0.5rem; padding:0.1rem 0.3rem; border-radius:3px;">{t}</span>' for t in tags[:3])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_evaluation_tab(api_key: str):
    """Render evaluation benchmark tab"""
    
    if not st.session_state.vectorstore or not api_key:
        st.info("Need documents and API key for evaluation")
        return
    
    if st.button("▶ Run Benchmark"):
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        
        results = []
        progress_bar = st.progress(0, text="Evaluating...")
        
        for i, q in enumerate(AnalyticsDashboard.EVAL_QUESTIONS):
            # Search for context
            search_results = st.session_state.vectorstore.search(q["question"], n_results=4)
            context = "\n---\n".join(search_results["documents"][0])
            
            # Get answer
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "Answer concisely using only the provided context."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q['question']}"}
                ],
                temperature=0.05,
                max_tokens=400
            )
            
            answer = response.choices[0].message.content
            
            # Score answer
            answer_lower = answer.lower()
            hits = sum(1 for kw in q["expected_keywords"] if kw in answer_lower)
            score = {
                "recall": hits / len(q["expected_keywords"]),
                "hits": hits,
                "total": len(q["expected_keywords"]),
                "score_pct": round(hits / len(q["expected_keywords"]) * 100, 1)
            }
            
            results.append({
                "question": q["question"],
                "category": q["category"],
                "answer": answer,
                "score": score
            })
            
            progress_bar.progress((i + 1) / len(AnalyticsDashboard.EVAL_QUESTIONS))
        
        progress_bar.empty()
        AnalyticsDashboard.render_eval_dashboard(results)

def process_uploaded_files(files: List) -> bool:
    """Process uploaded files and update vector store"""
    try:
        processor = DocumentProcessor()
        
        all_chunks = []
        all_metadatas = []
        all_texts = []
        documents = []
        
        for file in files:
            # Extract text
            text = processor.extract_text_from_file(file)
            all_texts.append(text)
            
            # Chunk text
            chunks = processor.chunk_text(
                text,
                chunk_size=Config.CHUNK_SIZE,
                overlap=Config.CHUNK_OVERLAP
            )
            
            # Create document
            doc = Document(file.name, text)
            documents.append(doc)
            
            # Prepare chunks and metadata
            for j, chunk in enumerate(chunks):
                all_chunks.append(chunk)
                all_metadatas.append({
                    "filename": file.name,
                    "chunk_index": j,
                    "total_chunks": len(chunks)
                })
        
        # Initialize or get RAG engine
        if not st.session_state.vectorstore:
            st.session_state.vectorstore = RAGEngine()
        
        # Add to vector store
        st.session_state.vectorstore.add_documents(documents, all_chunks, all_metadatas)
        
        # Update session state
        st.session_state.uploaded_docs = len(files)
        st.session_state.chunk_count = len(all_chunks)
        st.session_state.file_names = [f.name for f in files]
        st.session_state.doc_full_text = " ".join(all_texts)
        
        # Extract metrics
        st.session_state.auto_metrics = MetricsExtractor.extract_metrics(
            st.session_state.doc_full_text
        )
        st.session_state.auto_generated = True
        
        return True
        
    except Exception as e:
        st.error(f"Error processing files: {str(e)}")
        return False

# ============================================================================
# SECTION 13: ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    main()
