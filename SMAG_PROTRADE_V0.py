import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
from datetime import timedelta, datetime
import io, json, re

try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="ProTrader Intelligence", page_icon="📈",
                   layout="wide", initial_sidebar_state="expanded")

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=IBM+Plex+Mono:wght@400;600&display=swap');
html,body,[class*="css"]{font-family:'IBM Plex Mono',monospace;background:#080c18;}
.stApp{background:#080c18;}
p,span,div,label,li,td,th,.stMarkdown,[data-testid="stMarkdownContainer"],
[data-testid="stText"],.element-container{color:#dce8f5 !important;}
section[data-testid="stSidebar"]{background:#0b1120 !important;border-right:1px solid #1a2840;}
section[data-testid="stSidebar"] *{color:#c4d4ea !important;}
[data-testid="stWidgetLabel"]>p{color:#7fa8d0 !important;font-size:0.77rem !important;}
button[data-baseweb="tab"]{color:#6a90b8 !important;font-size:0.82rem;}
button[data-baseweb="tab"][aria-selected="true"]{color:#38bdf8 !important;border-bottom:2px solid #38bdf8;}
[data-testid="stDataFrame"] *{color:#dce8f5 !important;}
textarea{background:#0f1929 !important;color:#dce8f5 !important;border:1px solid #1e3050 !important;font-family:'IBM Plex Mono',monospace !important;}
.stTextArea textarea{background:#0f1929 !important;color:#e0eeff !important;}
.main-header{font-family:'Syne',sans-serif;font-size:2.3rem;font-weight:800;letter-spacing:-1px;
  background:linear-gradient(130deg,#38bdf8 0%,#818cf8 55%,#fb923c 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:0;}
.sub-header{font-size:0.68rem;letter-spacing:3px;color:#2d4260 !important;text-transform:uppercase;margin-bottom:1.6rem;}
.metric-card{background:linear-gradient(145deg,#0f1929,#152030);border:1px solid #1a2d45;
  border-radius:12px;padding:0.9rem 1rem;text-align:center;position:relative;overflow:hidden;}
.metric-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;
  background:linear-gradient(90deg,#38bdf8,#818cf8);}
.metric-label{font-size:0.58rem;letter-spacing:2px;color:#3d5a7a !important;text-transform:uppercase;margin-bottom:0.25rem;}
.metric-value{font-family:'Syne',sans-serif;font-size:1.35rem;font-weight:700;color:#e8f4ff !important;}
.metric-delta{font-size:0.76rem;margin-top:0.1rem;font-weight:600;}
.clr-up{color:#34d399 !important;}.clr-dn{color:#f87171 !important;}.clr-neu{color:#8aa0c0 !important;}
.sec-title{font-family:'Syne',sans-serif;font-size:0.95rem;font-weight:700;letter-spacing:1px;
  color:#38bdf8 !important;border-bottom:1px solid #1a2d45;padding-bottom:0.4rem;margin:1.2rem 0 0.6rem;}
.verdict-banner{border-radius:10px;padding:0.85rem 1.3rem;display:flex;align-items:center;gap:1rem;margin:0.4rem 0;}
.v-buy{background:rgba(52,211,153,0.07);border:1px solid #34d399;}
.v-sell{background:rgba(248,113,113,0.07);border:1px solid #f87171;}
.v-neu{background:rgba(251,191,36,0.07);border:1px solid #fbbf24;}
.badge{display:inline-block;padding:0.16rem 0.65rem;border-radius:20px;font-size:0.65rem;font-weight:700;letter-spacing:1px;text-transform:uppercase;}
.b-buy{background:rgba(52,211,153,0.15);color:#34d399 !important;border:1px solid #34d399;}
.b-sell{background:rgba(248,113,113,0.15);color:#f87171 !important;border:1px solid #f87171;}
.b-neu{background:rgba(251,191,36,0.15);color:#fbbf24 !important;border:1px solid #fbbf24;}
.strat-card{border-radius:10px;padding:0.9rem 1.1rem;margin:0.35rem 0;border:1px solid;font-size:0.82rem;line-height:1.58;}
.sc-buy{background:rgba(52,211,153,0.07);border-color:#34d399;}
.sc-sell{background:rgba(248,113,113,0.07);border-color:#f87171;}
.sc-wait{background:rgba(251,191,36,0.07);border-color:#fbbf24;}
.st-name{font-family:'Syne',sans-serif;font-size:0.88rem;font-weight:700;margin-bottom:0.3rem;}
.sc-buy .st-name{color:#34d399 !important;}.sc-sell .st-name{color:#f87171 !important;}.sc-wait .st-name{color:#fbbf24 !important;}
.st-desc{color:#8aa0c0 !important;font-size:0.74rem;margin-bottom:0.3rem;}
.st-detail{color:#b8d0e8 !important;font-size:0.71rem;}
.sig-box{border-radius:8px;padding:0.65rem 1rem;margin:0.28rem 0;font-size:0.82rem;border-left:4px solid;line-height:1.55;}
.s-buy{background:rgba(52,211,153,0.09);border-color:#34d399;color:#a7f3d0 !important;}
.s-sell{background:rgba(248,113,113,0.09);border-color:#f87171;color:#fecaca !important;}
.s-neu{background:rgba(100,116,139,0.09);border-color:#475569;color:#94a3b8 !important;}
.ins-row{background:#0f1929;border-radius:8px;padding:0.65rem 1rem;margin:0.28rem 0;
  border:1px solid #1a2d45;font-size:0.8rem;line-height:1.65;color:#b8d0e8 !important;}
.ins-row b{color:#e8f4ff !important;}
.trigger-table{width:100%;border-collapse:collapse;font-size:0.78rem;}
.trigger-table th{background:#111e30;color:#38bdf8 !important;padding:0.5rem 0.8rem;
  text-align:left;border-bottom:1px solid #1a2d45;font-weight:600;letter-spacing:0.5px;}
.trigger-table td{padding:0.45rem 0.8rem;border-bottom:1px solid #111e30;color:#c4d4ea !important;}
.trigger-table tr:hover td{background:#0f1929;}
.trigger-buy td:first-child{border-left:3px solid #34d399;}
.trigger-sell td:first-child{border-left:3px solid #f87171;}
.custom-strat-box{background:#0c1828;border:1px solid #1a3050;border-radius:10px;
  padding:1.2rem;margin:0.5rem 0;}
.custom-strat-title{font-family:'Syne',sans-serif;font-size:0.9rem;font-weight:700;
  color:#38bdf8 !important;margin-bottom:0.6rem;}
hr{border-color:#1a2d45 !important;}
/* ── surge analysis ── */
.surge-card{border-radius:12px;padding:1.1rem 1.4rem;margin:0.5rem 0;border:1px solid;position:relative;overflow:hidden;}
.surge-card::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;}
.surge-bullish{background:rgba(52,211,153,0.06);border-color:#34d399;}
.surge-bullish::before{background:linear-gradient(90deg,#34d399,#38bdf8);}
.surge-bearish{background:rgba(248,113,113,0.06);border-color:#f87171;}
.surge-bearish::before{background:linear-gradient(90deg,#f87171,#f97316);}
.surge-caution{background:rgba(251,191,36,0.06);border-color:#fbbf24;}
.surge-caution::before{background:linear-gradient(90deg,#fbbf24,#fb923c);}
.surge-neutral{background:rgba(100,116,139,0.06);border-color:#475569;}
.surge-neutral::before{background:linear-gradient(90deg,#475569,#64748b);}
.surge-title{font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;margin-bottom:0.7rem;}
.surge-bullish .surge-title{color:#34d399 !important;}
.surge-bearish .surge-title{color:#f87171 !important;}
.surge-caution .surge-title{color:#fbbf24 !important;}
.surge-neutral .surge-title{color:#8aa0c0 !important;}
.surge-metric{display:inline-block;background:#0a1020;border:1px solid #1a2d45;border-radius:8px;
  padding:0.4rem 0.8rem;margin:0.2rem 0.2rem 0.2rem 0;font-size:0.75rem;}
.surge-metric b{color:#e8f4ff !important;}
.stButton>button{background:linear-gradient(135deg,#1a3a5c,#0f2640);color:#38bdf8 !important;
  border:1px solid #2a4a6c;border-radius:8px;font-size:0.8rem;padding:0.4rem 1.2rem;
  font-family:'IBM Plex Mono',monospace;transition:all 0.2s;}
.stButton>button:hover{background:linear-gradient(135deg,#1e4570,#132e52);border-color:#38bdf8;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def clean_num(s):
    return pd.to_numeric(s.astype(str).str.replace(",","").str.strip(), errors="coerce")

def parse_csv(file):
    try:
        text = file.read().decode("utf-8-sig")
        df = pd.read_csv(io.StringIO(text))
        df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)
        col_map = {
            "Symbol":"Symbol","Series":"Series","Date":"Date",
            "Prev Close":"Prev Close","Open Price":"Open","High Price":"High",
            "Low Price":"Low","Last Price":"Last","Close Price":"Close",
            "Average Price":"Avg Price","Total Traded Quantity":"Volume",
            "Turnover ₹":"Turnover","No. of Trades":"Trades",
            "Deliverable Qty":"Deliverable Qty","% Dly Qt to Traded Qty":"Delivery%",
        }
        df.rename(columns={k:v for k,v in col_map.items() if k in df.columns}, inplace=True)
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")
        for c in ["Open","High","Low","Close","Avg Price","Volume",
                  "Turnover","Trades","Deliverable Qty","Delivery%","Prev Close"]:
            if c in df.columns: df[c] = clean_num(df[c])
        df.dropna(subset=["Date","Close"], inplace=True)
        df.sort_values("Date", inplace=True)
        df.reset_index(drop=True, inplace=True)
        return df
    except Exception as e:
        st.error(f"Parse error: {e}"); return None

def resample_df(df, tf):
    if tf == "Daily": return df.copy()
    rule = "W-FRI" if tf == "Weekly" else "ME"
    agg = {"Open":"first","High":"max","Low":"min","Close":"last"}
    for c in ["Volume","Trades"]:
        if c in df.columns: agg[c] = "sum"
    if "Delivery%" in df.columns: agg["Delivery%"] = "mean"
    r = df.set_index("Date").resample(rule).agg({k:v for k,v in agg.items() if k in df.columns})
    r.dropna(subset=["Close"], inplace=True)
    r.reset_index(inplace=True)
    if "Symbol" in df.columns: r["Symbol"] = df["Symbol"].iloc[0]
    return r


# ─────────────────────────────────────────────────────────────────────────────
#  INDICATORS
# ─────────────────────────────────────────────────────────────────────────────
def add_indicators(df):
    c = df["Close"].copy()
    df["EMA_9"]  = c.ewm(span=9,  adjust=False).mean()
    df["EMA_12"] = c.ewm(span=12, adjust=False).mean()
    df["EMA_26"] = c.ewm(span=26, adjust=False).mean()
    df["SMA_14"]  = c.rolling(14).mean()
    df["SMA_20"]  = c.rolling(20).mean()
    df["SMA_50"]  = c.rolling(50).mean()
    df["SMA_100"] = c.rolling(100).mean()
    df["SMA_200"] = c.rolling(200).mean()
    df["MACD"]        = df["EMA_12"] - df["EMA_26"]
    df["MACD_Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["MACD_Hist"]   = df["MACD"] - df["MACD_Signal"]
    delta = c.diff()
    gain  = delta.clip(lower=0).rolling(14).mean()
    loss  = (-delta.clip(upper=0)).rolling(14).mean()
    df["RSI"] = 100 - (100/(1 + gain/loss.replace(0, np.nan)))
    mid = c.rolling(20).mean(); std = c.rolling(20).std()
    df["BB_Upper"] = mid+2*std; df["BB_Lower"] = mid-2*std; df["BB_Mid"] = mid
    df["BB_Width"] = (df["BB_Upper"]-df["BB_Lower"])/mid.replace(0, np.nan)
    if {"High","Low"}.issubset(df.columns):
        hl  = df["High"]-df["Low"]
        hpc = (df["High"]-c.shift()).abs()
        lpc = (df["Low"]-c.shift()).abs()
        tr  = pd.concat([hl,hpc,lpc],axis=1).max(axis=1)
        df["ATR"]  = tr.rolling(14).mean()
        df["ATR%"] = df["ATR"]/c*100
        lo14=df["Low"].rolling(14).min(); hi14=df["High"].rolling(14).max()
        df["Stoch_K"] = 100*(c-lo14)/(hi14-lo14+1e-9)
        df["Stoch_D"] = df["Stoch_K"].rolling(3).mean()
        df["Pivot"] = (df["High"]+df["Low"]+c)/3
        df["R1"]=2*df["Pivot"]-df["Low"]; df["S1"]=2*df["Pivot"]-df["High"]
        df["R2"]=df["Pivot"]+(df["High"]-df["Low"]); df["S2"]=df["Pivot"]-(df["High"]-df["Low"])
    if "Volume" in df.columns:
        df["Vol_SMA20"] = df["Volume"].rolling(20).mean()
        df["Vol_Ratio"] = df["Volume"]/df["Vol_SMA20"].replace(0, np.nan)
        df["OBV"] = (np.sign(c.diff())*df["Volume"]).fillna(0).cumsum()
    df["ROC_5"]  = c.pct_change(5)*100
    df["ROC_20"] = c.pct_change(20)*100
    return df


# ─────────────────────────────────────────────────────────────────────────────
#  YAHOO FINANCE DATA FETCHER
# ─────────────────────────────────────────────────────────────────────────────
def fetch_yahoo(ticker: str, start: str, end: str) -> pd.DataFrame | None:
    """
    Download OHLCV data from Yahoo Finance and normalise it to the app's column format.
    ticker : e.g. "TCS.NS", "RELIANCE.NS", "AAPL", "^NSEI"
    start  : "YYYY-MM-DD"
    end    : "YYYY-MM-DD"
    """
    if not YF_AVAILABLE:
        st.error("yfinance is not installed. Run: pip install yfinance")
        return None
    try:
        raw = yf.download(ticker, start=start, end=end,
                          auto_adjust=True, progress=False)
        if raw.empty:
            st.error(f"No data returned for '{ticker}'. Check the ticker symbol.")
            return None
        # Flatten MultiIndex columns if present
        if isinstance(raw.columns, pd.MultiIndex):
            raw.columns = raw.columns.get_level_values(0)
        raw = raw.reset_index()
        raw.rename(columns={
            "Date":"Date", "Open":"Open", "High":"High",
            "Low":"Low",  "Close":"Close","Volume":"Volume"
        }, inplace=True)
        raw["Date"] = pd.to_datetime(raw["Date"])
        for col in ["Open","High","Low","Close","Volume"]:
            if col in raw.columns:
                raw[col] = pd.to_numeric(raw[col], errors="coerce")
        raw.dropna(subset=["Date","Close"], inplace=True)
        raw.sort_values("Date", inplace=True)
        raw.reset_index(drop=True, inplace=True)
        # Add a Symbol column using the ticker
        raw["Symbol"] = ticker.upper()
        return raw
    except Exception as e:
        st.error(f"Yahoo Finance error for '{ticker}': {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  CMP vs ALL-DMA ANALYSIS
#  Rules:
#   BULL RUN  : CMP > SMA20 > SMA50 > SMA100 > SMA200 AND CMP < 1.10 × SMA200
#   BEAR RUN  : CMP < SMA20 < SMA50 < SMA100 < SMA200 AND CMP > 0.90 × SMA200
#   BULL TARGET: 1.07 × CMP
#   Intermediate states also classified
# ─────────────────────────────────────────────────────────────────────────────
def dma_cmp_analysis(df: pd.DataFrame):
    """
    Analyses CMP vs SMA20, SMA50, SMA100, SMA200.
    Returns rich dict with phase, signals, target, and historical phase series.
    """
    result = {
        "phase": "NEUTRAL",
        "phase_color": "#8aa0c0",
        "cmp": np.nan,
        "sma20": np.nan, "sma50": np.nan,
        "sma100": np.nan, "sma200": np.nan,
        "bull_target": np.nan,
        "bear_stop": np.nan,
        "above_count": 0,       # how many DMAs is CMP above
        "pct_vs_200": np.nan,   # CMP vs SMA200 %
        "pct_vs_100": np.nan,
        "pct_vs_50": np.nan,
        "pct_vs_20": np.nan,
        "insights": [],
        "phase_series": pd.Series(dtype=str),  # historical phase per bar
        "has_data": False,
    }

    last = df.iloc[-1]
    cmp    = last.get("Close",    np.nan)
    sma20  = last.get("SMA_20",   np.nan)
    sma50  = last.get("SMA_50",   np.nan)
    sma100 = last.get("SMA_100",  np.nan)
    sma200 = last.get("SMA_200",  np.nan)

    if any(np.isnan(x) for x in [cmp, sma20, sma50]):
        result["insights"].append("⚪ Insufficient data for DMA analysis.")
        return result

    result.update({"cmp": cmp, "sma20": sma20, "sma50": sma50,
                   "sma100": sma100, "sma200": sma200, "has_data": True})

    # How many DMAs is CMP above?
    dmas = [(sma20,"SMA20"), (sma50,"SMA50"), (sma100,"SMA100"), (sma200,"SMA200")]
    dmas_valid = [(v,n) for v,n in dmas if not np.isnan(v)]
    above = [(v,n) for v,n in dmas_valid if cmp > v]
    below = [(v,n) for v,n in dmas_valid if cmp < v]
    result["above_count"] = len(above)

    # % distance from each DMA
    if not np.isnan(sma200): result["pct_vs_200"] = (cmp/sma200 - 1)*100
    if not np.isnan(sma100): result["pct_vs_100"] = (cmp/sma100 - 1)*100
    if not np.isnan(sma50):  result["pct_vs_50"]  = (cmp/sma50  - 1)*100
    if not np.isnan(sma20):  result["pct_vs_20"]  = (cmp/sma20  - 1)*100

    # ── Phase classification ──────────────────────────────────────────────────
    all_dmas_valid = len(dmas_valid) == 4

    # BULL RUN: CMP > all DMAs in order AND CMP < 1.10×SMA200
    is_bull = (all_dmas_valid and
               cmp > sma20 > sma50 > sma100 > sma200 and
               cmp < 1.10 * sma200)

    # EXTENDED BULL: CMP > all DMAs but CMP >= 1.10×SMA200 (getting stretched)
    is_extended_bull = (all_dmas_valid and
                        cmp > sma20 > sma50 > sma100 > sma200 and
                        cmp >= 1.10 * sma200)

    # BEAR RUN: CMP < all DMAs in order AND CMP > 0.90×SMA200
    is_bear = (all_dmas_valid and
               cmp < sma20 < sma50 < sma100 < sma200 and
               cmp > 0.90 * sma200)

    # DEEP BEAR: CMP < 0.90×SMA200 (severely oversold)
    is_deep_bear = (not np.isnan(sma200) and cmp <= 0.90 * sma200)

    bull_target  = round(cmp * 1.07, 2)
    bear_target  = round(cmp * 0.93, 2)   # downside target
    result["bull_target"] = bull_target
    result["bear_stop"]   = bear_target

    if is_bull:
        result["phase"]       = "BULL RUN 🟢"
        result["phase_color"] = "#34d399"
        result["insights"] = [
            f"✅ <b>BULL RUN CONFIRMED:</b> CMP ₹{cmp:,.2f} is above ALL four DMAs (20/50/100/200) in perfect bullish alignment.",
            f"📐 CMP is {result['pct_vs_200']:+.2f}% above SMA200 — within the 10% extension zone (not yet overextended).",
            f"🎯 <b>Bull Run Target:</b> ₹{bull_target:,.2f} (CMP × 1.07) — based on standard 7% breakout target.",
            f"🛡 Suggested Stop-Loss: ₹{sma20:,.2f} (SMA20) — trail stop as price advances.",
            f"📊 DMA Alignment: CMP({cmp:,.0f}) > SMA20({sma20:,.0f}) > SMA50({sma50:,.0f}) > SMA100({sma100:,.0f}) > SMA200({sma200:,.0f}) ✓",
        ]
    elif is_extended_bull:
        result["phase"]       = "EXTENDED BULL ⚡"
        result["phase_color"] = "#fbbf24"
        result["insights"] = [
            f"⚡ <b>EXTENDED BULL:</b> CMP is above ALL DMAs in order — but {result['pct_vs_200']:+.2f}% above SMA200 (>10% extension).",
            f"⚠️ Price is stretched beyond the 1.10×SMA200 zone. Mean reversion risk elevated.",
            f"🎯 <b>Bull Target:</b> ₹{bull_target:,.2f} (CMP × 1.07) — but consider partial profits at this level.",
            f"🛡 Tighten stops to SMA20 ₹{sma20:,.2f}. A pullback to SMA50 (₹{sma50:,.0f}) would be healthy.",
            f"📊 DMA Alignment: CMP({cmp:,.0f}) > SMA20({sma20:,.0f}) > SMA50({sma50:,.0f}) > SMA100({sma100:,.0f}) > SMA200({sma200:,.0f}) — Extended",
        ]
    elif is_deep_bear:
        result["phase"]       = "DEEP BEAR 🔴"
        result["phase_color"] = "#ef4444"
        result["insights"] = [
            f"💥 <b>DEEP BEAR:</b> CMP is {abs(result['pct_vs_200']):.2f}% BELOW SMA200 — beyond the 0.90×SMA200 threshold.",
            f"⚠️ Severely oversold on a long-term basis. Potential for mean-reversion bounce but fundamental weakness likely.",
            f"🎯 Recovery target: SMA200 at ₹{sma200:,.2f} ({(sma200/cmp-1)*100:+.2f}% from current).",
            f"🛡 Downside target (0.93×CMP): ₹{bear_target:,.2f} if selling continues.",
            f"📊 CMP({cmp:,.0f}) is {abs(result['pct_vs_200']):.1f}% below SMA200({sma200:,.0f})",
        ]
    elif is_bear:
        result["phase"]       = "BEAR RUN 🔴"
        result["phase_color"] = "#f87171"
        result["insights"] = [
            f"🔴 <b>BEAR RUN CONFIRMED:</b> CMP ₹{cmp:,.2f} is below ALL four DMAs in perfect bearish alignment.",
            f"📐 CMP is {result['pct_vs_200']:+.2f}% below SMA200 — within the bear zone (above 0.90×SMA200 floor).",
            f"⚠️ Avoid fresh long positions. Wait for price to reclaim at least SMA20 (₹{sma20:,.2f}).",
            f"🎯 Downside target: ₹{bear_target:,.2f} (CMP × 0.93).",
            f"📊 DMA Alignment: CMP({cmp:,.0f}) < SMA20({sma20:,.0f}) < SMA50({sma50:,.0f}) < SMA100({sma100:,.0f}) < SMA200({sma200:,.0f}) ✓",
        ]
    else:
        # Mixed/transitional — give detail on what's happening
        above_names = [n for v,n in dmas_valid if cmp > v]
        below_names = [n for v,n in dmas_valid if cmp < v]
        if len(above) >= 3:
            result["phase"]       = "RECOVERING 🟡"
            result["phase_color"] = "#fbbf24"
            result["insights"] = [
                f"🟡 <b>RECOVERING:</b> CMP above {len(above)}/4 DMAs — building toward full bull alignment.",
                f"✅ Above: {', '.join(above_names)}. ⚠️ Still below: {', '.join(below_names)}.",
                f"📈 Next target: reclaim {below_names[0] if below_names else 'all DMAs'} to confirm trend shift.",
                f"🎯 If bull alignment completes, target ₹{bull_target:,.2f} (×1.07).",
            ]
        elif len(below) >= 3:
            result["phase"]       = "WEAKENING 🟠"
            result["phase_color"] = "#fb923c"
            result["insights"] = [
                f"🟠 <b>WEAKENING:</b> CMP below {len(below)}/4 DMAs — trending toward bear alignment.",
                f"⚠️ Below: {', '.join(below_names)}. Still above: {', '.join(above_names)}.",
                f"📉 Key support: SMA50 at ₹{sma50:,.2f}. A close below confirms breakdown.",
                f"🛡 Hold longs only if price reclaims SMA20 (₹{sma20:,.2f}) immediately.",
            ]
        else:
            result["phase"]       = "TRANSITION ↔"
            result["phase_color"] = "#8aa0c0"
            result["insights"] = [
                f"↔️ <b>TRANSITION / CONSOLIDATION:</b> CMP above {len(above)}/4 DMAs — mixed alignment.",
                f"✅ Above: {', '.join(above_names) if above_names else 'none'}. ⚠️ Below: {', '.join(below_names) if below_names else 'none'}.",
                f"🎯 Wait for DMA stack alignment (all MAs in order) before taking a directional position.",
            ]

    # ── Build historical phase series for chart background shading ────────────
    phases = []
    for i in range(len(df)):
        row  = df.iloc[i]
        c_   = row.get("Close",    np.nan)
        s20_ = row.get("SMA_20",   np.nan)
        s50_ = row.get("SMA_50",   np.nan)
        s100_= row.get("SMA_100",  np.nan)
        s200_= row.get("SMA_200",  np.nan)
        if any(np.isnan(x) for x in [c_, s20_, s50_, s100_, s200_]):
            phases.append("neutral")
            continue
        if c_ > s20_ > s50_ > s100_ > s200_ and c_ < 1.10*s200_:
            phases.append("bull")
        elif c_ > s20_ > s50_ > s100_ > s200_ and c_ >= 1.10*s200_:
            phases.append("extended")
        elif c_ < s20_ < s50_ < s100_ < s200_ and c_ > 0.90*s200_:
            phases.append("bear")
        elif c_ <= 0.90*s200_:
            phases.append("deep_bear")
        else:
            phases.append("neutral")
    result["phase_series"] = pd.Series(phases, index=df.index)
    return result


def build_dma_chart(df: pd.DataFrame, dma_result: dict, symbol: str, tf: str) -> go.Figure:
    """
    Dedicated CMP vs All-DMA chart with:
    - Candlestick + SMA20/50/100/200 lines
    - Colour-shaded background: green=bull, red=bear, amber=transition
    - Bull target line (1.07×CMP)
    - DMA distance % panel (row 2)
    - RSI confirmation (row 3)
    """
    has_ohlc = {"Open","High","Low","Close"}.issubset(df.columns)
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        row_heights=[0.55, 0.25, 0.20],
        subplot_titles=("CMP vs SMA 20 / 50 / 100 / 200", "% Distance from Each DMA", "RSI Confirmation"),
    )

    # ── Background phase shading ──────────────────────────────────────────────
    phase_s = dma_result["phase_series"]
    if len(phase_s) > 0:
        phase_colors = {
            "bull":     "rgba(52,211,153,0.07)",
            "extended": "rgba(251,191,36,0.07)",
            "bear":     "rgba(248,113,113,0.07)",
            "deep_bear":"rgba(239,68,68,0.12)",
            "neutral":  "rgba(0,0,0,0)",
        }
        # Compress into contiguous segments for efficiency
        prev_p = None; seg_start = None
        for i, (idx, ph) in enumerate(phase_s.items()):
            if ph != prev_p:
                if prev_p is not None and prev_p != "neutral" and seg_start is not None:
                    seg_end_date = df["Date"].iloc[max(0, i-1)]
                    fig.add_vrect(x0=df["Date"].iloc[seg_start], x1=seg_end_date,
                                  fillcolor=phase_colors.get(prev_p,"rgba(0,0,0,0)"),
                                  line_width=0, row=1, col=1)
                seg_start = i
                prev_p = ph
        # Close last segment
        if prev_p is not None and prev_p != "neutral":
            fig.add_vrect(x0=df["Date"].iloc[seg_start], x1=df["Date"].iloc[-1],
                          fillcolor=phase_colors.get(prev_p,"rgba(0,0,0,0)"),
                          line_width=0, row=1, col=1)

    # ── Candlestick or line ──────────────────────────────────────────────────
    if has_ohlc:
        fig.add_trace(go.Candlestick(
            x=df["Date"], open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="Price",
            increasing_line_color="#34d399", decreasing_line_color="#f87171",
            increasing_fillcolor="rgba(52,211,153,0.75)",
            decreasing_fillcolor="rgba(248,113,113,0.75)",
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"],
                                 line=dict(color="#38bdf8",width=1.8), name="CMP"), row=1, col=1)

    # ── DMA lines ────────────────────────────────────────────────────────────
    dma_styles = [
        ("SMA_20",  "#38bdf8",  "solid",    1.3, "SMA 20"),
        ("SMA_50",  "#fb923c",  "dash",     1.5, "SMA 50"),
        ("SMA_100", "#a78bfa",  "longdash", 1.5, "SMA 100"),
        ("SMA_200", "#f472b6",  "dot",      2.0, "SMA 200"),
    ]
    for col, clr, dash, wid, lbl in dma_styles:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df["Date"], y=df[col],
                                     line=dict(color=clr, width=wid, dash=dash),
                                     name=lbl), row=1, col=1)

    # ── Bull target line (horizontal) ────────────────────────────────────────
    cmp = dma_result["cmp"]
    bull_target = dma_result["bull_target"]
    if not np.isnan(bull_target) and dma_result["phase"] in ["BULL RUN 🟢","EXTENDED BULL ⚡","RECOVERING 🟡"]:
        fig.add_hline(y=bull_target, line_dash="dash", line_color="#34d399", line_width=1.5,
                      annotation_text=f"🎯 Bull Target ₹{bull_target:,.0f} (+7%)",
                      annotation_font_color="#34d399", annotation_position="right",
                      row=1, col=1)
    # Bear downside target
    bear_target = dma_result["bear_stop"]
    if not np.isnan(bear_target) and "BEAR" in dma_result["phase"]:
        fig.add_hline(y=bear_target, line_dash="dash", line_color="#f87171", line_width=1.5,
                      annotation_text=f"⬇ Bear Target ₹{bear_target:,.0f} (−7%)",
                      annotation_font_color="#f87171", annotation_position="right",
                      row=1, col=1)

    # ── CMP annotation ───────────────────────────────────────────────────────
    phase_clr = dma_result["phase_color"]
    fig.add_annotation(
        x=df["Date"].iloc[-1], y=cmp,
        text=f"<b>CMP ₹{cmp:,.2f}</b>",
        font=dict(size=11, color=phase_clr),
        bgcolor="rgba(10,16,30,0.88)", bordercolor=phase_clr, borderwidth=1,
        showarrow=True, arrowcolor=phase_clr, ax=50, ay=-20,
    )

    # ── Panel 2: % distance from each DMA ────────────────────────────────────
    dma_pct_cols = [("SMA_20","SMA20","#38bdf8"), ("SMA_50","SMA50","#fb923c"),
                    ("SMA_100","SMA100","#a78bfa"), ("SMA_200","SMA200","#f472b6")]
    for col, lbl, clr in dma_pct_cols:
        if col in df.columns:
            pct_series = (df["Close"] / df[col] - 1) * 100
            fig.add_trace(go.Scatter(x=df["Date"], y=pct_series,
                                     line=dict(color=clr, width=1.2),
                                     name=f"vs {lbl}%", showlegend=True), row=2, col=1)
    fig.add_hline(y=0,  line_dash="solid", line_color="rgba(148,163,184,0.3)", line_width=1, row=2, col=1)
    fig.add_hline(y=10, line_dash="dot",   line_color="rgba(251,191,36,0.4)",  line_width=1,
                  annotation_text="1.10×SMA200", annotation_font_color="#fbbf24",
                  annotation_position="right", row=2, col=1)
    fig.add_hline(y=-10,line_dash="dot",   line_color="rgba(248,113,113,0.4)", line_width=1,
                  annotation_text="0.90×SMA200", annotation_font_color="#f87171",
                  annotation_position="right", row=2, col=1)
    fig.add_hrect(y0=0, y1=10,  fillcolor="rgba(52,211,153,0.04)", line_width=0, row=2, col=1)
    fig.add_hrect(y0=-10,y1=0,  fillcolor="rgba(248,113,113,0.04)", line_width=0, row=2, col=1)

    # ── Panel 3: RSI ─────────────────────────────────────────────────────────
    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"],
                                 line=dict(color="#a78bfa", width=1.5), name="RSI",
                                 fill="tozeroy", fillcolor="rgba(167,139,250,0.04)"), row=3, col=1)
        for lvl, clr2 in [(70,"rgba(248,113,113,0.5)"), (50,"rgba(251,191,36,0.35)"),
                          (30,"rgba(52,211,153,0.5)")]:
            fig.add_hline(y=lvl, line_dash="dot", line_color=clr2, line_width=1.2, row=3, col=1)
        fig.update_yaxes(range=[0,100], row=3, col=1)

    for ann in fig.layout.annotations:
        if hasattr(ann,"font") and ann.font:
            ann.font.color = "#94afd4"

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#080c18", plot_bgcolor="#0d1525",
        height=760,
        title=dict(
            text=f"<b>{symbol}</b>  ·  CMP vs All DMA Strategy  ·  {tf}  ·  Phase: <b>{dma_result['phase']}</b>",
            font=dict(family="Syne", size=16, color="#dce8f5"), x=0.01,
        ),
        legend=dict(orientation="h", y=1.005, x=0,
                    font=dict(size=11, color="#dce8f5"),
                    bgcolor="rgba(10,14,26,0.88)", bordercolor="#2a3d55", borderwidth=1),
        margin=dict(l=10, r=80, t=58, b=10),
        xaxis_rangeslider_visible=False,
        font=dict(color="#94afd4"),
    )
    for r in range(1,4):
        fig.update_xaxes(gridcolor="#111e30", row=r, col=1, tickfont=dict(color="#8aabcb",size=10))
        fig.update_yaxes(gridcolor="#111e30", row=r, col=1, tickfont=dict(color="#8aabcb",size=10))
    return fig



#  Returns a rich dict used for commentary + comparison score
# ─────────────────────────────────────────────────────────────────────────────
def surge_analysis(df, lookback=15):
    """
    Analyses the last `lookback` trading bars (≈3 weeks on daily TF) for:
      • Price surge / collapse vs prior baseline
      • Volume surge vs 20-bar average
      • Delivery % surge / collapse (institutional intent signal)
      • Trend of each metric (accelerating / fading)
      • Combined surge score  -10 … +10
      • Natural-language commentary lines for display
    """
    result = {
        "price_chg_pct": np.nan,
        "vol_surge_ratio": np.nan,
        "deliv_chg": np.nan,
        "price_trend": "neutral",
        "vol_trend": "neutral",
        "deliv_trend": "neutral",
        "surge_score": 0,
        "alert_level": "none",   # none | watch | caution | alert
        "direction": "neutral",  # bullish | bearish | neutral
        "commentary": [],
        "has_data": False,
    }

    n = len(df)
    if n < lookback + 5:
        result["commentary"].append("Insufficient data for surge analysis (need at least 20 bars).")
        return result

    recent   = df.iloc[-lookback:]          # last ~3 weeks
    baseline = df.iloc[-(lookback*2):-lookback]  # prior ~3 weeks as baseline
    last     = df.iloc[-1]
    score    = 0
    notes    = []

    # ── 1. PRICE SURGE ──────────────────────────────────────────────────────
    close_now   = recent["Close"].iloc[-1]
    close_start = recent["Close"].iloc[0]
    close_base  = baseline["Close"].mean() if len(baseline) > 0 else close_start

    price_chg_pct = (close_now / close_start - 1) * 100 if close_start else 0
    price_vs_base = (close_now / close_base - 1) * 100  if close_base  else 0

    # Price momentum within the window (first half vs second half)
    mid = len(recent) // 2
    p_first_half  = recent["Close"].iloc[:mid].mean()
    p_second_half = recent["Close"].iloc[mid:].mean()
    price_accelerating = p_second_half > p_first_half

    result["price_chg_pct"] = price_chg_pct

    if price_chg_pct >= 15:
        notes.append(f"🚀 <b>Strong Price Surge:</b> +{price_chg_pct:.1f}% in last {lookback} sessions — significant bullish momentum. Watch for continuation or exhaustion near resistance.")
        score += 3
        result["price_trend"] = "surging"
    elif price_chg_pct >= 7:
        notes.append(f"📈 <b>Moderate Price Rally:</b> +{price_chg_pct:.1f}% in {lookback} sessions vs prior base. {'Momentum still accelerating.' if price_accelerating else 'Momentum slowing in recent sessions — watch for distribution.'}")
        score += 2
        result["price_trend"] = "rising"
    elif price_chg_pct >= 3:
        notes.append(f"🟡 <b>Mild Price Gain:</b> +{price_chg_pct:.1f}% in {lookback} sessions. Steady but not yet a strong breakout.")
        score += 1
        result["price_trend"] = "rising"
    elif price_chg_pct <= -15:
        notes.append(f"💥 <b>Sharp Selloff:</b> {price_chg_pct:.1f}% in last {lookback} sessions — heavy selling pressure. Could see oversold bounce or continued breakdown.")
        score -= 3
        result["price_trend"] = "collapsing"
    elif price_chg_pct <= -7:
        notes.append(f"📉 <b>Significant Decline:</b> {price_chg_pct:.1f}% in {lookback} sessions. {'Selling accelerating — risk of further downside.' if not price_accelerating else 'Decline slowing — monitor for stabilisation.'}")
        score -= 2
        result["price_trend"] = "falling"
    elif price_chg_pct <= -3:
        notes.append(f"🟡 <b>Mild Price Weakness:</b> {price_chg_pct:.1f}% in {lookback} sessions. Contained pullback within normal range.")
        score -= 1
        result["price_trend"] = "falling"
    else:
        notes.append(f"⚪ <b>Price Flat:</b> {price_chg_pct:+.1f}% in {lookback} sessions — sideways consolidation. Awaiting directional catalyst.")
        result["price_trend"] = "neutral"

    # ── 2. VOLUME SURGE ──────────────────────────────────────────────────────
    if "Volume" in df.columns and "Vol_SMA20" in df.columns:
        avg_vol_recent   = recent["Volume"].mean()
        avg_vol_baseline = df["Vol_SMA20"].iloc[-lookback] if not np.isnan(df["Vol_SMA20"].iloc[-lookback]) else avg_vol_recent
        vol_surge_ratio  = avg_vol_recent / avg_vol_baseline if avg_vol_baseline > 0 else 1.0

        # trend: is volume expanding or contracting within the window?
        v_first = recent["Volume"].iloc[:mid].mean()
        v_second= recent["Volume"].iloc[mid:].mean()
        vol_expanding = v_second > v_first * 1.1
        vol_fading    = v_second < v_first * 0.85

        result["vol_surge_ratio"] = vol_surge_ratio

        # Peak volume day
        peak_vol_idx  = recent["Volume"].idxmax()
        peak_vol_date = df.loc[peak_vol_idx, "Date"].strftime("%d %b") if peak_vol_idx in df.index else "recent"
        peak_vol_x    = recent["Volume"].max() / avg_vol_baseline if avg_vol_baseline > 0 else 1.0

        if vol_surge_ratio >= 2.5:
            notes.append(f"🔊 <b>Extreme Volume Surge:</b> Avg volume {vol_surge_ratio:.1f}× the 20-day baseline (peak: {peak_vol_x:.1f}× on {peak_vol_date}). "
                         f"{'Volume still expanding — institutional activity likely ongoing.' if vol_expanding else 'Volume now fading — surge may be complete, watch for reversal.'}")
            score += 3 if price_chg_pct > 0 else -3
            result["vol_trend"] = "surging"
        elif vol_surge_ratio >= 1.6:
            notes.append(f"📢 <b>Above-Average Volume:</b> {vol_surge_ratio:.1f}× baseline in recent {lookback} sessions. "
                         f"{'Confirms move with strong participation.' if price_chg_pct > 0 else 'Heavy volume on decline — distribution signal.'}")
            score += 2 if price_chg_pct > 0 else -2
            result["vol_trend"] = "elevated"
        elif vol_surge_ratio >= 1.2:
            notes.append(f"🔉 <b>Slightly Elevated Volume:</b> {vol_surge_ratio:.1f}× baseline. Moderate interest — not a decisive breakout signal yet.")
            score += 1 if price_chg_pct > 0 else 0
            result["vol_trend"] = "elevated"
        elif vol_surge_ratio < 0.7:
            notes.append(f"🔕 <b>Volume Drying Up:</b> Only {vol_surge_ratio:.1f}× baseline. Low participation — {'rally lacks conviction, risk of fakeout.' if price_chg_pct > 0 else 'decline on low volume — sellers not aggressive, possible base forming.'}")
            score -= 1 if price_chg_pct > 0 else 1
            result["vol_trend"] = "drying"
        else:
            notes.append(f"⚪ <b>Volume Normal:</b> {vol_surge_ratio:.1f}× baseline — no unusual activity in recent sessions.")
            result["vol_trend"] = "normal"

        # Price-volume divergence check
        if price_chg_pct > 5 and vol_surge_ratio < 1.0:
            notes.append("⚠️ <b>Price-Volume Divergence:</b> Price rising but volume below average — rally lacks institutional support. High risk of reversal.")
            score -= 1
        if price_chg_pct < -5 and vol_surge_ratio < 0.8:
            notes.append("💡 <b>Decline on Low Volume:</b> Selling pressure weak (low volume). May indicate temporary weakness rather than a structural breakdown.")
            score += 1

    # ── 3. DELIVERY % SURGE ─────────────────────────────────────────────────
    if "Delivery%" in df.columns:
        deliv_recent  = recent["Delivery%"].dropna()
        deliv_base    = baseline["Delivery%"].dropna() if len(baseline) > 0 else deliv_recent

        if len(deliv_recent) >= 3 and len(deliv_base) >= 3:
            avg_deliv_recent = deliv_recent.mean()
            avg_deliv_base   = deliv_base.mean()
            deliv_chg        = avg_deliv_recent - avg_deliv_base
            last_deliv       = deliv_recent.iloc[-1]

            result["deliv_chg"] = deliv_chg

            # Trend within recent window
            d_first  = deliv_recent.iloc[:max(1,len(deliv_recent)//2)].mean()
            d_second = deliv_recent.iloc[max(1,len(deliv_recent)//2):].mean()
            deliv_rising = d_second > d_first

            if avg_deliv_recent >= 60 and deliv_chg >= 10:
                notes.append(f"🏦 <b>Institutional Accumulation Surge:</b> Delivery% rose to {avg_deliv_recent:.1f}% avg (was {avg_deliv_base:.1f}%, +{deliv_chg:.1f}pp). "
                             f"Strong quality buying — institutions are building positions. "
                             f"{'Delivery still rising — accumulation ongoing.' if deliv_rising else 'Delivery plateauing — watch if they continue.'}")
                score += 3 if price_chg_pct >= 0 else 2
                result["deliv_trend"] = "accumulating"
            elif avg_deliv_recent >= 50 and deliv_chg >= 5:
                notes.append(f"📦 <b>Rising Delivery Quality:</b> Avg delivery {avg_deliv_recent:.1f}% (up {deliv_chg:+.1f}pp vs prior period). "
                             f"Investor-grade buying increasing — supports price move sustainability.")
                score += 2 if price_chg_pct >= 0 else 1
                result["deliv_trend"] = "rising"
            elif avg_deliv_recent < 25 and deliv_chg <= -8:
                notes.append(f"🎲 <b>Delivery Collapse — Distribution Alert:</b> Delivery% dropped to {avg_deliv_recent:.1f}% avg (was {avg_deliv_base:.1f}%, {deliv_chg:.1f}pp). "
                             f"Move dominated by speculators/intraday traders — institutional selling suspected. "
                             f"{'Dangerous: price up but delivery falling = smart money exiting.' if price_chg_pct > 0 else 'Confirms bearish thesis — weak-hand selling.'}")
                score -= 3 if price_chg_pct > 0 else -1
                result["deliv_trend"] = "distributing"
            elif avg_deliv_recent < 30 and price_chg_pct > 5:
                notes.append(f"⚠️ <b>Low Delivery on Price Rise:</b> Delivery only {avg_deliv_recent:.1f}% despite rally. "
                             f"Speculative frenzy — high risk of sharp reversal when speculators exit.")
                score -= 2
                result["deliv_trend"] = "distributing"
            elif deliv_chg <= -10:
                notes.append(f"📉 <b>Delivery Declining:</b> Down {abs(deliv_chg):.1f}pp to {avg_deliv_recent:.1f}%. "
                             f"Institutional interest waning — monitor for continued deterioration.")
                score -= 1
                result["deliv_trend"] = "declining"
            else:
                notes.append(f"⚪ <b>Delivery Stable:</b> {avg_deliv_recent:.1f}% avg (base: {avg_deliv_base:.1f}%, Δ{deliv_chg:+.1f}pp) — no significant change in institutional activity.")
                result["deliv_trend"] = "stable"

    # ── 4. DAY-OVER-DAY RECENT MOMENTUM NARRATION ───────────────────────────
    # Narrate the last 3 sessions specifically (most recent activity)
    if n >= 4:
        dod_notes = []
        for back in [3, 2, 1]:    # 3 days ago → yesterday → today
            idx_now  = -back
            idx_prev = -back - 1
            d_now    = df.iloc[idx_now]
            d_prev   = df.iloc[idx_prev]
            day_lbl  = {1:"Today", 2:"Yesterday", 3:"2 days ago"}.get(back, f"{back}d ago")
            dt_str   = d_now["Date"].strftime("%d %b")

            p_chg = (d_now["Close"] / d_prev["Close"] - 1)*100 if d_prev["Close"] else 0
            p_icon = "▲" if p_chg > 0 else "▼"
            p_clr  = "color:#34d399" if p_chg > 0.3 else ("color:#f87171" if p_chg < -0.3 else "color:#94a3b8")

            vol_note = ""
            if "Volume" in df.columns and "Vol_SMA20" in df.columns:
                vr_now = d_now.get("Vol_Ratio", np.nan)
                if not np.isnan(vr_now):
                    if   vr_now > 2.5: vol_note = f" · Vol <b style='color:#fbbf24;'>{vr_now:.1f}×</b> avg 🔊"
                    elif vr_now > 1.5: vol_note = f" · Vol <b style='color:#34d399;'>{vr_now:.1f}×</b> avg"
                    elif vr_now < 0.6: vol_note = f" · Vol <b style='color:#f87171;'>{vr_now:.1f}×</b> avg 🔕"
                    else:              vol_note = f" · Vol {vr_now:.1f}× avg"

            deliv_note = ""
            if "Delivery%" in df.columns:
                dv = d_now.get("Delivery%", np.nan)
                dv_p = d_prev.get("Delivery%", np.nan)
                if not np.isnan(dv):
                    dv_chg = dv - dv_p if not np.isnan(dv_p) else 0
                    dv_clr = "color:#34d399" if dv > 55 else ("color:#f87171" if dv < 25 else "color:#94a3b8")
                    dv_delta = f"({dv_chg:+.1f}pp)" if abs(dv_chg) >= 2 else ""
                    deliv_note = f" · Delivery <b style='{dv_clr};'>{dv:.1f}%</b>{dv_delta}"

            dod_notes.append(
                f"<span style='color:#4a6a8a;font-size:0.73rem;'>{day_lbl} ({dt_str}):</span> "
                f"Close ₹{d_now['Close']:,.2f} "
                f"<b style='{p_clr};'>{p_icon}{abs(p_chg):.2f}%</b>"
                f"{vol_note}{deliv_note}"
            )

        notes.append(
            "📅 <b>Recent Day-by-Day Activity:</b><br>" +
            "<br>".join(dod_notes)
        )

    # ── 5. CONFLUENCE ASSESSMENT ─────────────────────────────────────────────
    if score >= 6:
        result["alert_level"] = "alert"
        result["direction"]   = "bullish"
        notes.append("🟢 <b>SURGE CONFLUENCE — BULLISH:</b> Price + Volume + Delivery all confirm a strong accumulation phase. High probability of continued upside. Watch for breakout above recent highs.")
    elif score >= 3:
        result["alert_level"] = "watch"
        result["direction"]   = "bullish"
        notes.append("🟡 <b>Moderate Bullish Confluence:</b> Most surge indicators align bullishly. Not yet a high-conviction signal — wait for either volume expansion or delivery confirmation.")
    elif score <= -6:
        result["alert_level"] = "alert"
        result["direction"]   = "bearish"
        notes.append("🔴 <b>SURGE CONFLUENCE — BEARISH:</b> Price + Volume + Delivery all signal distribution/selling. High probability of continued downside or sharp reversal. Protect positions.")
    elif score <= -3:
        result["alert_level"] = "caution"
        result["direction"]   = "bearish"
        notes.append("🟠 <b>Moderate Bearish Confluence:</b> Multiple indicators signal caution. Avoid fresh longs until delivery and volume confirm reversal.")
    else:
        result["alert_level"] = "none"
        result["direction"]   = "neutral"
        notes.append("⚪ <b>No Significant Surge Detected:</b> Price, volume, and delivery within normal ranges. No imminent breakout or breakdown signal from recent activity.")

    result["surge_score"] = max(-10, min(10, score))
    result["commentary"]  = notes
    result["has_data"]    = True
    return result


def build_surge_chart(df, lookback=15, symbol=""):
    """
    3-panel chart: Price bars | Volume bars | Delivery% bars
    All for the last lookback*2 bars, with the recent surge window highlighted.
    """
    n = len(df)
    if n < lookback + 2:
        return None

    window = min(lookback * 2 + 5, n)
    dfw = df.iloc[-window:].copy().reset_index(drop=True)
    surge_start_idx = len(dfw) - lookback

    has_vol   = "Volume"    in dfw.columns and dfw["Volume"].notna().any()
    has_deliv = "Delivery%" in dfw.columns and dfw["Delivery%"].notna().any()

    rows    = 1 + int(has_vol) + int(has_deliv)
    heights = ([0.55] + [0.225]*(rows-1)) if rows > 1 else [1.0]
    sub_titles = ["Price (Close)"]
    if has_vol:   sub_titles.append("Volume")
    if has_deliv: sub_titles.append("Delivery %")

    fig = make_subplots(rows=rows, cols=1, shared_xaxes=True,
                        vertical_spacing=0.06, row_heights=heights,
                        subplot_titles=sub_titles)

    # shade the surge window on all panels
    surge_start_date = dfw["Date"].iloc[surge_start_idx]
    surge_end_date   = dfw["Date"].iloc[-1]

    for r in range(1, rows+1):
        fig.add_vrect(x0=surge_start_date, x1=surge_end_date,
                      fillcolor="rgba(251,191,36,0.06)", line_width=0,
                      annotation_text="◀ Surge Window" if r==1 else "",
                      annotation_position="top left",
                      annotation_font_color="#fbbf24",
                      annotation_font_size=10,
                      row=r, col=1)

    # ── Row 1: Price ──
    up_clr   = "rgba(52,211,153,0.75)"
    dn_clr   = "rgba(248,113,113,0.75)"
    bar_clrs = []
    for i in dfw.index:
        pi = i-1 if i>0 else 0
        bar_clrs.append(up_clr if dfw.loc[i,"Close"] >= dfw.loc[pi,"Close"] else dn_clr)

    if {"Open","High","Low"}.issubset(dfw.columns):
        fig.add_trace(go.Candlestick(
            x=dfw["Date"], open=dfw["Open"], high=dfw["High"],
            low=dfw["Low"],  close=dfw["Close"], name="Price",
            increasing_line_color="#34d399", decreasing_line_color="#f87171",
            increasing_fillcolor="rgba(52,211,153,0.75)",
            decreasing_fillcolor="rgba(248,113,113,0.75)",
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=dfw["Date"], y=dfw["Close"],
                                 line=dict(color="#38bdf8", width=1.8), name="Close"), row=1, col=1)

    # SMA20 overlay
    if "SMA_20" in dfw.columns:
        fig.add_trace(go.Scatter(x=dfw["Date"], y=dfw["SMA_20"],
                                 line=dict(color="#38bdf8", width=1, dash="dot"),
                                 name="SMA20", showlegend=False), row=1, col=1)

    # vertical line at surge start
    fig.add_vline(x=surge_start_date, line_dash="dash",
                  line_color="rgba(251,191,36,0.5)", line_width=1.5, row=1, col=1)

    # ── Row 2: Volume (if available) ──
    cur_row = 2
    if has_vol:
        if "Vol_SMA20" in dfw.columns:
            baseline_vol = dfw["Vol_SMA20"].iloc[surge_start_idx-1] if surge_start_idx > 0 else dfw["Vol_SMA20"].median()
        else:
            baseline_vol = dfw["Volume"].iloc[:surge_start_idx].mean()

        surge_vol_clrs = []
        for i in dfw.index:
            if i >= surge_start_idx:
                v = dfw.loc[i, "Volume"]
                if not np.isnan(baseline_vol) and baseline_vol > 0:
                    ratio = v / baseline_vol
                    if ratio >= 2.0:   surge_vol_clrs.append("rgba(251,191,36,0.85)")
                    elif ratio >= 1.3: surge_vol_clrs.append("rgba(52,211,153,0.75)")
                    else:              surge_vol_clrs.append("rgba(52,211,153,0.45)")
                else:
                    surge_vol_clrs.append("rgba(52,211,153,0.55)")
            else:
                surge_vol_clrs.append("rgba(100,116,139,0.35)")

        fig.add_trace(go.Bar(x=dfw["Date"], y=dfw["Volume"], marker_color=surge_vol_clrs,
                             name="Volume", showlegend=False), row=cur_row, col=1)
        if "Vol_SMA20" in dfw.columns:
            fig.add_trace(go.Scatter(x=dfw["Date"], y=dfw["Vol_SMA20"],
                                     line=dict(color="#fbbf24", width=1.2, dash="dot"),
                                     name="Vol MA20", showlegend=False), row=cur_row, col=1)
        fig.add_vline(x=surge_start_date, line_dash="dash",
                      line_color="rgba(251,191,36,0.5)", line_width=1.5, row=cur_row, col=1)
        cur_row += 1

    # ── Row 3: Delivery% (if available) ──
    if has_deliv:
        deliv_clrs = []
        for i in dfw.index:
            d = dfw.loc[i, "Delivery%"]
            if np.isnan(d):
                deliv_clrs.append("rgba(100,116,139,0.3)")
            elif i >= surge_start_idx:
                if   d >= 60: deliv_clrs.append("rgba(52,211,153,0.85)")
                elif d >= 40: deliv_clrs.append("rgba(52,211,153,0.50)")
                elif d >= 25: deliv_clrs.append("rgba(251,191,36,0.55)")
                else:         deliv_clrs.append("rgba(248,113,113,0.75)")
            else:
                deliv_clrs.append("rgba(100,116,139,0.30)")

        fig.add_trace(go.Bar(x=dfw["Date"], y=dfw["Delivery%"],
                             marker_color=deliv_clrs, name="Delivery%", showlegend=False),
                      row=cur_row, col=1)
        # reference lines
        for lvl, clr in [(60,"rgba(52,211,153,0.4)"), (25,"rgba(248,113,113,0.4)")]:
            fig.add_hline(y=lvl, line_dash="dot", line_color=clr, line_width=1, row=cur_row, col=1)
        fig.add_vline(x=surge_start_date, line_dash="dash",
                      line_color="rgba(251,191,36,0.5)", line_width=1.5, row=cur_row, col=1)

    # ── annotations on chart subtitles ──
    for ann in fig.layout.annotations:
        if hasattr(ann, "font") and ann.font:
            ann.font.color = "#b8d0e8"

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#080c18",
        plot_bgcolor="#0d1525",
        height=520 + (has_vol + has_deliv) * 60,
        title=dict(
            text=f"<b>{symbol}</b>  ·  Surge Window Analysis  ·  Last {lookback} sessions highlighted",
            font=dict(family="Syne", size=15, color="#dce8f5"), x=0.01,
        ),
        showlegend=False,
        margin=dict(l=10, r=20, t=55, b=10),
        xaxis_rangeslider_visible=False,
        font=dict(color="#7a9cc0"),
    )
    for r in range(1, rows+1):
        fig.update_xaxes(gridcolor="#111e30", row=r, col=1, tickfont=dict(color="#8aabcb",size=11))
        fig.update_yaxes(gridcolor="#111e30", row=r, col=1, tickfont=dict(color="#8aabcb",size=11))

    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  BB + RSI DEDICATED CHART & SIGNAL ANALYSIS
#  Implements all 8 variants of the Bollinger Bands + RSI combined strategy
# ─────────────────────────────────────────────────────────────────────────────
def build_bb_rsi_chart(df, symbol, tf):
    """
    3-panel chart specifically for BB+RSI strategy analysis:
    Panel 1: Candlestick + all 4 Bollinger Band lines + BB+RSI buy/sell markers
    Panel 2: RSI with 65/50/35 reference lines + BB band position overlay
    Panel 3: BB Width (squeeze indicator) + volume
    """
    n = len(df)
    if n < 25:
        return None

    has_ohlc  = {"Open","High","Low","Close"}.issubset(df.columns)
    has_vol   = "Volume" in df.columns
    rows      = 3
    heights   = [0.50, 0.28, 0.22]

    fig = make_subplots(
        rows=rows, cols=1, shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=heights,
        subplot_titles=("Price + Bollinger Bands  (BB+RSI signals)", "RSI + Band Position", "BB Width (Squeeze) & Volume"),
    )

    # ── Panel 1: Price + Bollinger Bands ──────────────────────────────────────
    if has_ohlc:
        fig.add_trace(go.Candlestick(
            x=df["Date"], open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"], name="Price",
            increasing_line_color="#34d399", decreasing_line_color="#f87171",
            increasing_fillcolor="rgba(52,211,153,0.72)",
            decreasing_fillcolor="rgba(248,113,113,0.72)",
        ), row=1, col=1)
    else:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"],
                                 line=dict(color="#38bdf8",width=1.6), name="Close"), row=1, col=1)

    # BB lines
    if "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Upper"],
                                 line=dict(color="rgba(129,140,248,0.7)", width=1.4, dash="dot"),
                                 name="BB Upper", showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Mid"],
                                 line=dict(color="rgba(251,191,36,0.8)", width=1.2),
                                 name="BB Mid (SMA20)", showlegend=True), row=1, col=1)
        fig.add_trace(go.Scatter(x=df["Date"], y=df["BB_Lower"],
                                 fill="tonexty", fillcolor="rgba(129,140,248,0.05)",
                                 line=dict(color="rgba(129,140,248,0.7)", width=1.4, dash="dot"),
                                 name="BB Lower", showlegend=True), row=1, col=1)

    # ── Detect all 8 BB+RSI signals and plot markers ──────────────────────────
    close  = df["Close"].values
    rsi    = df["RSI"].values   if "RSI"    in df.columns else np.full(n, np.nan)
    bb_u   = df["BB_Upper"].values if "BB_Upper" in df.columns else np.full(n, np.nan)
    bb_l   = df["BB_Lower"].values if "BB_Lower" in df.columns else np.full(n, np.nan)
    bb_m   = df["BB_Mid"].values   if "BB_Mid"   in df.columns else np.full(n, np.nan)
    macd   = df["MACD"].values       if "MACD"       in df.columns else np.full(n, np.nan)
    macd_s = df["MACD_Signal"].values if "MACD_Signal" in df.columns else np.full(n, np.nan)
    vr     = df["Vol_Ratio"].values  if "Vol_Ratio"  in df.columns else np.full(n, 1.0)
    sma20  = df["SMA_20"].values     if "SMA_20"     in df.columns else np.full(n, np.nan)
    sma50  = df["SMA_50"].values     if "SMA_50"     in df.columns else np.full(n, np.nan)
    dates  = df["Date"].values

    signals_plot = {
        "BB Lower+RSI Oversold": {"dates":[], "prices":[], "type":"buy",  "sym":"triangle-up",   "clr":"#34d399", "size":14},
        "BB+RSI+MACD Triple Buy":{"dates":[], "prices":[], "type":"buy",  "sym":"star",           "clr":"#00ffcc", "size":16},
        "BB Lower Bounce Entry": {"dates":[], "prices":[], "type":"buy",  "sym":"circle",         "clr":"#a7f3d0", "size":11},
        "BB Mid Reclaim":        {"dates":[], "prices":[], "type":"buy",  "sym":"diamond",        "clr":"#38bdf8", "size":12},
        "BB Upper+RSI Overbought":{"dates":[],"prices":[], "type":"sell", "sym":"triangle-down",  "clr":"#f87171", "size":14},
        "BB Upper Rejection":    {"dates":[], "prices":[], "type":"sell", "sym":"circle",         "clr":"#fca5a5", "size":11},
        "BB Squeeze Breakout":   {"dates":[], "prices":[], "type":"buy",  "sym":"hexagram",       "clr":"#fbbf24", "size":15},
        "BB Band Walk":          {"dates":[], "prices":[], "type":"buy",  "sym":"square",         "clr":"#818cf8", "size":10},
    }

    for i in range(1, n):
        c, r, u, l, m = close[i], rsi[i], bb_u[i], bb_l[i], bb_m[i]
        mc, ms = macd[i], macd_s[i]
        v = vr[i] if not np.isnan(vr[i]) else 1.0
        cp = close[i-1]; rp = rsi[i-1]
        up = bb_u[i-1]; lp = bb_l[i-1]; mp = bb_m[i-1]
        mcp = macd[i-1]; msp = macd_s[i-1]
        s20, s50 = sma20[i], sma50[i]

        if any(np.isnan(x) for x in [c,r,u,l,m]): continue
        dt = dates[i]

        # S1: BB Lower + RSI Oversold
        if c < l and r < 35 and v > 0.8:
            signals_plot["BB Lower+RSI Oversold"]["dates"].append(dt)
            signals_plot["BB Lower+RSI Oversold"]["prices"].append(c)

        # S2: BB + RSI + MACD Triple
        if c < l and r < 38 and not np.isnan(mc) and mc > ms and v > 1.0:
            signals_plot["BB+RSI+MACD Triple Buy"]["dates"].append(dt)
            signals_plot["BB+RSI+MACD Triple Buy"]["prices"].append(c)

        # S3: Price crosses back above lower band
        if cp < lp and c > l and r < 45 and c < m:
            signals_plot["BB Lower Bounce Entry"]["dates"].append(dt)
            signals_plot["BB Lower Bounce Entry"]["prices"].append(c)

        # S4: Price crosses above middle band with RSI >50
        if cp < mp and c > m and rp < 50 and r > 50:
            signals_plot["BB Mid Reclaim"]["dates"].append(dt)
            signals_plot["BB Mid Reclaim"]["prices"].append(c)

        # S5: BB Upper + RSI Overbought
        if c > u and r > 65 and not np.isnan(mc) and mc < ms:
            signals_plot["BB Upper+RSI Overbought"]["dates"].append(dt)
            signals_plot["BB Upper+RSI Overbought"]["prices"].append(c)

        # S6: Price crosses back below upper band
        if cp > up and c < u and r > 60 and c > m:
            signals_plot["BB Upper Rejection"]["dates"].append(dt)
            signals_plot["BB Upper Rejection"]["prices"].append(c)

        # S7: BB Squeeze breakout (price breaks above upper with RSI 55-72)
        if c > u and r > 55 and r < 72 and v > 1.5 and c > m:
            signals_plot["BB Squeeze Breakout"]["dates"].append(dt)
            signals_plot["BB Squeeze Breakout"]["prices"].append(c)

        # S8: Band walk (sustained strength)
        if (c > m and c > s20 and not np.isnan(s20) and not np.isnan(s50)
                and s20 > s50 and r > 58 and r < 80
                and not np.isnan(mc) and mc > ms):
            signals_plot["BB Band Walk"]["dates"].append(dt)
            signals_plot["BB Band Walk"]["prices"].append(c)

    buy_labels  = ["BB Lower+RSI Oversold","BB+RSI+MACD Triple Buy","BB Lower Bounce Entry",
                   "BB Mid Reclaim","BB Squeeze Breakout","BB Band Walk"]
    sell_labels = ["BB Upper+RSI Overbought","BB Upper Rejection"]

    for name, d in signals_plot.items():
        if not d["dates"]: continue
        tpos = "top center" if d["type"]=="buy" else "bottom center"
        short_lbl = name[:8]
        fig.add_trace(go.Scatter(
            x=d["dates"], y=d["prices"],
            mode="markers+text",
            marker=dict(symbol=d["sym"], size=d["size"], color=d["clr"],
                        line=dict(color="white", width=0.8)),
            text=[short_lbl]*len(d["dates"]),
            textposition=tpos,
            textfont=dict(size=7, color="white"),
            name=name,
        ), row=1, col=1)

    # ── Panel 2: RSI + band position ─────────────────────────────────────────
    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"], y=df["RSI"],
                                 line=dict(color="#a78bfa", width=1.8), name="RSI",
                                 fill="tozeroy", fillcolor="rgba(167,139,250,0.04)"), row=2, col=1)
        # Reference lines
        for lvl, clr, lbl in [(70,"rgba(248,113,113,0.6)","OB 70"),
                               (65,"rgba(248,113,113,0.35)","65"),
                               (50,"rgba(251,191,36,0.45)","50"),
                               (35,"rgba(52,211,153,0.35)","35"),
                               (30,"rgba(52,211,153,0.6)","OS 30")]:
            fig.add_hline(y=lvl, line_dash="dot", line_color=clr, line_width=1.2,
                          annotation_text=lbl, annotation_font_color=clr,
                          annotation_position="right", row=2, col=1)
        fig.add_hrect(y0=65, y1=100, fillcolor="rgba(248,113,113,0.05)", line_width=0, row=2, col=1)
        fig.add_hrect(y0=0,  y1=35,  fillcolor="rgba(52,211,153,0.05)",  line_width=0, row=2, col=1)

        # Band position % on secondary y-like overlay (0-100% of BB range)
        if "BB_Upper" in df.columns:
            bb_range = df["BB_Upper"] - df["BB_Lower"]
            bb_pct   = ((df["Close"] - df["BB_Lower"]) / bb_range.replace(0, np.nan) * 100).clip(0,100)
            fig.add_trace(go.Scatter(x=df["Date"], y=bb_pct,
                                     line=dict(color="rgba(251,191,36,0.5)", width=1, dash="dot"),
                                     name="BB Position%", showlegend=True), row=2, col=1)

    # ── Panel 3: BB Width (squeeze) + volume ──────────────────────────────────
    if "BB_Width" in df.columns:
        # Colour BB Width: green when expanding, red when contracting
        bw = df["BB_Width"].values
        bw_clrs = []
        for i in range(len(bw)):
            if i == 0 or np.isnan(bw[i]) or np.isnan(bw[i-1]):
                bw_clrs.append("rgba(100,116,139,0.5)")
            elif bw[i] > bw[i-1]:
                bw_clrs.append("rgba(52,211,153,0.65)")
            else:
                bw_clrs.append("rgba(248,113,113,0.65)")
        fig.add_trace(go.Bar(x=df["Date"], y=df["BB_Width"],
                             marker_color=bw_clrs, name="BB Width", showlegend=True), row=3, col=1)

        # Squeeze threshold line (20th percentile of historical width)
        bw_valid = [v for v in bw if not np.isnan(v)]
        if bw_valid:
            squeeze_threshold = np.percentile(bw_valid, 20)
            fig.add_hline(y=squeeze_threshold, line_dash="dot",
                          line_color="rgba(251,191,36,0.6)", line_width=1.5,
                          annotation_text="Squeeze zone", annotation_font_color="#fbbf24",
                          row=3, col=1)

    for ann in fig.layout.annotations:
        if hasattr(ann,"font") and ann.font:
            ann.font.color = "#94afd4"

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#080c18", plot_bgcolor="#0d1525",
        height=780,
        title=dict(
            text=f"<b>{symbol}</b>  ·  Bollinger Bands + RSI Strategy Chart  ·  {tf}",
            font=dict(family="Syne", size=16, color="#dce8f5"), x=0.01,
        ),
        legend=dict(orientation="h", y=1.005, x=0,
                    font=dict(size=11, color="#dce8f5"),
                    bgcolor="rgba(10,14,26,0.88)", bordercolor="#2a3d55", borderwidth=1),
        margin=dict(l=10, r=60, t=58, b=10),
        xaxis_rangeslider_visible=False,
        font=dict(color="#94afd4"),
    )
    for r in range(1, rows+1):
        fig.update_xaxes(gridcolor="#111e30", row=r, col=1, tickfont=dict(color="#8aabcb",size=10))
        fig.update_yaxes(gridcolor="#111e30", row=r, col=1, tickfont=dict(color="#8aabcb",size=10))
    if "RSI" in df.columns:
        fig.update_yaxes(range=[0,100], row=2, col=1)

    return fig


def bb_rsi_current_status(df):
    """Return current BB+RSI status summary dict for the latest bar."""
    last  = df.iloc[-1]
    prev  = df.iloc[-2] if len(df) > 1 else last
    cl    = last.get("Close",  np.nan)
    rsi   = last.get("RSI",    np.nan)
    bbu   = last.get("BB_Upper",np.nan)
    bbl   = last.get("BB_Lower",np.nan)
    bbm   = last.get("BB_Mid", np.nan)
    bbw   = last.get("BB_Width",np.nan)
    macd  = last.get("MACD",   np.nan)
    macds = last.get("MACD_Signal",np.nan)
    vr    = last.get("Vol_Ratio",  np.nan)

    # BB position %
    bb_range = bbu - bbl if not (np.isnan(bbu) or np.isnan(bbl)) else np.nan
    bb_pct   = ((cl - bbl) / bb_range * 100) if not np.isnan(bb_range) and bb_range > 0 else np.nan

    # Squeeze detection (current width vs 20-period historical)
    if "BB_Width" in df.columns:
        hist_widths = df["BB_Width"].dropna()
        squeeze_thr = hist_widths.quantile(0.20) if len(hist_widths) >= 20 else np.nan
        is_squeeze  = (not np.isnan(bbw)) and (not np.isnan(squeeze_thr)) and (bbw <= squeeze_thr)
    else:
        is_squeeze = False; squeeze_thr = np.nan

    # Active signals
    active = []
    if not any(np.isnan(x) for x in [cl,rsi,bbl]):
        if cl < bbl and rsi < 35:                        active.append(("🟢 BB Lower + RSI Oversold",          "buy",    "Strong reversal buy — price at lower band, RSI oversold"))
        if cl < bbl and rsi < 38 and macd > macds:       active.append(("🟢⭐ BB+RSI+MACD Triple Confirm",      "buy",    "Highest conviction buy — all 3 indicators aligned"))
        if prev.get("Close",cl) < prev.get("BB_Lower",bbl) and cl > bbl and rsi < 45:
                                                          active.append(("🟢 BB Lower Bounce Entry",             "buy",    "Bounce confirmed — entry signal triggered"))
        if prev.get("Close",cl) < prev.get("BB_Mid",bbm) and cl > bbm and rsi > 50:
                                                          active.append(("🟢 BB Middle Band Reclaim",             "buy",    "Momentum shift — middle band reclaimed"))
    if not any(np.isnan(x) for x in [cl,rsi,bbu]):
        if cl > bbu and rsi > 65 and macd < macds:       active.append(("🔴 BB Upper + RSI Overbought",         "sell",   "Reversal sell — price at upper band, RSI overbought"))
        if prev.get("Close",cl) > prev.get("BB_Upper",bbu) and cl < bbu and rsi > 60:
                                                          active.append(("🔴 BB Upper Rejection",                 "sell",   "Rejection confirmed — entry signal triggered"))
        if cl > bbu and rsi > 55 and rsi < 72 and not np.isnan(vr) and vr > 1.5:
                                                          active.append(("🟡 BB Squeeze Breakout",                "buy",    "Volatility expansion — potential strong uptrend starting"))

    return {
        "cl": cl, "rsi": rsi, "bbu": bbu, "bbl": bbl, "bbm": bbm, "bbw": bbw,
        "bb_pct": bb_pct, "is_squeeze": is_squeeze, "squeeze_thr": squeeze_thr,
        "active_signals": active,
        "vr": vr,
    }



def generate_signals(df):
    """
    Signal engine reads indicator values only.
    The % change shown in the screenshot (portfolio P&L) is IRRELEVANT to signal direction.
    A stock can be up 50% YTD and still have a SELL signal if current indicators are bearish.
    """
    last=df.iloc[-1]; prev=df.iloc[-2] if len(df)>1 else last
    sigs={}; score=0

    # ── RSI ──
    rsi=last.get("RSI",np.nan)
    if not np.isnan(rsi):
        if rsi < 35:
            sigs["RSI"] = ("🟢 Oversold (<35) — Potential reversal upward", "buy"); score+=1
        elif rsi > 70:
            sigs["RSI"] = (f"🔴 Overbought (>70, RSI={rsi:.1f}) — Risk of pullback", "sell"); score-=1
        elif rsi > 60:
            sigs["RSI"] = (f"🟡 RSI={rsi:.1f} — Bullish momentum zone (60-70)", "neu"); score+=0
        elif rsi < 40:
            sigs["RSI"] = (f"🟡 RSI={rsi:.1f} — Bearish momentum zone (30-40)", "neu"); score+=0
        else:
            sigs["RSI"] = (f"⚪ RSI={rsi:.1f} — Neutral zone", "neu")

    # ── MACD ──
    macd,sl = last.get("MACD",np.nan), last.get("MACD_Signal",np.nan)
    if not(np.isnan(macd) or np.isnan(sl)):
        pm,ps = prev.get("MACD",macd), prev.get("MACD_Signal",sl)
        if   macd>sl and pm<=ps: sigs["MACD"]=("🟢 Bullish MACD crossover — Fresh buy signal","buy"); score+=2
        elif macd<sl and pm>=ps: sigs["MACD"]=("🔴 Bearish MACD crossover — Fresh sell signal","sell"); score-=2
        elif macd>sl:            sigs["MACD"]=("🟢 MACD above signal — Bullish bias","buy"); score+=1
        else:                    sigs["MACD"]=("🔴 MACD below signal — Bearish bias","sell"); score-=1

    # ── Bollinger Bands ──
    cl=last.get("Close",np.nan); bbu=last.get("BB_Upper",np.nan); bbl=last.get("BB_Lower",np.nan)
    if not any(np.isnan(x) for x in [cl,bbu,bbl]):
        if   cl>bbu: sigs["BB"]=("🔴 Above upper BB — Statistically extended, mean-reversion risk","sell"); score-=1
        elif cl<bbl: sigs["BB"]=("🟢 Below lower BB — Statistically oversold, bounce likely","buy"); score+=1
        else:
            pct=(cl-bbl)/(bbu-bbl)*100
            sigs["BB"]=(f"⚪ Price at {pct:.0f}% within BB range","neu")

    # ── Moving Average Trend ──
    s20,s50 = last.get("SMA_20",np.nan), last.get("SMA_50",np.nan)
    if not(np.isnan(s20) or np.isnan(s50)):
        if   cl>s20 and s20>s50: sigs["MA Trend"]=("🟢 Price>SMA20>SMA50 — Confirmed uptrend","buy"); score+=2
        elif cl<s20 and s20<s50: sigs["MA Trend"]=("🔴 Price<SMA20<SMA50 — Confirmed downtrend","sell"); score-=2
        elif cl>s20:             sigs["MA Trend"]=("🟡 Price above SMA20, SMA20<SMA50 — Recovering","neu"); score+=1
        elif cl<s20:             sigs["MA Trend"]=("🟡 Price below SMA20, SMA20>SMA50 — Weakening","neu"); score-=1
        else:                    sigs["MA Trend"]=("⚪ Mixed MA alignment","neu")

    # ── EMA9 Trend ──
    e9=last.get("EMA_9",np.nan)
    if not np.isnan(e9):
        if   cl>e9: sigs["EMA9"]=("🟢 Close above EMA9 — Short-term bullish","buy"); score+=1
        else:       sigs["EMA9"]=("🔴 Close below EMA9 — Short-term bearish","sell"); score-=1

    # ── Volume ──
    vr=last.get("Vol_Ratio",np.nan)
    if not np.isnan(vr):
        if   vr>1.5: sigs["Volume"]=(f"🟢 Volume {vr:.1f}× avg — Strong participation","buy"); score+=1
        elif vr<0.5: sigs["Volume"]=(f"⚪ Low volume {vr:.1f}× avg — Thin conviction","neu")
        else:        sigs["Volume"]=(f"⚪ Normal volume {vr:.1f}× avg","neu")

    # ── Stochastic ──
    stk=last.get("Stoch_K",np.nan)
    if not np.isnan(stk):
        if   stk<20: sigs["Stoch"]=(f"🟢 Stoch K={stk:.0f} — Oversold zone","buy"); score+=1
        elif stk>80: sigs["Stoch"]=(f"🔴 Stoch K={stk:.0f} — Overbought zone","sell"); score-=1
        else:        sigs["Stoch"]=(f"⚪ Stoch K={stk:.0f} — Neutral","neu")

    # ── Delivery ──
    d=last.get("Delivery%",np.nan)
    if not np.isnan(d):
        if   d>60: sigs["Delivery%"]=(f"🟢 {d:.1f}% delivery — Institutional accumulation","buy"); score+=1
        elif d<25: sigs["Delivery%"]=(f"🔴 {d:.1f}% delivery — Speculative/distribution","sell"); score-=1
        else:      sigs["Delivery%"]=(f"⚪ {d:.1f}% delivery — Normal","neu")

    # ── Verdict ──
    if   score>=6:  verdict=("STRONG BUY","buy")
    elif score>=3:  verdict=("BUY","buy")
    elif score<=-6: verdict=("STRONG SELL","sell")
    elif score<=-3: verdict=("SELL","sell")
    else:           verdict=("HOLD / SIDEWAYS","neu")
    return {"signals":sigs,"score":score,"verdict":verdict}


# ─────────────────────────────────────────────────────────────────────────────
#  BUILT-IN STRATEGIES  — returns triggers WITH full detail for trigger log
# ─────────────────────────────────────────────────────────────────────────────
def run_builtin_strategies(df):
    res = []
    if len(df) < 3: return res
    rsi   = df["RSI"].values
    ema9  = df["EMA_9"].values
    sma14 = df["SMA_14"].values
    close = df["Close"].values
    dates = df["Date"].values

    def fd(i): return pd.Timestamp(dates[i]).strftime("%d %b %Y")

    # ── S1A: RSI crosses UP through 40 AND close > EMA9 → BUY ──
    s1a = [(i, fd(i), f"{rsi[i]:.1f}", f"₹{close[i]:,.2f}", f"₹{ema9[i]:,.2f}", "-")
           for i in range(1,len(df))
           if (rsi[i-1]<40) and (rsi[i]>=40) and not np.isnan(rsi[i])
           and (close[i]>ema9[i]) and not np.isnan(ema9[i])]
    if s1a:
        li=s1a[-1][0]
        res.append({"name":"S1A · RSI↑40 & Close > EMA9","signal":"buy",
                    "desc":"RSI crossed above 40 with close above EMA9 — momentum reversal up",
                    "detail":f"Last: {s1a[-1][1]} | RSI {s1a[-1][2]} | Close {s1a[-1][3]} | EMA9 {s1a[-1][4]}",
                    "bars":[x[0] for x in s1a],"trigger_log":s1a,
                    "log_cols":["Bar#","Date","RSI","Close","EMA9","SMA14"]})
    else:
        res.append({"name":"S1A · RSI↑40 & Close > EMA9","signal":"wait",
                    "desc":"Watching: RSI to cross above 40 with Close above EMA9",
                    "detail":f"Current RSI: {rsi[-1]:.1f} | Close ₹{close[-1]:,.2f} | EMA9 ₹{ema9[-1]:,.2f}",
                    "bars":[],"trigger_log":[],"log_cols":["Bar#","Date","RSI","Close","EMA9","SMA14"]})

    # ── S1B: RSI crosses DOWN through 60 AND close < EMA9 → SELL ──
    s1b = [(i, fd(i), f"{rsi[i]:.1f}", f"₹{close[i]:,.2f}", f"₹{ema9[i]:,.2f}", "-")
           for i in range(1,len(df))
           if (rsi[i-1]>60) and (rsi[i]<=60) and not np.isnan(rsi[i])
           and (close[i]<ema9[i]) and not np.isnan(ema9[i])]
    if s1b:
        li=s1b[-1][0]
        res.append({"name":"S1B · RSI↓60 & Close < EMA9","signal":"sell",
                    "desc":"RSI crossed below 60 with close below EMA9 — momentum reversal down",
                    "detail":f"Last: {s1b[-1][1]} | RSI {s1b[-1][2]} | Close {s1b[-1][3]} | EMA9 {s1b[-1][4]}",
                    "bars":[x[0] for x in s1b],"trigger_log":s1b,
                    "log_cols":["Bar#","Date","RSI","Close","EMA9","SMA14"]})
    else:
        res.append({"name":"S1B · RSI↓60 & Close < EMA9","signal":"wait",
                    "desc":"Watching: RSI to cross below 60 with Close below EMA9",
                    "detail":f"Current RSI: {rsi[-1]:.1f} | Close ₹{close[-1]:,.2f} | EMA9 ₹{ema9[-1]:,.2f}",
                    "bars":[],"trigger_log":[],"log_cols":["Bar#","Date","RSI","Close","EMA9","SMA14"]})

    # ── S2: RSI crosses ABOVE 60 AND close > SMA14 → BUY ──
    s2 = [(i, fd(i), f"{rsi[i]:.1f}", f"₹{close[i]:,.2f}", f"₹{ema9[i]:,.2f}", f"₹{sma14[i]:,.2f}")
          for i in range(1,len(df))
          if (rsi[i-1]<60) and (rsi[i]>=60) and not np.isnan(rsi[i])
          and (close[i]>sma14[i]) and not np.isnan(sma14[i])]
    if s2:
        li=s2[-1][0]
        res.append({"name":"S2 · RSI↑60 & Close > SMA14","signal":"buy",
                    "desc":"RSI broke above 60 (momentum breakout) with close above SMA14",
                    "detail":f"Last: {s2[-1][1]} | RSI {s2[-1][2]} | Close {s2[-1][3]} | SMA14 {s2[-1][5]}",
                    "bars":[x[0] for x in s2],"trigger_log":s2,
                    "log_cols":["Bar#","Date","RSI","Close","EMA9","SMA14"]})
    else:
        res.append({"name":"S2 · RSI↑60 & Close > SMA14","signal":"wait",
                    "desc":"Watching: RSI momentum breakout above 60 with close above SMA14",
                    "detail":f"Current RSI: {rsi[-1]:.1f} | Close ₹{close[-1]:,.2f} | SMA14 ₹{sma14[-1]:,.2f}",
                    "bars":[],"trigger_log":[],"log_cols":["Bar#","Date","RSI","Close","EMA9","SMA14"]})
    return res


# ─────────────────────────────────────────────────────────────────────────────
#  CUSTOM STRATEGY PARSER & RUNNER
# ─────────────────────────────────────────────────────────────────────────────
AVAILABLE_COLS = {
    "RSI":"RSI (14-period RSI)",
    "EMA9":"EMA_9 (9-period EMA)",
    "EMA12":"EMA_12","EMA26":"EMA_26",
    "SMA14":"SMA_14 (14-period SMA)",
    "SMA20":"SMA_20","SMA50":"SMA_50",
    "MACD":"MACD","MACD_Signal":"MACD_Signal","MACD_Hist":"MACD_Hist",
    "Close":"Close","Open":"Open","High":"High","Low":"Low",
    "Volume":"Volume","Vol_Ratio":"Vol_Ratio",
    "ATR":"ATR","ATR_pct":"ATR%",
    "Stoch_K":"Stoch_K","Stoch_D":"Stoch_D",
    "BB_Upper":"BB_Upper","BB_Lower":"BB_Lower","BB_Mid":"BB_Mid",
    "Delivery":"Delivery%",
    "OBV":"OBV","ROC5":"ROC_5","ROC20":"ROC_20",
}

CUSTOM_STRATEGY_HELP = """
**How to write custom strategies:**

Each condition uses format:
`INDICATOR OPERATOR VALUE` or `INDICATOR OPERATOR INDICATOR`

**Operators:** `>`, `<`, `>=`, `<=`, `crosses_above`, `crosses_below`

**Available indicators:**
`RSI`, `EMA9`, `SMA14`, `SMA20`, `SMA50`, `MACD`, `MACD_Signal`,
`Close`, `Open`, `High`, `Low`, `Volume`, `Vol_Ratio`,
`ATR`, `Stoch_K`, `Stoch_D`, `BB_Upper`, `BB_Lower`, `Delivery`

**Examples:**
```
Name: My RSI + EMA Strategy
Signal: BUY
Conditions (ALL must be true):
RSI crosses_above 50
Close > EMA9
MACD > MACD_Signal
```

```
Name: Breakdown Alert
Signal: SELL
Conditions (ALL must be true):
RSI < 45
Close < SMA20
Stoch_K < 40
```
"""

def parse_custom_strategy(text):
    """Parse custom strategy text → dict with name, signal, conditions"""
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    result = {"name":"Custom Strategy","signal":"buy","conditions":[],"raw":text}
    for line in lines:
        ll = line.lower()
        if ll.startswith("name:"):
            result["name"] = line[5:].strip()
        elif ll.startswith("signal:"):
            sig = line[7:].strip().lower()
            result["signal"] = "buy" if "buy" in sig else ("sell" if "sell" in sig else "buy")
        elif any(op in line for op in [">","<","crosses_above","crosses_below",">=","<="]):
            result["conditions"].append(line.strip())
    return result

def eval_condition(df, cond_str, i):
    """Evaluate a single condition for bar i. Returns True/False."""
    cond_str = cond_str.strip()
    # map friendly names to df column names
    col_alias = {
        "RSI":"RSI","EMA9":"EMA_9","EMA12":"EMA_12","EMA26":"EMA_26",
        "SMA14":"SMA_14","SMA20":"SMA_20","SMA50":"SMA_50",
        "MACD":"MACD","MACD_Signal":"MACD_Signal","MACD_Hist":"MACD_Hist",
        "Close":"Close","Open":"Open","High":"High","Low":"Low",
        "Volume":"Volume","Vol_Ratio":"Vol_Ratio",
        "ATR":"ATR","ATR_pct":"ATR%",
        "Stoch_K":"Stoch_K","Stoch_D":"Stoch_D",
        "BB_Upper":"BB_Upper","BB_Lower":"BB_Lower","BB_Mid":"BB_Mid",
        "Delivery":"Delivery%","OBV":"OBV","ROC5":"ROC_5","ROC20":"ROC_20",
    }

    def get_val(token, idx):
        t = token.strip()
        if t in col_alias and col_alias[t] in df.columns:
            return df[col_alias[t]].iloc[idx]
        try:
            return float(t)
        except:
            return np.nan

    try:
        if "crosses_above" in cond_str:
            parts = cond_str.split("crosses_above")
            left  = get_val(parts[0], i)
            right = get_val(parts[1], i)
            left_prev  = get_val(parts[0], i-1)
            right_prev = get_val(parts[1], i-1) if parts[1].strip() not in [str(float(x)) for x in []] else right
            return (left_prev < right_prev) and (left >= right)
        elif "crosses_below" in cond_str:
            parts = cond_str.split("crosses_below")
            left  = get_val(parts[0], i)
            right = get_val(parts[1], i)
            left_prev  = get_val(parts[0], i-1)
            right_prev = get_val(parts[1], i-1) if parts[1].strip() not in [str(float(x)) for x in []] else right
            return (left_prev > right_prev) and (left <= right)
        elif ">=" in cond_str:
            p=cond_str.split(">="); return get_val(p[0],i) >= get_val(p[1],i)
        elif "<=" in cond_str:
            p=cond_str.split("<="); return get_val(p[0],i) <= get_val(p[1],i)
        elif ">" in cond_str:
            p=cond_str.split(">"); return get_val(p[0],i) > get_val(p[1],i)
        elif "<" in cond_str:
            p=cond_str.split("<"); return get_val(p[0],i) < get_val(p[1],i)
        return False
    except:
        return False

def run_custom_strategy(df, strat_def):
    """Run parsed custom strategy on df. Returns list of trigger bar indices."""
    conditions = strat_def.get("conditions",[])
    if not conditions: return []
    triggers = []
    for i in range(1, len(df)):
        if all(eval_condition(df, c, i) for c in conditions):
            triggers.append(i)
    return triggers


# ─────────────────────────────────────────────────────────────────────────────
#  P&L SIMULATION  — per trigger, forward-track price for hold_bars
# ─────────────────────────────────────────────────────────────────────────────
def compute_trade_pnl(df, bars, signal, hold_bars=10):
    """
    For each trigger bar, simulate:
      - Entry at close on trigger bar
      - Exit at close after hold_bars bars (or last bar if data runs out)
    Returns:
      trades     : list of dicts with entry/exit info
      equity_df  : cumulative compounded equity curve (1 unit per trade)
      forward_df : per-trade forward P&L curves (for overlay chart)
    """
    close = df["Close"].values
    dates = df["Date"].values
    n = len(close)

    trades = []
    equity = [100.0]          # starts at 100
    running = 100.0
    forward_curves = []       # list of (bar_offsets, pnl_pct_series, label)

    for entry_bar in bars:
        entry_price = close[entry_bar]
        exit_bar    = min(entry_bar + hold_bars, n - 1)
        exit_price  = close[exit_bar]

        # forward curve from entry to exit
        fwd_pct = []
        for b in range(entry_bar, exit_bar + 1):
            pct = (close[b] / entry_price - 1) * 100
            if signal == "sell":
                pct = -pct          # short trade: profit if price falls
            fwd_pct.append(pct)
        offsets = list(range(len(fwd_pct)))
        label   = pd.Timestamp(dates[entry_bar]).strftime("%d %b %Y")
        forward_curves.append((offsets, fwd_pct, label))

        # trade result
        raw_pct = (exit_price / entry_price - 1) * 100
        trade_pct = raw_pct if signal == "buy" else -raw_pct

        running = running * (1 + trade_pct / 100)
        equity.append(running)

        trades.append({
            "Entry Date":   pd.Timestamp(dates[entry_bar]).strftime("%d %b %Y"),
            "Entry ₹":      f"{entry_price:,.2f}",
            "Exit Date":    pd.Timestamp(dates[exit_bar]).strftime("%d %b %Y"),
            "Exit ₹":       f"{exit_price:,.2f}",
            "Hold (bars)":  exit_bar - entry_bar,
            "P&L %":        f"{trade_pct:+.2f}%",
            "Result":       "✅ WIN" if trade_pct > 0 else ("🔴 LOSS" if trade_pct < 0 else "➖ FLAT"),
        })

    # equity curve indexed by trade number
    equity_dates = [pd.Timestamp(dates[b]).strftime("%d %b") for b in bars]
    equity_df = pd.DataFrame({
        "Trade": ["Start"] + [f"T{i+1}\n{d}" for i, d in enumerate(equity_dates)],
        "Equity": equity,
    })
    return trades, equity_df, forward_curves


def build_pnl_chart(df, bars, signal, strat_name, hold_bars=10):
    """Builds a 3-panel P&L chart: equity curve, per-trade bar chart, forward curves overlay."""
    if not bars:
        return None

    trades, equity_df, forward_curves = compute_trade_pnl(df, bars, signal, hold_bars)
    pnl_vals = [float(t["P&L %"].replace("%","").replace("+","")) for t in trades]
    trade_labels = [t["Entry Date"] for t in trades]
    results = [t["Result"] for t in trades]

    bar_colors = ["rgba(52,211,153,0.75)" if v >= 0 else "rgba(248,113,113,0.75)" for v in pnl_vals]

    wins  = sum(1 for v in pnl_vals if v > 0)
    total = len(pnl_vals)
    win_rate  = wins / total * 100 if total else 0
    avg_win   = np.mean([v for v in pnl_vals if v > 0]) if wins > 0 else 0
    avg_loss  = np.mean([v for v in pnl_vals if v < 0]) if total - wins > 0 else 0
    total_ret = equity_df["Equity"].iloc[-1] - 100
    max_dd    = 0.0
    peak      = equity_df["Equity"].iloc[0]
    for eq in equity_df["Equity"]:
        if eq > peak: peak = eq
        dd = (peak - eq) / peak * 100
        if dd > max_dd: max_dd = dd

    # ── Figure: 3 rows ──
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.10,
        subplot_titles=(
            f"📈 Equity Curve  (start=100)",
            f"📊 Per-Trade P&L %  ({total} trades · Win rate {win_rate:.0f}%)",
            f"🔀 Forward Price Curves  (entry=0%, {hold_bars}-bar hold)",
        ),
        row_heights=[0.38, 0.30, 0.32],
    )

    # ── Row 1: Equity curve ──
    eq_x = list(range(len(equity_df)))
    eq_y = equity_df["Equity"].tolist()
    # fill under/over 100
    fig.add_trace(go.Scatter(
        x=eq_x, y=eq_y,
        mode="lines+markers",
        line=dict(color="#38bdf8", width=2.2),
        marker=dict(size=7, color=["#fbbf24"] + bar_colors,
                    line=dict(color="white", width=0.8)),
        fill="tozeroy",
        fillcolor="rgba(56,189,248,0.06)",
        name="Equity",
        hovertemplate="Trade %{x}: ₹%{y:.1f}<extra></extra>",
    ), row=1, col=1)
    fig.add_hline(y=100, line_dash="dot", line_color="rgba(148,163,184,0.4)",
                  line_width=1, row=1, col=1)
    # annotate start & end
    fig.add_annotation(x=eq_x[-1], y=eq_y[-1],
                       text=f"<b>{eq_y[-1]:.1f}</b>",
                       font=dict(color="#38bdf8", size=11),
                       bgcolor="rgba(8,12,24,0.8)", bordercolor="#38bdf8",
                       borderwidth=1, showarrow=True, arrowcolor="#38bdf8",
                       ax=20, ay=-20, row=1, col=1)

    # ── Row 2: Per-trade P&L bars ──
    fig.add_trace(go.Bar(
        x=list(range(total)),
        y=pnl_vals,
        marker_color=bar_colors,
        marker_line_color="rgba(255,255,255,0.15)",
        marker_line_width=0.5,
        name="Trade P&L %",
        customdata=trade_labels,
        hovertemplate="<b>%{customdata}</b><br>P&L: %{y:+.2f}%<extra></extra>",
    ), row=2, col=1)
    fig.add_hline(y=0, line_dash="solid", line_color="rgba(148,163,184,0.3)",
                  line_width=1, row=2, col=1)
    # avg win/loss lines
    if avg_win:
        fig.add_hline(y=avg_win, line_dash="dot", line_color="rgba(52,211,153,0.5)",
                      annotation_text=f"Avg win {avg_win:+.2f}%",
                      annotation_font_color="#34d399",
                      annotation_position="right", row=2, col=1)
    if avg_loss:
        fig.add_hline(y=avg_loss, line_dash="dot", line_color="rgba(248,113,113,0.5)",
                      annotation_text=f"Avg loss {avg_loss:.2f}%",
                      annotation_font_color="#f87171",
                      annotation_position="right", row=2, col=1)

    # ── Row 3: Forward curves overlay ──
    palette = ["#38bdf8","#fbbf24","#34d399","#f87171","#a78bfa",
               "#fb923c","#f472b6","#4ade80","#60a5fa","#e879f9"]
    for ci, (offsets, fwd_pct, lbl) in enumerate(forward_curves):
        is_win = fwd_pct[-1] > 0
        clr = palette[ci % len(palette)]
        fig.add_trace(go.Scatter(
            x=offsets, y=fwd_pct,
            mode="lines",
            line=dict(color=clr, width=1.3),
            opacity=0.75,
            name=lbl,
            showlegend=True,
            hovertemplate=f"<b>{lbl}</b><br>Bar %{{x}}: %{{y:+.2f}}%<extra></extra>",
        ), row=3, col=1)
    # zero line
    fig.add_hline(y=0, line_dash="dot", line_color="rgba(148,163,184,0.4)",
                  line_width=1, row=3, col=1)
    # median curve
    if forward_curves:
        max_len = max(len(fc[1]) for fc in forward_curves)
        median_curve = []
        for b in range(max_len):
            vals_at_b = [fc[1][b] for fc in forward_curves if b < len(fc[1])]
            median_curve.append(float(np.median(vals_at_b)))
        fig.add_trace(go.Scatter(
            x=list(range(max_len)), y=median_curve,
            mode="lines",
            line=dict(color="white", width=2.5, dash="dash"),
            name="Median",
            hovertemplate="Median bar %{x}: %{y:+.2f}%<extra></extra>",
        ), row=3, col=1)

    # ── Stats annotation box ──
    stats_text = (
        f"<b>Strategy Backtest Summary</b><br>"
        f"Trades: {total}  |  Wins: {wins}  |  Losses: {total-wins}<br>"
        f"Win Rate: {win_rate:.0f}%  |  Avg Win: {avg_win:+.2f}%  |  Avg Loss: {avg_loss:.2f}%<br>"
        f"Total Return: {total_ret:+.1f}  |  Max Drawdown: {max_dd:.1f}%"
    )
    fig.add_annotation(
        x=0.01, y=0.99, xref="paper", yref="paper",
        text=stats_text,
        align="left", showarrow=False,
        font=dict(size=12, color="#dce8f5"),
        bgcolor="rgba(10,16,32,0.85)",
        bordercolor="#1a3050", borderwidth=1,
        xanchor="left", yanchor="top",
    )

    # ── Layout ──
    for ann in fig.layout.annotations:
        if hasattr(ann, "font") and ann.font:
            ann.font.color = "#b8d0e8"

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#080c18",
        plot_bgcolor="#0d1525",
        height=720,
        title=dict(
            text=f"<b>Strategy P&L Analysis</b>  ·  {strat_name}  ·  {hold_bars}-bar hold",
            font=dict(family="Syne", size=16, color="#dce8f5"), x=0.01,
        ),
        showlegend=True,
        legend=dict(
            orientation="h", x=0, y=-0.04,
            font=dict(size=12, color="#dce8f5"),
            bgcolor="rgba(10,14,26,0.88)",
            bordercolor="#2a3d55", borderwidth=1,
        ),
        margin=dict(l=10, r=60, t=55, b=10),
        font=dict(color="#94afd4"),
    )
    for r in range(1, 4):
        fig.update_xaxes(gridcolor="#111e30", row=r, col=1,
                         tickfont=dict(color="#8aabcb",size=11), zeroline=False)
        fig.update_yaxes(gridcolor="#111e30", row=r, col=1,
                         tickfont=dict(color="#8aabcb",size=11), zeroline=False)
    # row 1 x-axis: trade numbers
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(len(equity_df))),
        ticktext=["S"] + [str(i+1) for i in range(total)],
        row=1, col=1,
    )
    # row 2 x-axis: trade dates (short)
    fig.update_xaxes(
        tickmode="array",
        tickvals=list(range(total)),
        ticktext=[d[:6] for d in trade_labels],
        row=2, col=1,
    )
    # row 3 x-axis: bar offset
    fig.update_xaxes(title_text="Bars after entry", title_font=dict(color="#5a7898"),
                     row=3, col=1)
    fig.update_yaxes(title_text="% P&L", title_font=dict(color="#5a7898"), row=3, col=1)
    return fig, trades


# ─────────────────────────────────────────────────────────────────────────────
#  TRIGGER LOG DISPLAY  (now includes P&L chart)
# ─────────────────────────────────────────────────────────────────────────────
def render_trigger_log(df, bars, signal, strat_name, hold_bars=10, widget_key=""):
    """widget_key MUST be globally unique across all calls — pass symbol+strat_idx."""
    if not bars:
        st.markdown('<div class="ins-row">⚪ No triggers found in the loaded data.</div>',
                    unsafe_allow_html=True)
        return
    rows = []
    for i in bars:
        row = {
            "Date": df["Date"].iloc[i].strftime("%d %b %Y"),
            "Close ₹": f"{df['Close'].iloc[i]:,.2f}",
            "RSI": f"{df['RSI'].iloc[i]:.1f}" if "RSI" in df.columns and not np.isnan(df['RSI'].iloc[i]) else "-",
            "EMA9 ₹": f"{df['EMA_9'].iloc[i]:,.2f}" if "EMA_9" in df.columns and not np.isnan(df['EMA_9'].iloc[i]) else "-",
            "SMA14 ₹": f"{df['SMA_14'].iloc[i]:,.2f}" if "SMA_14" in df.columns and not np.isnan(df['SMA_14'].iloc[i]) else "-",
            "SMA20 ₹": f"{df['SMA_20'].iloc[i]:,.2f}" if "SMA_20" in df.columns and not np.isnan(df['SMA_20'].iloc[i]) else "-",
            "MACD": f"{df['MACD'].iloc[i]:.2f}" if "MACD" in df.columns and not np.isnan(df['MACD'].iloc[i]) else "-",
            "Vol Ratio": f"{df['Vol_Ratio'].iloc[i]:.2f}×" if "Vol_Ratio" in df.columns and not np.isnan(df['Vol_Ratio'].iloc[i]) else "-",
            "Signal": "🟢 BUY" if signal=="buy" else "🔴 SELL",
        }
        rows.append(row)
    log_df = pd.DataFrame(rows)
    st.dataframe(log_df, use_container_width=True, hide_index=True)
    st.markdown(f'<div class="ins-row">📊 Total triggers for <b>{strat_name}</b>: '
                f'<b style="color:#e8f4ff;">{len(bars)}</b> in the dataset</div>',
                unsafe_allow_html=True)

    # ── P&L Chart ──
    st.markdown('<div class="sec-title">📉 Strategy P&L Analysis</div>', unsafe_allow_html=True)

    # Build a guaranteed-unique slider key from widget_key (passed by caller)
    safe_key = re.sub(r"[^a-zA-Z0-9_]", "_", widget_key) if widget_key else \
               re.sub(r"[^a-zA-Z0-9_]", "_", f"hold_{strat_name[:12]}_{len(bars)}")

    h_col1, h_col2 = st.columns([1, 3])
    with h_col1:
        hold_bars = st.slider(
            "Hold period (bars)",
            min_value=1, max_value=30, value=hold_bars,
            key=safe_key,
            help="Number of bars to hold after entry signal before exiting"
        )

    result = build_pnl_chart(df, bars, signal, strat_name, hold_bars)
    if result:
        fig_pnl, trades = result

        # KPI row above chart
        pnl_vals = [float(t["P&L %"].replace("%","").replace("+","")) for t in trades]
        wins   = sum(1 for v in pnl_vals if v > 0)
        total  = len(pnl_vals)
        wr     = wins / total * 100 if total else 0
        avg_w  = np.mean([v for v in pnl_vals if v > 0]) if wins > 0 else 0
        avg_l  = np.mean([v for v in pnl_vals if v < 0]) if total - wins > 0 else 0
        net    = sum(pnl_vals)

        k1, k2, k3, k4, k5 = st.columns(5)
        kpis = [
            ("Total Trades", str(total),       "", "clr-neu"),
            ("Win Rate",     f"{wr:.0f}%",     f"{wins}W / {total-wins}L", "clr-up" if wr>=50 else "clr-dn"),
            ("Avg Win",      f"{avg_w:+.2f}%", "per trade", "clr-up"),
            ("Avg Loss",     f"{avg_l:.2f}%",  "per trade", "clr-dn"),
            ("Net P&L",      f"{net:+.2f}%",   "sum of all trades", "clr-up" if net>0 else "clr-dn"),
        ]
        for col, (lbl, val, delta, cls) in zip([k1,k2,k3,k4,k5], kpis):
            dh = f'<div class="metric-delta {cls}">{delta}</div>' if delta else ""
            col.markdown(f"""<div class="metric-card">
                <div class="metric-label">{lbl}</div>
                <div class="metric-value {cls}">{val}</div>{dh}
            </div>""", unsafe_allow_html=True)

        st.markdown("")
        st.plotly_chart(fig_pnl, use_container_width=True)

        # Trade detail table with coloring hint
        st.markdown('<div class="sec-title">🗒 Trade-by-Trade Results</div>', unsafe_allow_html=True)
        trade_df = pd.DataFrame(trades)
        st.dataframe(trade_df, use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  FORECAST  — Multi-Signal Ensemble (price-action anchored)
#
#  OLD problem: linear regression on FULL history drags forecast in the
#  direction of the long prior trend (e.g. a 9-month downtrend overrides
#  a current bullish signal, giving paradoxical "BUY but price goes down").
#
#  NEW approach — 5-component ensemble, all anchored to RECENT bars:
#   1. Short-term slope     : exp-weighted regression on last 20 bars only
#   2. Medium-term slope    : exp-weighted regression on last 50 bars
#   3. Signal-score bias    : composite buy/sell score shifts slope ±
#   4. RSI dampener         : overbought/oversold adjusts slope multiplier
#   5. EMA9 gravity         : mean-reversion pull back toward fast MA
#  Confidence bands use ATR (true volatility) × sqrt(time)
#  Hard clamp: forecast never deviates more than 3×ATR×sqrt(horizon) from LTP
# ─────────────────────────────────────────────────────────────────────────────
def forecast_prices(df, days, tf, signal_score=0):
    cl   = df["Close"].dropna().values
    n    = len(cl)
    freq = {"Daily":"B","Weekly":"W-FRI","Monthly":"MS"}[tf]
    fd   = pd.date_range(df["Date"].max() + timedelta(days=1), periods=days, freq=freq)
    last_price = cl[-1]

    # ── 1. SHORT-TERM MOMENTUM (last 20 bars, exponential weights) ──────────
    lb20     = min(20, n)
    rec20    = cl[-lb20:]
    x20      = np.arange(lb20)
    ew20     = np.exp(np.linspace(0, 1.1, lb20))
    c20      = np.polyfit(x20, rec20, 1, w=ew20)
    slope20  = c20[0] / last_price          # daily slope as fraction of price

    # ── 2. MEDIUM-TERM MOMENTUM (last 50 bars) ───────────────────────────────
    lb50     = min(50, n)
    rec50    = cl[-lb50:]
    x50      = np.arange(lb50)
    ew50     = np.exp(np.linspace(0, 0.8, lb50))
    c50      = np.polyfit(x50, rec50, 1, w=ew50)
    slope50  = c50[0] / last_price

    # Blend 70% recent + 30% medium
    blended  = 0.70 * slope20 + 0.30 * slope50

    # ── 3. SIGNAL-SCORE ADJUSTMENT (±0.02% per bar per score unit, capped) ──
    score_adj = np.clip(signal_score * 0.0002, -0.002, 0.002)

    # ── 4. RSI DAMPENER ──────────────────────────────────────────────────────
    rsi_ser = df["RSI"].dropna() if "RSI" in df.columns else pd.Series([50.0])
    rsi_val = rsi_ser.iloc[-1] if len(rsi_ser) > 0 else 50.0

    if   rsi_val >= 75:  rsi_mult = 0.35   # very overbought → heavily cap upside
    elif rsi_val >= 68:  rsi_mult = 0.65   # overbought → moderate cap
    elif rsi_val <= 25:  rsi_mult = 0.35   # very oversold → cap downside (bounce)
    elif rsi_val <= 32:  rsi_mult = 0.65   # oversold → moderate cap of downside
    else:                rsi_mult = 1.00

    # For oversold: dampen negative slope (support forming)
    if rsi_val <= 32 and blended < 0:
        effective = blended * rsi_mult + score_adj
    else:
        effective = blended * rsi_mult + score_adj

    # ── 5. EMA9 GRAVITY  (30% mean-reversion pull, decays over time) ─────────
    ema9_ser = df["EMA_9"].dropna() if "EMA_9" in df.columns else pd.Series([last_price])
    ema9_val = ema9_ser.iloc[-1] if len(ema9_ser) > 0 else last_price
    gravity_gap     = ema9_val - last_price
    gravity_per_bar = gravity_gap * 0.30 / max(days, 1)

    # ── 6. BUILD FORECAST ────────────────────────────────────────────────────
    forecast_vals = np.zeros(days)
    for i in range(days):
        momentum_part = last_price * ((1 + effective) ** (i + 1))
        gravity_part  = gravity_per_bar * (i + 1) * np.exp(-0.05 * i)
        forecast_vals[i] = momentum_part + gravity_part

    # ── 7. ATR-BASED CONFIDENCE BANDS ────────────────────────────────────────
    if "ATR" in df.columns and len(df["ATR"].dropna()) > 0:
        atr_val = df["ATR"].dropna().iloc[-1]
    else:
        lb_v  = min(20, n - 1)
        atr_val = np.std(np.diff(cl[-lb_v:])) if lb_v > 1 else cl[-1] * 0.01
    uncertainty = atr_val * np.sqrt(np.arange(1, days + 1))

    # ── 8. SANITY CLAMP (prevent wildly unrealistic swings) ──────────────────
    max_dev = atr_val * 3.0 * np.sqrt(days)
    forecast_vals = np.clip(forecast_vals,
                            last_price - max_dev,
                            last_price + max_dev)
    forecast_vals = np.maximum(forecast_vals, last_price * 0.50)   # price > 0

    meta = {
        "short_slope_pct":    slope20   * 100,
        "medium_slope_pct":   slope50   * 100,
        "blended_slope_pct":  blended   * 100,
        "effective_slope_pct":effective * 100,
        "rsi_mult": rsi_mult, "rsi_val": rsi_val,
        "score_adj_pct": score_adj * 100,
        "gravity_target": ema9_val,
        "atr_val": atr_val,
        "direction": "▲ Bullish" if effective > 0 else "▼ Bearish",
        "signal_score": signal_score,
    }
    return fd, forecast_vals, uncertainty, meta




# ─────────────────────────────────────────────────────────────────────────────
#  CHART
# ─────────────────────────────────────────────────────────────────────────────
def build_chart(df, symbol, builtin_strats, custom_strats_rendered, tf):
    fig=make_subplots(rows=4,cols=1,shared_xaxes=True,vertical_spacing=0.025,
                      row_heights=[0.50,0.17,0.17,0.16],
                      subplot_titles=("","MACD","RSI","Volume"))

    if {"Open","High","Low","Close"}.issubset(df.columns):
        fig.add_trace(go.Candlestick(
            x=df["Date"],open=df["Open"],high=df["High"],low=df["Low"],close=df["Close"],
            name="OHLC",
            increasing_line_color="#34d399",decreasing_line_color="#f87171",
            increasing_fillcolor="rgba(52,211,153,0.78)",
            decreasing_fillcolor="rgba(248,113,113,0.78)"),row=1,col=1)
    else:
        fig.add_trace(go.Scatter(x=df["Date"],y=df["Close"],
                                 line=dict(color="#38bdf8",width=1.8),name="Close"),row=1,col=1)

    if "BB_Upper" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"],y=df["BB_Upper"],
                                 line=dict(color="rgba(129,140,248,0.45)",width=1,dash="dot"),
                                 name="BB",showlegend=False),row=1,col=1)
        fig.add_trace(go.Scatter(x=df["Date"],y=df["BB_Lower"],fill="tonexty",
                                 fillcolor="rgba(129,140,248,0.05)",
                                 line=dict(color="rgba(129,140,248,0.45)",width=1,dash="dot"),
                                 name="BB Lower",showlegend=False),row=1,col=1)

    for col,clr,dash,lbl in [("EMA_9","#fbbf24","solid","EMA 9"),
                               ("SMA_14","#c084fc","dot","SMA 14"),
                               ("SMA_20","#38bdf8","solid","SMA 20"),
                               ("SMA_50","#fb923c","dash","SMA 50"),
                               ("SMA_200","#f472b6","longdash","SMA 200")]:
        if col in df.columns:
            fig.add_trace(go.Scatter(x=df["Date"],y=df[col],
                                     line=dict(color=clr,width=1.3,dash=dash),name=lbl),row=1,col=1)

    # Built-in strategy markers
    style_map={
        "S1A · RSI↑40 & Close > EMA9":("triangle-up","#34d399","1A"),
        "S1B · RSI↓60 & Close < EMA9":("triangle-down","#f87171","1B"),
        "S2 · RSI↑60 & Close > SMA14":("star","#fbbf24","S2"),
    }
    for s in builtin_strats:
        if not s["bars"]: continue
        sym_sh,clr,lbl=style_map.get(s["name"],("circle","#94a3b8","?"))
        xs=[df["Date"].iloc[i] for i in s["bars"]]
        ys=[df["Close"].iloc[i] for i in s["bars"]]
        tpos="top center" if s["signal"]=="buy" else "bottom center"
        fig.add_trace(go.Scatter(x=xs,y=ys,mode="markers+text",
                                 marker=dict(symbol=sym_sh,size=14,color=clr,
                                             line=dict(color="white",width=0.8)),
                                 text=[lbl]*len(xs),textposition=tpos,
                                 textfont=dict(size=8,color="#ffffff"),
                                 name=s["name"]),row=1,col=1)

    # Custom strategy markers
    custom_colors=["#a78bfa","#fb923c","#f472b6","#34d3d3","#facc15"]
    custom_syms_buy=["diamond","pentagon","hexagram","cross","bowtie"]
    custom_syms_sell=["diamond-open","pentagon-open","hexagram-open","cross-open","bowtie-open"]
    for ci,(cname,cbars,csig) in enumerate(custom_strats_rendered):
        if not cbars: continue
        clr=custom_colors[ci%len(custom_colors)]
        sym=custom_syms_buy[ci%len(custom_syms_buy)] if csig=="buy" else custom_syms_sell[ci%len(custom_syms_sell)]
        xs=[df["Date"].iloc[i] for i in cbars]
        ys=[df["Close"].iloc[i] for i in cbars]
        tpos="top center" if csig=="buy" else "bottom center"
        short=f"C{ci+1}"
        fig.add_trace(go.Scatter(x=xs,y=ys,mode="markers+text",
                                 marker=dict(symbol=sym,size=13,color=clr,
                                             line=dict(color="white",width=0.8)),
                                 text=[short]*len(xs),textposition=tpos,
                                 textfont=dict(size=8,color="#ffffff"),
                                 name=f"Custom: {cname[:20]}"),row=1,col=1)

    if "MACD" in df.columns:
        bc=["rgba(52,211,153,0.65)" if v>=0 else "rgba(248,113,113,0.65)"
            for v in df["MACD_Hist"].fillna(0)]
        fig.add_trace(go.Bar(x=df["Date"],y=df["MACD_Hist"],marker_color=bc,
                             name="Hist",showlegend=False),row=2,col=1)
        fig.add_trace(go.Scatter(x=df["Date"],y=df["MACD"],
                                 line=dict(color="#38bdf8",width=1.3),name="MACD"),row=2,col=1)
        fig.add_trace(go.Scatter(x=df["Date"],y=df["MACD_Signal"],
                                 line=dict(color="#fbbf24",width=1.3,dash="dot"),name="Signal"),row=2,col=1)

    if "RSI" in df.columns:
        fig.add_trace(go.Scatter(x=df["Date"],y=df["RSI"],
                                 line=dict(color="#a78bfa",width=1.6),name="RSI",
                                 fill="tozeroy",fillcolor="rgba(167,139,250,0.04)"),row=3,col=1)
        for lvl,clr2 in [(70,"rgba(248,113,113,0.5)"),(60,"rgba(251,191,36,0.4)"),
                         (40,"rgba(52,211,153,0.4)"),(30,"rgba(52,211,153,0.5)")]:
            fig.add_hline(y=lvl,line_dash="dot",line_color=clr2,line_width=1.2,row=3,col=1)
        fig.add_hrect(y0=60,y1=100,fillcolor="rgba(248,113,113,0.04)",line_width=0,row=3,col=1)
        fig.add_hrect(y0=0,y1=40,fillcolor="rgba(52,211,153,0.04)",line_width=0,row=3,col=1)

    if "Volume" in df.columns:
        vc=[]
        idx_list=list(df.index)
        for pos,i in enumerate(idx_list):
            pi=idx_list[pos-1] if pos>0 else i
            vc.append("rgba(52,211,153,0.55)" if df.loc[i,"Close"]>=df.loc[pi,"Close"]
                      else "rgba(248,113,113,0.55)")
        fig.add_trace(go.Bar(x=df["Date"],y=df["Volume"],marker_color=vc,
                             name="Vol",showlegend=False),row=4,col=1)
        if "Vol_SMA20" in df.columns:
            fig.add_trace(go.Scatter(x=df["Date"],y=df["Vol_SMA20"],
                                     line=dict(color="#fbbf24",width=1,dash="dot"),
                                     name="Vol MA",showlegend=False),row=4,col=1)

    for ann in fig.layout.annotations: ann.font.color="#b8d0e8"
    fig.update_layout(
        template="plotly_dark",paper_bgcolor="#080c18",plot_bgcolor="#0d1525",height=830,
        title=dict(text=f"<b>{symbol}</b>  ·  {tf} Chart",
                   font=dict(family="Syne",size=17,color="#dce8f5"),x=0.01),
        legend=dict(orientation="h",y=1.006,x=0,
                    font=dict(size=12,color="#dce8f5"),
                    bgcolor="rgba(10,14,26,0.88)",
                    bordercolor="#2a3d55",borderwidth=1),
        margin=dict(l=10,r=10,t=55,b=10),
        xaxis_rangeslider_visible=False,
        font=dict(color="#94afd4"),
    )
    for r in range(1,5):
        fig.update_xaxes(gridcolor="#111e30",row=r,col=1,tickfont=dict(color="#8aabcb",size=11))
        fig.update_yaxes(gridcolor="#111e30",row=r,col=1,tickfont=dict(color="#8aabcb",size=11))
    if "RSI" in df.columns:
        fig.update_yaxes(range=[0,100],row=3,col=1)
    return fig

def build_forecast_chart(df, fd, bv, unc, symbol, tf, meta=None):
    fig=go.Figure()

    # Historical line
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], name="Historical",
                             line=dict(color="#38bdf8", width=1.8)))

    # Confidence band
    fig.add_trace(go.Scatter(
        x=list(fd)+list(fd[::-1]),
        y=list(bv+2*unc)+list((bv-2*unc)[::-1]),
        fill="toself", fillcolor="rgba(129,140,248,0.11)",
        line=dict(color="rgba(0,0,0,0)"), name="95% Confidence"))

    # Forecast line colour driven by direction
    is_bull    = bv[-1] >= df["Close"].iloc[-1]
    fcast_clr  = "#34d399" if is_bull else "#f87171"
    fcast_lbl  = f"Forecast {'▲' if is_bull else '▼'}"

    fig.add_trace(go.Scatter(x=fd, y=bv, name=fcast_lbl,
                             line=dict(color=fcast_clr, width=2.4, dash="dash"),
                             mode="lines+markers",
                             marker=dict(size=6, color=fcast_clr,
                                         symbol="circle-open", line=dict(width=2))))

    # Bridge from last historical to first forecast
    fig.add_trace(go.Scatter(
        x=[df["Date"].iloc[-1], fd[0]],
        y=[df["Close"].iloc[-1], bv[0]],
        line=dict(color=fcast_clr, width=1.2, dash="dot"), showlegend=False))

    # Forecast endpoint annotation
    exp_pct = (bv[-1] / df["Close"].iloc[-1] - 1) * 100
    fig.add_annotation(
        x=fd[-1], y=bv[-1],
        text=f"<b>₹{bv[-1]:,.0f} ({exp_pct:+.1f}%)</b>",
        font=dict(size=11, color=fcast_clr),
        bgcolor="rgba(10,16,30,0.85)", bordercolor=fcast_clr, borderwidth=1,
        showarrow=True, arrowcolor=fcast_clr, ax=40, ay=-30,
    )

    # Model direction badge
    if meta:
        eff = meta.get("effective_slope_pct", 0)
        rsi_m = meta.get("rsi_mult", 1.0)
        badge_txt = f"Model: {meta.get('direction','?')}  |  slope {eff:+.3f}%/bar  |  RSI×{rsi_m:.2f}"
        badge_clr = "#34d399" if eff > 0 else "#f87171"
        fig.add_annotation(
            x=0.01, y=0.97, xref="paper", yref="paper",
            text=badge_txt, align="left", showarrow=False,
            font=dict(size=10, color=badge_clr),
            bgcolor="rgba(10,16,30,0.85)", bordercolor=badge_clr, borderwidth=1,
            xanchor="left", yanchor="top",
        )

    fig.update_layout(
        template="plotly_dark", paper_bgcolor="#080c18", plot_bgcolor="#0d1525", height=420,
        title=dict(text=f"<b>{symbol}</b>  ·  {tf} Forecast  (recent-anchored ensemble)",
                   font=dict(family="Syne", size=15, color="#dce8f5"), x=0.01),
        legend=dict(orientation="h", y=1.02, x=0,
                    font=dict(size=12, color="#dce8f5"),
                    bgcolor="rgba(10,14,26,0.88)", bordercolor="#2a3d55", borderwidth=1),
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis=dict(gridcolor="#111e30", tickfont=dict(color="#8aabcb", size=11)),
        yaxis=dict(gridcolor="#111e30", tickfont=dict(color="#8aabcb", size=11)),
        font=dict(color="#94afd4"),
    )
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  DEFAULT CUSTOM STRATEGIES (pre-loaded examples)
# ─────────────────────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────────────────────
#  PRO-TRADER STRATEGY LIBRARY  — 30 famous strategies used by professional
#  traders globally, expressed in the app's condition syntax
# ─────────────────────────────────────────────────────────────────────────────
PRO_STRATEGY_LIBRARY = {

    # ── TREND FOLLOWING ──────────────────────────────────────────────────────
    "Trend Following": {
        "Golden Cross": {
            "signal": "BUY",
            "desc": "SMA50 crosses above SMA200 — classic long-term uptrend signal used by institutional fund managers.",
            "used_by": "Warren Buffett style funds, momentum ETFs",
            "text": """Name: Golden Cross
Signal: BUY
Conditions:
SMA50 crosses_above SMA200
Close > SMA50
Vol_Ratio > 1.0"""
        },
        "Death Cross": {
            "signal": "SELL",
            "desc": "SMA50 crosses below SMA200 — institutional exit signal, often precedes bear markets.",
            "used_by": "Hedge funds, macro traders",
            "text": """Name: Death Cross
Signal: SELL
Conditions:
SMA50 crosses_below SMA200
Close < SMA50"""
        },
        "Trend Rider (EMA Stack)": {
            "signal": "BUY",
            "desc": "Price above EMA9 > SMA20 > SMA50 — all MAs aligned bullishly. Used by trend followers for high-probability entries.",
            "used_by": "Mark Minervini, William O'Neil",
            "text": """Name: Trend Rider EMA Stack
Signal: BUY
Conditions:
Close > EMA9
Close > SMA20
SMA20 > SMA50
RSI > 50"""
        },
        "Bearish EMA Stack": {
            "signal": "SELL",
            "desc": "All MAs aligned bearishly. Strong downtrend confirmation used by short sellers.",
            "used_by": "Short-side momentum traders",
            "text": """Name: Bearish EMA Stack
Signal: SELL
Conditions:
Close < EMA9
Close < SMA20
SMA20 < SMA50
RSI < 50"""
        },
        "Pullback to SMA20 (Uptrend)": {
            "signal": "BUY",
            "desc": "Price pulls back to SMA20 in an uptrend. Used by swing traders to buy the dip with trend intact.",
            "used_by": "IBD investors, CAN SLIM method",
            "text": """Name: Pullback to SMA20
Signal: BUY
Conditions:
Close > SMA50
SMA50 > SMA200
Close > SMA20
RSI > 40
RSI < 65"""
        },
    },

    # ── RSI STRATEGIES ───────────────────────────────────────────────────────
    "RSI Strategies": {
        "RSI Oversold Reversal": {
            "signal": "BUY",
            "desc": "RSI crosses above 30 from oversold. Classic Wilder RSI reversal — one of the most backtested signals.",
            "used_by": "J. Welles Wilder, swing traders worldwide",
            "text": """Name: RSI Oversold Reversal
Signal: BUY
Conditions:
RSI crosses_above 30
Close > EMA9"""
        },
        "RSI Overbought Exit": {
            "signal": "SELL",
            "desc": "RSI crosses below 70 from overbought. Exit or short signal when momentum exhausts.",
            "used_by": "Counter-trend traders, options sellers",
            "text": """Name: RSI Overbought Exit
Signal: SELL
Conditions:
RSI crosses_below 70
Close < EMA9"""
        },
        "RSI Momentum Breakout": {
            "signal": "BUY",
            "desc": "RSI crosses above 60 while price is above SMA14. Signals momentum entering bullish zone — used in trending markets.",
            "used_by": "Momentum traders, Minervini system",
            "text": """Name: RSI Momentum Breakout
Signal: BUY
Conditions:
RSI crosses_above 60
Close > SMA14
Close > SMA20"""
        },
        "RSI Mid-Line Cross (Bullish)": {
            "signal": "BUY",
            "desc": "RSI crosses above 50 — shift from bearish to bullish momentum. Simple but highly reliable trend change.",
            "used_by": "Connor RSI traders, quantitative systems",
            "text": """Name: RSI Mid-Line Bullish
Signal: BUY
Conditions:
RSI crosses_above 50
Close > SMA20
MACD > 0"""
        },
        "RSI Mid-Line Cross (Bearish)": {
            "signal": "SELL",
            "desc": "RSI crosses below 50 — momentum turning bearish.",
            "used_by": "Trend-following systems",
            "text": """Name: RSI Mid-Line Bearish
Signal: SELL
Conditions:
RSI crosses_below 50
Close < SMA20
MACD < 0"""
        },
    },

    # ── MACD STRATEGIES ──────────────────────────────────────────────────────
    "MACD Strategies": {
        "MACD Bullish Crossover": {
            "signal": "BUY",
            "desc": "MACD line crosses above signal line. Gerald Appel's original strategy — most widely used momentum signal.",
            "used_by": "Gerald Appel, institutional quants",
            "text": """Name: MACD Bullish Crossover
Signal: BUY
Conditions:
MACD crosses_above MACD_Signal
MACD < 0
Close > SMA20"""
        },
        "MACD Bearish Crossover": {
            "signal": "SELL",
            "desc": "MACD crosses below signal line — momentum turning down.",
            "used_by": "Momentum traders, trend followers",
            "text": """Name: MACD Bearish Crossover
Signal: SELL
Conditions:
MACD crosses_below MACD_Signal
MACD > 0
Close < SMA20"""
        },
        "MACD Zero-Line Cross (Bull)": {
            "signal": "BUY",
            "desc": "MACD crosses above zero — sustained bullish momentum confirmed. Stronger signal than signal-line cross.",
            "used_by": "System traders, Alexander Elder",
            "text": """Name: MACD Zero-Line Bull
Signal: BUY
Conditions:
MACD crosses_above 0
Close > SMA20
RSI > 50"""
        },
        "MACD + RSI Confluence": {
            "signal": "BUY",
            "desc": "Both MACD and RSI confirm bullish momentum simultaneously. Dual-indicator confluence increases accuracy.",
            "used_by": "Professional system traders",
            "text": """Name: MACD RSI Confluence Buy
Signal: BUY
Conditions:
MACD > MACD_Signal
RSI > 55
RSI < 70
Close > EMA9
Close > SMA20"""
        },
    },

    # ── BOLLINGER BAND + RSI STRATEGIES ──────────────────────────────────────
    # Complete 8-variant suite based on the classic BB+RSI combined approach:
    # (1) Price at band extremes + RSI confirmation = reversal signals
    # (2) Middle band crossover = entry confirmation
    # (3) BB squeeze + RSI momentum = breakout signals
    # (4) Band walk + RSI staying elevated = trend continuation
    # John Bollinger's core rule: "Tags of the bands are not signals — they need
    # RSI confirmation to become tradeable entries."
    "Bollinger Bands + RSI": {

        # ── SIGNAL 1: BB Lower Band Touch + RSI Oversold → BUY REVERSAL ──────
        "BB Lower + RSI Oversold Reversal": {
            "signal": "BUY",
            "desc": (
                "CORE BB+RSI SETUP (Reversal Buy): Price touches or pierces the lower Bollinger Band "
                "AND RSI is below 35 (oversold) — confirming the band touch is a genuine oversold "
                "extreme, not a trending market walking the band. "
                "Entry: when price closes back ABOVE the lower band. "
                "Target: middle band (SMA20). Stop: recent swing low below the lower band. "
                "John Bollinger's Rule: 'RSI must confirm the band tag — if RSI is not oversold when "
                "price hits the lower band, it is NOT a buy signal, it may be a breakdown.'"
            ),
            "used_by": "John Bollinger, mean-reversion traders, swing traders",
            "text": """Name: BB Lower + RSI Oversold Buy
Signal: BUY
Conditions:
Close < BB_Lower
RSI < 35
Vol_Ratio > 0.8"""
        },

        # ── SIGNAL 2: BB Lower Touch + RSI Oversold + MACD Confirming ────────
        "BB Lower + RSI + MACD Triple Confirm (Buy)": {
            "signal": "BUY",
            "desc": (
                "STRONGEST BB+RSI SETUP: Price at lower band, RSI oversold, AND MACD histogram "
                "turning positive or MACD crossing above signal line — triple confirmation. "
                "All three indicators must agree. Reduces false signals dramatically in trending markets. "
                "Best used in choppy/sideways markets where mean reversion works. "
                "Avoid this setup when SMA50 < SMA200 (downtrend — price can walk the lower band indefinitely)."
            ),
            "used_by": "Professional algo traders, TradingView strategy builders",
            "text": """Name: BB+RSI+MACD Triple Buy
Signal: BUY
Conditions:
Close < BB_Lower
RSI < 38
MACD > MACD_Signal
Vol_Ratio > 1.0"""
        },

        # ── SIGNAL 3: Price Crosses Back Above Lower BB (Entry Trigger) ───────
        "BB Lower Band Bounce — Middle Band Target": {
            "signal": "BUY",
            "desc": (
                "ENTRY TIMING SIGNAL: After price touches/pierces lower BB with RSI oversold, "
                "wait for price to cross back ABOVE the lower band — this is the actual entry candle. "
                "Target is the middle band (BB_Mid / SMA20). "
                "This avoids buying a falling knife — you enter only when bounce is confirmed. "
                "RSI < 45 ensures we're not entering an already-recovered situation."
            ),
            "used_by": "Swing traders, bounce traders",
            "text": """Name: BB Lower Bounce Entry Trigger
Signal: BUY
Conditions:
Close crosses_above BB_Lower
RSI < 45
Close < BB_Mid"""
        },

        # ── SIGNAL 4: Price Crosses Back Above Middle BB (Momentum Confirmed) ─
        "BB Middle Band Reclaim (Bull Confirmation)": {
            "signal": "BUY",
            "desc": (
                "MOMENTUM CONFIRMATION: Price crosses above the middle band (SMA20) after being below it, "
                "with RSI crossing above 50 — confirming the shift from bearish to bullish momentum. "
                "This is the second entry point in the BB+RSI system: "
                "First signal = lower band touch; Second signal = middle band reclaim. "
                "The middle band reclaim with RSI > 50 is a high-conviction trend-change signal."
            ),
            "used_by": "Trend-change traders, Alexander Elder",
            "text": """Name: BB Middle Band Reclaim Bull
Signal: BUY
Conditions:
Close crosses_above BB_Mid
RSI crosses_above 50
Vol_Ratio > 1.0"""
        },

        # ── SIGNAL 5: BB Upper Touch + RSI Overbought → SELL REVERSAL ─────────
        "BB Upper + RSI Overbought Reversal": {
            "signal": "SELL",
            "desc": (
                "CORE BB+RSI SETUP (Reversal Sell): Price touches or pierces the UPPER Bollinger Band "
                "AND RSI is above 65 (overbought) — confirming the band touch is an overextended extreme. "
                "Entry: when price closes back BELOW the upper band. "
                "Target: middle band (SMA20). Stop: recent swing high above the upper band. "
                "KEY RULE: If price is 'walking the upper band' (multiple closes above BB_Upper with RSI > 70), "
                "it is a STRONG TREND — do NOT sell. Only sell when RSI starts turning down from overbought."
            ),
            "used_by": "John Bollinger, counter-trend traders, options sellers",
            "text": """Name: BB Upper + RSI Overbought Sell
Signal: SELL
Conditions:
Close > BB_Upper
RSI > 65
MACD < MACD_Signal"""
        },

        # ── SIGNAL 6: BB Upper Rejection Candle ───────────────────────────────
        "BB Upper Band Rejection — Entry Trigger": {
            "signal": "SELL",
            "desc": (
                "SELL ENTRY TIMING: After price pierces upper band with RSI overbought, "
                "wait for price to cross back BELOW the upper band — actual sell entry. "
                "Target: middle band. Stop: recent high above the upper band. "
                "RSI > 60 confirms we were genuinely overbought before the rejection."
            ),
            "used_by": "Swing traders, short-side traders",
            "text": """Name: BB Upper Rejection Sell Trigger
Signal: SELL
Conditions:
Close crosses_below BB_Upper
RSI > 60
Close > BB_Mid"""
        },

        # ── SIGNAL 7: BB Squeeze Breakout (Volatility Expansion) + RSI ────────
        "BB Squeeze Breakout + RSI Momentum": {
            "signal": "BUY",
            "desc": (
                "VOLATILITY EXPANSION SIGNAL: The Bollinger Squeeze occurs when BB_Width narrows "
                "(bands tighten) — indicating a period of low volatility before a big move. "
                "When price breaks above the upper band with RSI in momentum zone (55-72), "
                "it signals the start of a bullish expansion phase. "
                "This is John Carter's famous Squeeze setup adapted with RSI filter. "
                "Volume surge (>1.5×) confirms institutional participation in the breakout."
            ),
            "used_by": "John Carter (Simpler Trading), volatility breakout traders",
            "text": """Name: BB Squeeze Breakout Bull
Signal: BUY
Conditions:
Close > BB_Upper
RSI > 55
RSI < 72
Vol_Ratio > 1.5
Close > SMA20"""
        },

        # ── SIGNAL 8: BB+RSI Trend Continuation (Walking the Upper Band) ──────
        "BB Upper Band Walk (Trend Continuation)": {
            "signal": "BUY",
            "desc": (
                "TREND CONTINUATION SIGNAL: In a strong uptrend, price 'walks' the upper Bollinger Band — "
                "repeatedly touching/closing near it. RSI stays elevated (60-80) without collapsing. "
                "This is NOT overbought — it is a sign of STRENGTH. Pullbacks to the middle band are buys. "
                "John Bollinger: 'Prices can walk up the upper band for extended periods in a strong trend — "
                "those who sell because they think it is overbought get run over.' "
                "Signal: Price holding above middle band with RSI in bullish zone and SMA20 > SMA50."
            ),
            "used_by": "Trend-following traders, momentum investors",
            "text": """Name: BB Upper Band Walk Buy
Signal: BUY
Conditions:
Close > BB_Mid
Close > SMA20
SMA20 > SMA50
RSI > 58
RSI < 80
MACD > MACD_Signal"""
        },
    },

    # ── VOLUME-BASED STRATEGIES ──────────────────────────────────────────────
    "Volume Strategies": {
        "Volume Breakout Bull": {
            "signal": "BUY",
            "desc": "Price breaks above SMA20 with surging volume. Volume confirms the breakout — O'Neil, Livermore principle.",
            "used_by": "Jesse Livermore, William O'Neil, CANSLIM",
            "text": """Name: Volume Breakout Bull
Signal: BUY
Conditions:
Close crosses_above SMA20
Vol_Ratio > 2.0
RSI > 50
RSI < 70"""
        },
        "Volume Dry-Up Accumulation": {
            "signal": "BUY",
            "desc": "Price holding up on falling volume — supply exhausted, smart money absorbing. Classic Wyckoff accumulation.",
            "used_by": "Richard Wyckoff, institutional traders",
            "text": """Name: Volume Dry-Up Accumulation
Signal: BUY
Conditions:
Vol_Ratio < 0.7
Close > SMA20
RSI > 40
RSI < 60"""
        },
        "Institutional Delivery Surge": {
            "signal": "BUY",
            "desc": "High delivery% with rising price — institutions accumulating, not speculators. NSE/BSE specific signal.",
            "used_by": "FII/DII tracking traders (India specific)",
            "text": """Name: Institutional Delivery Surge
Signal: BUY
Conditions:
Delivery > 55
Close > SMA20
Vol_Ratio > 1.3
RSI > 45"""
        },
        "Distribution Warning": {
            "signal": "SELL",
            "desc": "High volume with low delivery% — smart money selling to retail speculators. Distribution phase.",
            "used_by": "Wyckoff analysts, institutional watchers",
            "text": """Name: Distribution Warning
Signal: SELL
Conditions:
Vol_Ratio > 1.8
Delivery < 25
Close < EMA9"""
        },
    },

    # ── STOCHASTIC STRATEGIES ────────────────────────────────────────────────
    "Stochastic Strategies": {
        "Stochastic Oversold Bounce": {
            "signal": "BUY",
            "desc": "Stochastic K crosses above D from below 20. George Lane's original signal — high-probability reversal setup.",
            "used_by": "George Lane, options traders",
            "text": """Name: Stochastic Oversold Bounce
Signal: BUY
Conditions:
Stoch_K crosses_above Stoch_D
Stoch_K < 30
RSI < 45
Close > EMA9"""
        },
        "Stochastic Overbought Reversal": {
            "signal": "SELL",
            "desc": "Stochastic K crosses below D from above 80 — momentum reversal from overbought.",
            "used_by": "Swing traders, options traders",
            "text": """Name: Stochastic Overbought Reversal
Signal: SELL
Conditions:
Stoch_K crosses_below Stoch_D
Stoch_K > 70
RSI > 60"""
        },
    },

    # ── COMBINED / MULTI-INDICATOR ───────────────────────────────────────────
    "Multi-Indicator Combos": {
        "Triple Screen (Elder)": {
            "signal": "BUY",
            "desc": "Alexander Elder's triple screen: trend up (SMA50>SMA200) + weekly momentum + daily oversold entry.",
            "used_by": "Alexander Elder, professional traders",
            "text": """Name: Elder Triple Screen Buy
Signal: BUY
Conditions:
SMA50 > SMA200
MACD > MACD_Signal
RSI > 40
RSI < 65
Close > SMA20"""
        },
        "Supertrend Proxy (ATR Based)": {
            "signal": "BUY",
            "desc": "Price well above its ATR baseline with bullish momentum — mimics Supertrend indicator used by Indian retail traders.",
            "used_by": "Indian retail traders, Zerodha community",
            "text": """Name: Supertrend Proxy Buy
Signal: BUY
Conditions:
Close > SMA20
RSI > 55
MACD > MACD_Signal
Vol_Ratio > 1.2
Stoch_K > 50"""
        },
        "Minervini VCP (Trend Template)": {
            "signal": "BUY",
            "desc": "Mark Minervini's Trend Template: price above all MAs, MAs in bullish order, RS strong.",
            "used_by": "Mark Minervini, US Investing Champion",
            "text": """Name: Minervini Trend Template
Signal: BUY
Conditions:
Close > SMA50
Close > SMA200
SMA50 > SMA200
RSI > 60
Vol_Ratio > 1.0"""
        },
        "Power of Three (Smart Money)": {
            "signal": "BUY",
            "desc": "ICT concept: accumulation on pullback with volume confirmation and trend alignment.",
            "used_by": "ICT traders, smart money concepts",
            "text": """Name: Power of Three Buy
Signal: BUY
Conditions:
Close > SMA20
Close > EMA9
MACD > 0
Vol_Ratio > 1.3
Delivery > 45"""
        },
        "Breadth Thrust Proxy": {
            "signal": "BUY",
            "desc": "Strong momentum surge — RSI, MACD, volume all firing simultaneously. Rare but high-conviction setup.",
            "used_by": "Martin Zweig, momentum funds",
            "text": """Name: Breadth Thrust Buy
Signal: BUY
Conditions:
RSI > 60
RSI < 80
MACD > MACD_Signal
Vol_Ratio > 2.0
Close > SMA20
Delivery > 50"""
        },
    },

    # ── PRICE ACTION / SWING ─────────────────────────────────────────────────
    "Price Action & Swing": {
        "Inside Day Breakout": {
            "signal": "BUY",
            "desc": "Momentum expanding after consolidation, RSI building. Proxy for inside-day breakout with volume.",
            "used_by": "Price action traders, Al Brooks",
            "text": """Name: Consolidation Breakout
Signal: BUY
Conditions:
Close > SMA20
Vol_Ratio > 1.8
RSI crosses_above 55
MACD > MACD_Signal"""
        },
        "Momentum Continuation": {
            "signal": "BUY",
            "desc": "Strong trend continuation — price holds above EMA9, RSI stays in momentum zone (55-70).",
            "used_by": "Trend continuation traders",
            "text": """Name: Momentum Continuation
Signal: BUY
Conditions:
Close > EMA9
RSI > 55
RSI < 72
MACD > MACD_Signal
SMA20 > SMA50"""
        },
        "Reversal from Exhaustion": {
            "signal": "BUY",
            "desc": "Sharp decline exhausted: RSI oversold, Stochastic turning up, price near lower BB.",
            "used_by": "Reversal traders, counter-trend system",
            "text": """Name: Reversal from Exhaustion
Signal: BUY
Conditions:
RSI < 35
Stoch_K crosses_above Stoch_D
Close > BB_Lower
Vol_Ratio > 1.2"""
        },
        "Trend Breakdown Short": {
            "signal": "SELL",
            "desc": "Trend structure broken — price below all key MAs, MACD negative, RSI weak.",
            "used_by": "Swing traders, position traders",
            "text": """Name: Trend Breakdown Short
Signal: SELL
Conditions:
Close < SMA20
SMA20 < SMA50
RSI < 45
MACD < MACD_Signal
Vol_Ratio > 1.3"""
        },
    },
}

# Flat list for session state (all strategies, disabled by default except first)

# ─────────────────────────────────────────────────────────────────────────────
#  FUNDAMENTALS via yfinance
# ─────────────────────────────────────────────────────────────────────────────
def fetch_fundamentals(ticker: str) -> dict:
    if not YF_AVAILABLE:
        return {}
    try:
        t = yf.Ticker(ticker)
        inf = t.info or {}
        def g(k, fmt=None, default="N/A"):
            v = inf.get(k)
            if v is None or v == "": return default
            try:
                if fmt=="pct":  return f"{float(v)*100:.1f}%"
                if fmt=="B":    return f"${float(v)/1e9:,.1f}B" if float(v)>=1e9 else f"${float(v)/1e6:,.1f}M"
                if fmt=="2f":   return f"{float(v):.2f}"
                return str(v)
            except: return str(v)
        return {
            "Company": g("longName"), "Sector": g("sector"), "Industry": g("industry"),
            "Market Cap": g("marketCap","B"), "P/E (TTM)": g("trailingPE","2f"),
            "Forward P/E": g("forwardPE","2f"), "P/B Ratio": g("priceToBook","2f"),
            "EV/EBITDA": g("enterpriseToEbitda","2f"), "Beta": g("beta","2f"),
            "ROE": g("returnOnEquity","pct"), "ROA": g("returnOnAssets","pct"),
            "Profit Margin": g("profitMargins","pct"), "Operating Margin": g("operatingMargins","pct"),
            "Revenue (TTM)": g("totalRevenue","B"), "EPS (TTM)": g("trailingEps","2f"),
            "EPS Forward": g("forwardEps","2f"), "Revenue Growth": g("revenueGrowth","pct"),
            "Earnings Growth": g("earningsGrowth","pct"), "EBITDA": g("ebitda","B"),
            "Debt/Equity": g("debtToEquity","2f"), "Current Ratio": g("currentRatio","2f"),
            "Free Cash Flow": g("freeCashflow","B"), "Dividend Yield": g("dividendYield","pct"),
            "52W High": g("fiftyTwoWeekHigh","2f"), "52W Low": g("fiftyTwoWeekLow","2f"),
            "Analyst Target": g("targetMeanPrice","2f"), "Analyst Rec.": g("recommendationKey"),
            "_pe": inf.get("trailingPE"), "_pb": inf.get("priceToBook"),
            "_roe": inf.get("returnOnEquity"), "_dteq": inf.get("debtToEquity"),
            "_margin": inf.get("profitMargins"), "_target": inf.get("targetMeanPrice"),
            "_price": inf.get("currentPrice") or inf.get("regularMarketPrice"),
        }
    except Exception as e:
        return {"_error": str(e)}


def fundamental_score(fd: dict):
    score = 0; notes = []
    def safe_float(v):
        try: return float(v)
        except: return None

    pe = safe_float(fd.get("_pe"))
    if pe is not None:
        if pe < 0: notes.append("🔴 <b>P/E:</b> Negative — company is loss-making."); score -= 2
        elif pe < 15: notes.append(f"🟢 <b>P/E {pe:.1f}:</b> Value zone — potentially undervalued."); score += 2
        elif pe < 25: notes.append(f"🟡 <b>P/E {pe:.1f}:</b> Fairly valued."); score += 1
        elif pe > 40: notes.append(f"🔴 <b>P/E {pe:.1f}:</b> Expensive — high expectations priced in."); score -= 1

    roe = safe_float(fd.get("_roe"))
    if roe is not None:
        roe *= 100
        if roe >= 20: notes.append(f"🟢 <b>ROE {roe:.1f}%:</b> Excellent capital efficiency (Buffett benchmark ≥15%)."); score += 2
        elif roe >= 12: notes.append(f"🟡 <b>ROE {roe:.1f}%:</b> Acceptable profitability."); score += 1
        elif roe < 0: notes.append(f"🔴 <b>ROE {roe:.1f}%:</b> Negative — equity being destroyed."); score -= 2

    dteq = safe_float(fd.get("_dteq"))
    if dteq is not None:
        if dteq < 0.3: notes.append(f"🟢 <b>D/E {dteq:.2f}:</b> Low leverage — strong balance sheet."); score += 2
        elif dteq < 1.0: notes.append(f"🟡 <b>D/E {dteq:.2f}:</b> Manageable debt."); score += 1
        elif dteq > 2.5: notes.append(f"🔴 <b>D/E {dteq:.2f}:</b> High leverage — vulnerable to rate hikes."); score -= 2

    mgn = safe_float(fd.get("_margin"))
    if mgn is not None:
        mgn *= 100
        if mgn >= 20: notes.append(f"🟢 <b>Net Margin {mgn:.1f}%:</b> Excellent pricing power."); score += 2
        elif mgn >= 10: notes.append(f"🟡 <b>Net Margin {mgn:.1f}%:</b> Good profitability."); score += 1
        elif mgn < 0: notes.append(f"🔴 <b>Net Margin {mgn:.1f}%:</b> Loss-making."); score -= 2

    tgt = safe_float(fd.get("_target")); prc = safe_float(fd.get("_price"))
    if tgt and prc:
        upside = (tgt - prc) / prc * 100
        if upside >= 20: notes.append(f"🟢 <b>Analyst Target:</b> {upside:+.1f}% upside — strong conviction."); score += 2
        elif upside >= 8: notes.append(f"🟡 <b>Analyst Target:</b> {upside:+.1f}% moderate upside."); score += 1
        elif upside < 0: notes.append(f"🔴 <b>Analyst Target:</b> {upside:.1f}% downside — overvalued per consensus."); score -= 2

    return max(-10, min(10, score)), notes


# ─────────────────────────────────────────────────────────────────────────────
#  SUPPORT & RESISTANCE  — institutional multi-method
# ─────────────────────────────────────────────────────────────────────────────
def compute_sr_levels(df: pd.DataFrame, cl: float) -> dict:
    result = {"pivot":{}, "fib":{}, "swing_res":[], "swing_sup":[],
              "entry":cl, "stop_loss":cl*0.97, "targets":[cl*1.03, cl*1.06, cl*1.09],
              "risk_reward":1.0, "trade_bias":"NEUTRAL", "imm_resistance":cl*1.03,
              "imm_support":cl*0.97, "str_resistance":cl*1.06, "str_support":cl*0.94}
    n = len(df)
    last = df.iloc[-1]

    # Pivot
    if {"High","Low","Close"}.issubset(df.columns):
        h = last.get("High", cl); l = last.get("Low", cl); c = cl
        pp = (h+l+c)/3
        result["pivot"] = {"PP":pp,"R1":2*pp-l,"R2":pp+(h-l),"R3":h+2*(pp-l),
                           "S1":2*pp-h,"S2":pp-(h-l),"S3":l-2*(h-pp)}

    # Fibonacci from 52W
    lb = min(252, n)
    per = df.iloc[-lb:]
    hi52 = per["High"].max() if "High" in df.columns else per["Close"].max()
    lo52 = per["Low"].min()  if "Low"  in df.columns else per["Close"].min()
    rng  = hi52 - lo52
    if rng > 0:
        result["fib"] = {
            "100%": hi52, "78.6%": hi52-0.236*rng, "61.8%": hi52-0.382*rng,
            "50.0%": hi52-0.5*rng, "38.2%": hi52-0.618*rng,
            "23.6%": hi52-0.764*rng, "0%": lo52,
        }
        result["hi52"] = hi52; result["lo52"] = lo52

    # Swing levels
    cl_arr = df["Close"].values; w = 10
    swing_res = []; swing_sup = []
    for i in range(w, n-w):
        seg = cl_arr[i-w:i+w+1]
        if cl_arr[i] == max(seg) and cl_arr[i] > cl*1.002: swing_res.append(cl_arr[i])
        if cl_arr[i] == min(seg) and cl_arr[i] < cl*0.998: swing_sup.append(cl_arr[i])
    def dedup(lvls):
        out=[]
        for v in sorted(set(round(x,0) for x in lvls)):
            if not out or abs(v-out[-1])/out[-1]>0.005: out.append(v)
        return out
    result["swing_res"] = dedup(swing_res)[-5:]
    result["swing_sup"] = dedup(swing_sup)[:5]

    # ATR
    atr = last.get("ATR", cl*0.015)
    piv = result["pivot"]

    all_res = sorted([v for v in list(result["fib"].values()) + result["swing_res"] +
                      [piv.get("R1",cl*1.02), piv.get("R2",cl*1.04)] if v > cl*1.001],
                     key=lambda x: abs(x-cl))
    all_sup = sorted([v for v in list(result["fib"].values()) + result["swing_sup"] +
                      [piv.get("S1",cl*0.98), piv.get("S2",cl*0.96)] if v < cl*0.999],
                     key=lambda x: abs(x-cl))

    imm_r = all_res[0] if all_res else cl*1.03
    imm_s = all_sup[0] if all_sup else cl*0.97
    str_r = all_res[1] if len(all_res)>1 else cl*1.06
    str_s = all_sup[1] if len(all_sup)>1 else cl*0.94
    result.update({"imm_resistance":imm_r,"imm_support":imm_s,
                   "str_resistance":str_r,"str_support":str_s})

    bias = "BULLISH" if cl > piv.get("PP", cl) else "BEARISH"
    result["trade_bias"] = bias
    if bias == "BULLISH":
        result["entry"]     = cl
        result["stop_loss"] = round(max(imm_s - atr*0.5, cl*0.95), 1)
        result["targets"]   = [round(imm_r,1), round(str_r,1), round(piv.get("R3",cl*1.08),1)]
    else:
        result["entry"]     = cl
        result["stop_loss"] = round(min(imm_r + atr*0.5, cl*1.05), 1)
        result["targets"]   = [round(imm_s,1), round(str_s,1), round(piv.get("S3",cl*0.92),1)]

    risk   = abs(cl - result["stop_loss"])
    reward = abs(result["targets"][0] - cl) if result["targets"] else 0
    result["risk_reward"] = round(reward/risk, 2) if risk > 0 else 0
    return result


# ─────────────────────────────────────────────────────────────────────────────
#  OPTION CHAIN  — live via yfinance
# ─────────────────────────────────────────────────────────────────────────────
def fetch_option_chain(ticker: str, cl: float) -> dict:
    if not YF_AVAILABLE:
        return {"error": "yfinance not installed"}
    try:
        t = yf.Ticker(ticker)
        exps = t.options
        if not exps:
            return {"error": f"No options available for {ticker}"}
        exp = exps[0]
        chain = t.option_chain(exp)
        calls = chain.calls.copy(); puts = chain.puts.copy()
        if calls.empty or puts.empty:
            return {"error": "Option chain data empty"}
        for col in ["strike","openInterest","volume","lastPrice","impliedVolatility"]:
            for df_ in [calls, puts]:
                if col in df_.columns:
                    df_[col] = pd.to_numeric(df_[col], errors="coerce")
        calls.dropna(subset=["strike","openInterest"], inplace=True)
        puts.dropna(subset=["strike","openInterest"],  inplace=True)
        atm = calls.iloc[(calls["strike"]-cl).abs().argsort()[:1]]["strike"].values[0]
        total_call_oi = calls["openInterest"].sum(); total_put_oi = puts["openInterest"].sum()
        pcr_oi  = round(total_put_oi/total_call_oi, 2) if total_call_oi > 0 else np.nan
        pcr_vol = round(puts["volume"].sum()/calls["volume"].sum(), 2) if calls["volume"].sum()>0 else np.nan
        # Max pain
        strikes_all = sorted(set(list(calls["strike"].values)+list(puts["strike"].values)))
        pain = {}
        for s in strikes_all:
            cp = ((s-calls["strike"]).clip(lower=0)*calls["openInterest"].fillna(0)).sum()
            pp = ((puts["strike"]-s).clip(lower=0)*puts["openInterest"].fillna(0)).sum()
            pain[s] = cp + pp
        max_pain = min(pain, key=pain.get) if pain else atm
        # ATM IV
        atm_c = calls[calls["strike"]==atm]; atm_p = puts[puts["strike"]==atm]
        call_iv = round(atm_c["impliedVolatility"].values[0]*100,1) if not atm_c.empty else np.nan
        put_iv  = round(atm_p["impliedVolatility"].values[0]*100,1) if not atm_p.empty else np.nan
        iv_skew = round(put_iv - call_iv, 2) if not (np.isnan(put_iv) or np.isnan(call_iv)) else np.nan
        top_call = calls.nlargest(3,"openInterest")[["strike","openInterest","lastPrice","impliedVolatility"]]
        top_put  = puts.nlargest(3,"openInterest")[["strike","openInterest","lastPrice","impliedVolatility"]]
        # Chain display table
        nearby = calls[(calls["strike"]>=atm*0.88)&(calls["strike"]<=atm*1.12)]["strike"].values
        rows = []
        for s in sorted(nearby):
            cr = calls[calls["strike"]==s].iloc[0] if len(calls[calls["strike"]==s])>0 else pd.Series()
            pr = puts[puts["strike"]==s].iloc[0]   if len(puts[puts["strike"]==s])>0   else pd.Series()
            rows.append({"Call OI":int(cr.get("openInterest",0)) if not cr.empty else 0,
                         "Call Vol":int(cr.get("volume",0)) if not cr.empty else 0,
                         "Call LTP":round(cr.get("lastPrice",0),2) if not cr.empty else 0,
                         "Strike ₹":s, "ATM":"◀" if s==atm else "",
                         "Put LTP":round(pr.get("lastPrice",0),2) if not pr.empty else 0,
                         "Put Vol":int(pr.get("volume",0)) if not pr.empty else 0,
                         "Put OI":int(pr.get("openInterest",0)) if not pr.empty else 0})
        return {"expiry":exp,"atm":atm,"pcr_oi":pcr_oi,"pcr_vol":pcr_vol,
                "max_pain":max_pain,"call_iv":call_iv,"put_iv":put_iv,"iv_skew":iv_skew,
                "top_call_oi":top_call.to_dict("records"),"top_put_oi":top_put.to_dict("records"),
                "chain_df":pd.DataFrame(rows),"total_call_oi":int(total_call_oi),
                "total_put_oi":int(total_put_oi),"error":None}
    except Exception as e:
        return {"error": str(e)}


def build_oi_chart(oc: dict, symbol: str):
    if not oc or oc.get("error") or "chain_df" not in oc: return None
    df_ = oc["chain_df"]
    if df_.empty: return None
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_["Strike ₹"],y=df_["Call OI"],name="Call OI",
                         marker_color="rgba(248,113,113,0.75)"))
    fig.add_trace(go.Bar(x=df_["Strike ₹"],y=df_["Put OI"],name="Put OI",
                         marker_color="rgba(52,211,153,0.75)"))
    atm=oc["atm"]; mp=oc["max_pain"]
    fig.add_vline(x=atm,line_dash="dash",line_color="#38bdf8",
                  annotation_text=f"ATM ₹{atm:,.0f}",annotation_font_color="#38bdf8")
    fig.add_vline(x=mp,line_dash="dot",line_color="#fbbf24",
                  annotation_text=f"Max Pain ₹{mp:,.0f}",annotation_font_color="#fbbf24",
                  annotation_position="top right")
    fig.update_layout(
        template="plotly_dark",paper_bgcolor="#080c18",plot_bgcolor="#0d1525",
        height=360,barmode="group",
        title=dict(text=f"<b>{symbol}</b>  ·  Option Chain OI  ·  Expiry {oc['expiry']}",
                   font=dict(family="Syne",size=14,color="#dce8f5"),x=0.01),
        legend=dict(font=dict(size=12,color="#dce8f5"),bgcolor="rgba(10,14,26,0.88)",
                    bordercolor="#2a3d55",borderwidth=1),
        margin=dict(l=10,r=10,t=50,b=10),
        xaxis=dict(title="Strike ₹",gridcolor="#111e30",tickfont=dict(color="#8aabcb",size=11)),
        yaxis=dict(title="Open Interest",gridcolor="#111e30",tickfont=dict(color="#8aabcb",size=11)),
        font=dict(color="#94afd4"),
    )
    return fig


def render_institutional_report(df, symbol, ticker, cl, score, sig_data,
                                 sr, fd, oc, surge):
    st.markdown("---")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#0a0f1e,#0d1525);
                border:1px solid #1e3050;border-radius:14px;padding:1.2rem 1.6rem;margin-bottom:1rem;">
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                    background:linear-gradient(130deg,#38bdf8,#818cf8,#fb923c);
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            🏛 Institutional Analysis Report
        </div>
        <div style="font-size:0.7rem;color:#3d5270;letter-spacing:2px;text-transform:uppercase;margin-top:0.2rem;">
            Technical · Fundamental · Support/Resistance · Entry/Exit · Options
        </div>
    </div>""", unsafe_allow_html=True)

    rep_tabs = st.tabs(["📐 S/R & Entry/Exit", "🏦 Fundamentals", "⛓ Option Chain", "🏛 Verdict"])

    # ── S/R & ENTRY/EXIT ──────────────────────────────────────────────────────
    with rep_tabs[0]:
        st.markdown('<div class="sec-title">📐 Support, Resistance & Trade Setup</div>', unsafe_allow_html=True)
        bias=sr["trade_bias"]; entry=sr["entry"]; sl=sr["stop_loss"]
        tgts=sr["targets"];    rr=sr["risk_reward"]
        imm_r=sr.get("imm_resistance",cl*1.03); imm_s=sr.get("imm_support",cl*0.97)
        str_r=sr.get("str_resistance",cl*1.06);  str_s=sr.get("str_support",cl*0.94)
        bias_clr="#34d399" if bias=="BULLISH" else ("#f87171" if bias=="BEARISH" else "#8aa0c0")

        kc=st.columns(5)
        kpis_sr=[("Trade Bias",f"{'🟢' if bias=='BULLISH' else '🔴' if bias=='BEARISH' else '⚪'} {bias}",bias_clr),
                 ("Entry Zone",f"₹{entry:,.2f}","#dce8f5"),("Stop Loss",f"₹{sl:,.2f}","#f87171"),
                 ("Target 1",f"₹{tgts[0]:,.2f}" if tgts else "N/A","#34d399"),
                 ("Risk:Reward",f"1 : {rr}","#fbbf24" if rr>=2 else "#f87171")]
        for col_,(lbl_,val_,clr_) in zip(kc,kpis_sr):
            col_.markdown(f'<div class="metric-card"><div class="metric-label">{lbl_}</div>'
                          f'<div class="metric-value" style="font-size:1.1rem;color:{clr_};">{val_}</div></div>',
                          unsafe_allow_html=True)
        st.markdown("")

        lc1,lc2=st.columns(2)
        piv=sr.get("pivot",{})
        with lc1:
            st.markdown("**🔴 Resistance Levels**")
            res_rows=[]
            for lbl_,val_ in [("Imm. Resistance",imm_r),("Strong Resistance",str_r),
                               ("Pivot R1",piv.get("R1",np.nan)),("Pivot R2",piv.get("R2",np.nan)),
                               ("52W High",sr.get("hi52",np.nan)),
                               ("Fib 78.6%",sr["fib"].get("78.6%",np.nan) if sr.get("fib") else np.nan),
                               ("Fib 61.8%",sr["fib"].get("61.8%",np.nan) if sr.get("fib") else np.nan)]:
                try:
                    v=float(val_)
                    if not np.isnan(v) and v>cl:
                        res_rows.append({"Level":lbl_,"Price ₹":f"{v:,.2f}","% above CMP":f"+{(v/cl-1)*100:.2f}%"})
                except: pass
            if res_rows: st.dataframe(pd.DataFrame(res_rows),use_container_width=True,hide_index=True)

        with lc2:
            st.markdown("**🟢 Support Levels**")
            sup_rows=[]
            for lbl_,val_ in [("Imm. Support",imm_s),("Strong Support",str_s),("Stop Loss",sl),
                               ("Pivot S1",piv.get("S1",np.nan)),("Pivot S2",piv.get("S2",np.nan)),
                               ("52W Low",sr.get("lo52",np.nan)),
                               ("Fib 38.2%",sr["fib"].get("38.2%",np.nan) if sr.get("fib") else np.nan),
                               ("Fib 23.6%",sr["fib"].get("23.6%",np.nan) if sr.get("fib") else np.nan)]:
                try:
                    v=float(val_)
                    if not np.isnan(v) and v<cl:
                        sup_rows.append({"Level":lbl_,"Price ₹":f"{v:,.2f}","% below CMP":f"{(v/cl-1)*100:.2f}%"})
                except: pass
            if sup_rows: st.dataframe(pd.DataFrame(sup_rows),use_container_width=True,hide_index=True)

        # Trade Plan
        st.markdown('<div class="sec-title">📋 Institutional Trade Plan</div>', unsafe_allow_html=True)
        risk_amt=abs(cl-sl); tpcts=[(t/cl-1)*100 for t in tgts]
        if bias=="BULLISH":
            plan=f"""<div style="background:rgba(52,211,153,0.07);border:1px solid #34d399;border-radius:10px;padding:1rem 1.3rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:700;color:#34d399;font-size:0.95rem;margin-bottom:0.6rem;">🟢 LONG SETUP</div>
                <div style="font-size:0.82rem;line-height:1.9;color:#c4d4ea;">
                    <b style="color:#e8f4ff;">Entry:</b> ₹{entry:,.2f} (or pullback to ₹{imm_s:,.0f})<br>
                    <b style="color:#f87171;">Stop Loss:</b> ₹{sl:,.2f} ({((sl/cl-1)*100):+.2f}%)<br>
                    <b style="color:#34d399;">T1:</b> ₹{tgts[0]:,.2f} ({tpcts[0]:+.2f}%)
                    {'  <b style="color:#34d399;">T2:</b> ₹'+f'{tgts[1]:,.2f} ({tpcts[1]:+.2f}%)' if len(tgts)>1 else ''}
                    {'  <b style="color:#34d399;">T3:</b> ₹'+f'{tgts[2]:,.2f} ({tpcts[2]:+.2f}%)' if len(tgts)>2 else ''}<br>
                    <b style="color:#fbbf24;">R:R = 1:{rr}</b> {"✅ Good setup" if rr>=2 else "⚠️ Wait for better entry"} &nbsp;·&nbsp;
                    Position size = 2% capital / ₹{risk_amt:,.0f} risk per share
                </div></div>"""
        elif bias=="BEARISH":
            plan=f"""<div style="background:rgba(248,113,113,0.07);border:1px solid #f87171;border-radius:10px;padding:1rem 1.3rem;">
                <div style="font-family:'Syne',sans-serif;font-weight:700;color:#f87171;font-size:0.95rem;margin-bottom:0.6rem;">🔴 BEARISH — Avoid fresh longs</div>
                <div style="font-size:0.82rem;line-height:1.9;color:#c4d4ea;">
                    <b>Supports:</b> ₹{tgts[0]:,.2f} → ₹{tgts[1]:,.2f} (watch for bounce)<br>
                    <b>Stop for shorts:</b> ₹{sl:,.2f} ({((sl/cl-1)*100):+.2f}%)<br>
                    Wait for RSI &lt; 35 + support confirmation before entering long.
                </div></div>"""
        else:
            plan="""<div style="background:rgba(100,116,139,0.07);border:1px solid #475569;border-radius:10px;padding:1rem;color:#8aa0c0;">⚪ NEUTRAL — Wait for directional clarity</div>"""
        st.markdown(plan, unsafe_allow_html=True)

        # Fib chart
        if sr.get("fib"):
            ff=go.Figure()
            for lbl_,val_ in sorted(sr["fib"].items(),key=lambda x:x[1]):
                c_=("#34d399" if val_<cl else "#f87171")
                ff.add_hline(y=val_,line_dash="dot",line_color=c_,
                             annotation_text=f"{lbl_} ₹{val_:,.0f}",
                             annotation_font_color=c_,annotation_position="right")
            ff.add_hline(y=cl,line_dash="solid",line_color="#fbbf24",line_width=2,
                         annotation_text=f"CMP ₹{cl:,.0f}",annotation_font_color="#fbbf24",
                         annotation_position="right")
            ff.add_trace(go.Scatter(x=df["Date"].iloc[-60:],y=df["Close"].iloc[-60:],
                                    line=dict(color="#38bdf8",width=1.8),name="Price"))
            ff.update_layout(template="plotly_dark",paper_bgcolor="#080c18",plot_bgcolor="#0d1525",
                height=320,title=dict(text=f"<b>{symbol}</b>  ·  Fibonacci Levels (52W)",
                    font=dict(family="Syne",size=13,color="#dce8f5"),x=0.01),
                legend=dict(font=dict(size=12,color="#dce8f5"),bgcolor="rgba(10,14,26,0.88)"),
                margin=dict(l=10,r=110,t=45,b=10),
                xaxis=dict(gridcolor="#111e30",tickfont=dict(color="#8aabcb",size=10)),
                yaxis=dict(gridcolor="#111e30",tickfont=dict(color="#8aabcb",size=10)),
                font=dict(color="#94afd4"))
            st.plotly_chart(ff,use_container_width=True)

    # ── FUNDAMENTALS ─────────────────────────────────────────────────────────
    with rep_tabs[1]:
        st.markdown('<div class="sec-title">🏦 Fundamental Analysis</div>', unsafe_allow_html=True)
        if not fd or fd.get("_error"):
            st.markdown(f'<div class="ins-row">⚪ Fundamental data not available for <b>{symbol}</b>.<br>'
                        f'Use Yahoo Finance data source with a valid ticker (e.g. TCS.NS).<br>'
                        f'{"Error: "+fd.get("_error","") if fd and fd.get("_error") else ""}</div>',
                        unsafe_allow_html=True)
        else:
            fs,fn=fundamental_score(fd)
            fs_pct=(fs+10)/20*100; fs_clr="#34d399" if fs>3 else ("#f87171" if fs<-3 else "#fbbf24")
            fs_lbl="STRONG BUY" if fs>=6 else ("BUY" if fs>=3 else ("HOLD" if fs>=-2 else ("SELL" if fs>=-5 else "STRONG SELL")))
            comp=fd.get("Company",""); sect=fd.get("Sector",""); ind=fd.get("Industry","")
            st.markdown(f'<div style="margin-bottom:0.7rem;"><span style="font-family:Syne,sans-serif;font-size:1rem;font-weight:700;color:#dce8f5;">{comp}</span>'
                        f'{"<span style=color:#4a6a8a;font-size:0.73rem;> · "+sect+" · "+ind+"</span>" if sect else ""}</div>',
                        unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:#0c1828;border:1px solid #1a3050;border-radius:10px;padding:0.9rem 1.2rem;margin-bottom:0.7rem;">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.4rem;">
                    <span style="font-family:Syne,sans-serif;font-weight:700;color:{fs_clr};">Fundamental Score: {fs:+d}/10 — {fs_lbl}</span>
                    <span class="badge {'b-buy' if fs>=3 else 'b-sell' if fs<=-3 else 'b-neu'}">{fs_lbl}</span>
                </div>
                <div style="background:#0a1020;border-radius:6px;height:6px;overflow:hidden;">
                    <div style="width:{fs_pct:.0f}%;height:100%;background:{fs_clr};border-radius:6px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

            display_keys=[
                ("Valuation",   ["Market Cap","P/E (TTM)","Forward P/E","P/B Ratio","EV/EBITDA","Beta"]),
                ("Profitability",["ROE","ROA","Profit Margin","Operating Margin","EBITDA","Free Cash Flow"]),
                ("Growth",      ["Revenue (TTM)","EPS (TTM)","EPS Forward","Revenue Growth","Earnings Growth"]),
                ("Balance Sheet",["Debt/Equity","Current Ratio","Dividend Yield","52W High","52W Low","Analyst Target"]),
            ]
            for section_,keys_ in display_keys:
                st.markdown(f'<div style="font-size:0.73rem;color:#38bdf8;font-weight:700;margin:0.6rem 0 0.25rem;letter-spacing:1px;">{section_.upper()}</div>',
                            unsafe_allow_html=True)
                cols_=st.columns(6)
                for ci_,key_ in enumerate(keys_):
                    val_=fd.get(key_,"N/A")
                    cols_[ci_%6].markdown(f'<div class="metric-card" style="padding:0.5rem;"><div class="metric-label">{key_}</div>'
                                          f'<div style="font-family:Syne,sans-serif;font-size:0.88rem;font-weight:700;color:#e8f4ff;">{val_}</div></div>',
                                          unsafe_allow_html=True)

            st.markdown('<div class="sec-title">📋 Commentary</div>', unsafe_allow_html=True)
            for note in fn:
                brd_="#34d399" if "🟢" in note else ("#f87171" if "🔴" in note else "#fbbf24" if "🟠" in note else "#475569")
                st.markdown(f'<div class="ins-row" style="border-left:3px solid {brd_};">{note}</div>',unsafe_allow_html=True)

    # ── OPTION CHAIN ─────────────────────────────────────────────────────────
    with rep_tabs[2]:
        st.markdown('<div class="sec-title">⛓ Option Chain Analysis</div>', unsafe_allow_html=True)
        if not oc or oc.get("error"):
            err=oc.get("error","") if oc else ""
            st.markdown(f'<div class="ins-row">⚪ Options not available for <b>{symbol}</b>.<br>'
                        f'{"Reason: "+err+"<br>" if err else ""}'
                        f'Options data requires Yahoo Finance source with NSE tickers (e.g. TCS.NS).</div>',
                        unsafe_allow_html=True)
        else:
            atm=oc["atm"]; pcr_oi=oc["pcr_oi"]; mp=oc["max_pain"]
            iv_skew=oc["iv_skew"]; exp_=oc["expiry"]
            if not np.isnan(pcr_oi):
                if pcr_oi>1.5: ps="🟢 BULLISH — put writers dominating"; pc="#34d399"
                elif pcr_oi>1.0: ps="🟡 MILDLY BULLISH"; pc="#fbbf24"
                elif pcr_oi>0.7: ps="⚪ NEUTRAL"; pc="#8aa0c0"
                elif pcr_oi>0.5: ps="🟠 MILDLY BEARISH"; pc="#fb923c"
                else: ps="🔴 BEARISH — call writers dominating"; pc="#f87171"
            else: ps="N/A"; pc="#8aa0c0"

            oc_cols=st.columns(5)
            for col_,(lbl_,val_,clr_) in zip(oc_cols,[
                ("Expiry",exp_,"#dce8f5"),("ATM",f"₹{atm:,.0f}","#38bdf8"),
                ("PCR (OI)",f"{pcr_oi:.2f}" if not np.isnan(pcr_oi) else "N/A",pc),
                ("Max Pain",f"₹{mp:,.0f}","#fbbf24"),
                ("IV Skew",f"{iv_skew:+.1f}%" if iv_skew and not np.isnan(iv_skew) else "N/A",
                 "#f87171" if (iv_skew and not np.isnan(iv_skew) and iv_skew>2) else "#34d399")]):
                col_.markdown(f'<div class="metric-card"><div class="metric-label">{lbl_}</div>'
                              f'<div class="metric-value" style="font-size:1rem;color:{clr_};">{val_}</div></div>',
                              unsafe_allow_html=True)
            st.markdown("")
            st.markdown(f'<div class="ins-row" style="border-left:3px solid {pc};">📊 <b>PCR Signal:</b> {ps} | OI Ratio: {pcr_oi:.2f if isinstance(pcr_oi,float) else "N/A"}</div>',
                        unsafe_allow_html=True)

            oi_fig=build_oi_chart(oc,symbol)
            if oi_fig: st.plotly_chart(oi_fig,use_container_width=True)

            oa,ob=st.columns(2)
            with oa:
                st.markdown("**🔴 Top Call OI — Resistance**")
                for row in oc.get("top_call_oi",[]):
                    s_=row.get("strike",0)
                    st.markdown(f'<div class="ins-row" style="border-left:3px solid #f87171;">🔴 <b>₹{s_:,.0f}</b> — {int(row.get("openInterest",0)):,} call contracts. Call writers defend this level.</div>',
                                unsafe_allow_html=True)
            with ob:
                st.markdown("**🟢 Top Put OI — Support**")
                for row in oc.get("top_put_oi",[]):
                    s_=row.get("strike",0)
                    st.markdown(f'<div class="ins-row" style="border-left:3px solid #34d399;">🟢 <b>₹{s_:,.0f}</b> — {int(row.get("openInterest",0)):,} put contracts. Put writers defend this level.</div>',
                                unsafe_allow_html=True)

            mp_diff=(mp-cl)/cl*100
            st.markdown(f'<div class="ins-row" style="border-left:3px solid #fbbf24;">🎯 <b>Max Pain ₹{mp:,.0f}</b> ({mp_diff:+.2f}% from CMP). Option writers lose least here at expiry. Price tends to gravitate toward Max Pain as expiry approaches.</div>',
                        unsafe_allow_html=True)

            with st.expander("📊 Full Option Chain Table"):
                cdf_=oc.get("chain_df",pd.DataFrame())
                if not cdf_.empty: st.dataframe(cdf_,use_container_width=True,hide_index=True)

    # ── VERDICT ───────────────────────────────────────────────────────────────
    with rep_tabs[3]:
        st.markdown('<div class="sec-title">🏛 Institutional Verdict</div>', unsafe_allow_html=True)
        tech_b="BULLISH" if score>=3 else ("BEARISH" if score<=-3 else "NEUTRAL")
        fs_,_=fundamental_score(fd) if fd and not fd.get("_error") else (0,[])
        fund_b="BULLISH" if fs_>=3 else ("BEARISH" if fs_<=-3 else "NEUTRAL")
        surge_b=surge.get("direction","neutral").upper() if surge.get("has_data") else "NEUTRAL"
        sr_b=sr.get("trade_bias","NEUTRAL")
        pcr_b="NEUTRAL"
        if oc and not oc.get("error"):
            p_=oc.get("pcr_oi",1.0)
            if p_ and not np.isnan(p_): pcr_b="BULLISH" if p_>1.2 else ("BEARISH" if p_<0.8 else "NEUTRAL")
        def bs(b): return 1 if b=="BULLISH" else (-1 if b=="BEARISH" else 0)
        comp_=bs(tech_b)*3+bs(fund_b)*2+bs(surge_b)*2+bs(sr_b)*2+bs(pcr_b)*1
        comp_n=max(-10,min(10,comp_))
        if comp_n>=6: fv="STRONG BUY"; fc="#34d399"
        elif comp_n>=3: fv="BUY"; fc="#34d399"
        elif comp_n<=-6: fv="STRONG SELL"; fc="#f87171"
        elif comp_n<=-3: fv="SELL"; fc="#f87171"
        else: fv="HOLD / WATCH"; fc="#fbbf24"
        cp_=(comp_n+10)/20*100
        st.markdown(f"""
        <div style="background:linear-gradient(145deg,#0f1929,#152035);border:2px solid {fc};
                    border-radius:14px;padding:1.5rem 2rem;text-align:center;margin-bottom:1rem;">
            <div style="font-family:'Syne',sans-serif;font-size:2rem;font-weight:800;color:{fc};">{fv}</div>
            <div style="font-size:0.78rem;color:#8aa0c0;margin-top:0.3rem;">Composite Score: {comp_n:+d}/10</div>
            <div style="background:#0a1020;border-radius:8px;height:10px;margin:0.8rem 0;overflow:hidden;">
                <div style="width:{cp_:.0f}%;height:100%;background:{fc};border-radius:8px;"></div>
            </div>
        </div>""", unsafe_allow_html=True)

        for sig_n,sig_b in [("Technical (RSI·MACD·BB·MA)",tech_b),
                              ("Fundamentals (PE·ROE·D/E)",fund_b),
                              ("Surge (Price·Vol·Delivery)",surge_b),
                              ("S/R & Pivot Bias",sr_b),
                              ("Option PCR Signal",pcr_b)]:
            sc_=("#34d399" if sig_b=="BULLISH" else "#f87171" if sig_b=="BEARISH" else "#8aa0c0")
            si_=("🟢" if sig_b=="BULLISH" else "🔴" if sig_b=="BEARISH" else "⚪")
            st.markdown(f'<div class="ins-row" style="border-left:4px solid {sc_};">'
                        f'<b style="color:#e8f4ff;">{sig_n}</b> &nbsp;<span style="color:{sc_};">{si_} {sig_b}</span></div>',
                        unsafe_allow_html=True)

        st.markdown('<div class="sec-title">🎯 Final Entry/Exit</div>', unsafe_allow_html=True)
        t1=f"₹{sr['targets'][0]:,.2f} ({(sr['targets'][0]/cl-1)*100:+.2f}%)" if sr.get("targets") else "N/A"
        t2=f"₹{sr['targets'][1]:,.2f} ({(sr['targets'][1]/cl-1)*100:+.2f}%)" if len(sr.get("targets",[]))>1 else "N/A"
        t3=f"₹{sr['targets'][2]:,.2f} ({(sr['targets'][2]/cl-1)*100:+.2f}%)" if len(sr.get("targets",[]))>2 else "N/A"
        st.markdown(f"""
        <div style="background:#0c1828;border:1px solid #1a3050;border-radius:10px;padding:1.1rem 1.4rem;">
            <table style="width:100%;font-size:0.82rem;border-collapse:collapse;">
                <tr><td style="color:#4a6a8a;padding:0.25rem 0;">📍 CMP</td><td style="color:#e8f4ff;font-weight:700;">₹{cl:,.2f}</td></tr>
                <tr><td style="color:#4a6a8a;padding:0.25rem 0;">🎯 Entry</td><td style="color:#38bdf8;font-weight:700;">₹{sr['entry']:,.2f}</td></tr>
                <tr><td style="color:#4a6a8a;padding:0.25rem 0;">🛡 Stop Loss</td><td style="color:#f87171;font-weight:700;">₹{sr['stop_loss']:,.2f} ({((sr['stop_loss']/cl-1)*100):+.2f}%)</td></tr>
                <tr><td style="color:#4a6a8a;padding:0.25rem 0;">🟢 Target 1</td><td style="color:#34d399;font-weight:700;">{t1}</td></tr>
                <tr><td style="color:#4a6a8a;padding:0.25rem 0;">🟢 Target 2</td><td style="color:#34d399;font-weight:700;">{t2}</td></tr>
                <tr><td style="color:#4a6a8a;padding:0.25rem 0;">🟢 Target 3</td><td style="color:#34d399;font-weight:700;">{t3}</td></tr>
                <tr><td style="color:#4a6a8a;padding:0.25rem 0;">⚖ R:R</td><td style="color:{'#34d399' if sr['risk_reward']>=2 else '#fbbf24'};font-weight:700;">1 : {sr['risk_reward']}</td></tr>
                <tr><td style="color:#4a6a8a;padding:0.25rem 0;">💡 Options</td><td style="color:#dce8f5;">{"PCR "+str(oc.get('pcr_oi','N/A'))+" · Max Pain ₹"+f"{oc.get('max_pain',0):,.0f}" if oc and not oc.get('error') else "Fetch options data for OC signals"}</td></tr>
            </table>
        </div>""", unsafe_allow_html=True)
        st.markdown('<div style="font-size:0.68rem;color:#2d4060;margin-top:0.5rem;">⚠️ Educational only. Not financial advice.</div>',
                    unsafe_allow_html=True)


def _library_to_flat():
    flat = []
    for category, strats in PRO_STRATEGY_LIBRARY.items():
        for name, meta in strats.items():
            flat.append({
                "text": meta["text"],
                "enabled": False,
                "category": category,
                "desc": meta["desc"],
                "used_by": meta["used_by"],
            })
    return flat

ALL_LIBRARY_STRATEGIES = _library_to_flat()

DEFAULT_CUSTOM_STRATEGIES = [
    {
        "text": """Name: MACD Bull + Volume
Signal: BUY
Conditions:
MACD > MACD_Signal
Close > SMA20
Vol_Ratio > 1.2""",
        "enabled": True,
        "category": "Custom",
        "desc": "MACD bullish with above-average volume.",
        "used_by": "Custom",
    },
]



# ─────────────────────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    st.markdown('<p class="main-header">⚡ ProTrader Intelligence</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Indicator-Driven Signals · Custom Strategy Builder · Trigger Log · Forecast</p>',
                unsafe_allow_html=True)

    # ── Session state for strategies ──
    if "custom_strategies" not in st.session_state:
        st.session_state.custom_strategies = [s.copy() for s in DEFAULT_CUSTOM_STRATEGIES]
    if "library_strategies" not in st.session_state:
        st.session_state.library_strategies = [s.copy() for s in ALL_LIBRARY_STRATEGIES]

    with st.sidebar:
        st.markdown("### 📂 Data Source")

        data_source = st.radio("Choose data source:",
                               ["📁 Upload CSV", "🌐 Yahoo Finance"], index=0,
                               key="data_source")
        st.markdown("---")

        uploaded = []
        yahoo_data = {}   # symbol → raw df

        if data_source == "📁 Upload CSV":
            uploaded = st.file_uploader("NSE/BSE daily export — one or multiple",
                                        type=["csv"], accept_multiple_files=True)

        else:  # Yahoo Finance
            if not YF_AVAILABLE:
                st.warning("Install yfinance first:\n```\npip install yfinance\n```")
            else:
                st.markdown("**Ticker symbols** (one per line)")
                st.markdown('<span style="font-size:0.7rem;color:#4a6a8a;">NSE: `TCS.NS` · BSE: `TCS.BO` · US: `AAPL` · Nifty: `^NSEI`</span>',
                            unsafe_allow_html=True)
                ticker_input = st.text_area("Tickers:", value="TCS.NS\nRELIANCE.NS",
                                            height=100, key="yf_tickers")
                col_s, col_e = st.columns(2)
                with col_s:
                    start_date = st.date_input("From", value=datetime(2023,1,1),
                                               key="yf_start")
                with col_e:
                    end_date = st.date_input("To", value=datetime.today(),
                                             key="yf_end")
                if st.button("⬇️ Fetch Data", key="yf_fetch"):
                    tickers = [t.strip().upper() for t in ticker_input.splitlines() if t.strip()]
                    with st.spinner("Fetching from Yahoo Finance..."):
                        for t in tickers:
                            raw_yf = fetch_yahoo(t,
                                                 start_date.strftime("%Y-%m-%d"),
                                                 end_date.strftime("%Y-%m-%d"))
                            if raw_yf is not None:
                                yahoo_data[t] = raw_yf
                                st.success(f"✅ {t}: {len(raw_yf)} bars")
                            else:
                                st.error(f"❌ {t}: failed")
                    st.session_state["yahoo_data"] = yahoo_data

                # Restore from session state between reruns
                if "yahoo_data" in st.session_state:
                    yahoo_data = st.session_state["yahoo_data"]
                    if yahoo_data:
                        st.markdown(f'<div class="ins-row" style="font-size:0.73rem;">Loaded: {", ".join(yahoo_data.keys())}</div>',
                                    unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### ⏱ Timeframe")
        tf = st.radio("Chart timeframe", ["Daily","Weekly","Monthly"], index=0)
        st.markdown("---")
        default_days = {"Daily":10,"Weekly":8,"Monthly":6}[tf]
        forecast_days = st.slider("Forecast horizon (bars)", 5, 30, default_days)
        st.markdown("---")
        st.markdown('<span style="font-size:0.68rem;color:#2d4060;">⚠️ Educational use only. Not financial advice.</span>',
                    unsafe_allow_html=True)

    # ── Check if we have any data ──────────────────────────────────────────────
    has_csv   = bool(uploaded)
    has_yahoo = bool(yahoo_data)

    if not has_csv and not has_yahoo:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;border:1px dashed #1a2d45;
                    border-radius:16px;margin-top:2rem;">
            <div style="font-size:3.5rem;">📊</div>
            <h3 style="font-family:'Syne',sans-serif;color:#3d5a7a;">Choose a data source to begin</h3>
            <p style="color:#243550;font-size:0.83rem;">
                Upload NSE/BSE CSV  <b>or</b>  fetch live data from Yahoo Finance
            </p>
        </div>""", unsafe_allow_html=True)
        return

    # ── Parse files ──
    stock_data = {}

    # From CSV uploads
    for f in uploaded:
        raw = parse_csv(f)
        if raw is None: continue
        sym = raw["Symbol"].iloc[0] if "Symbol" in raw.columns else f.name.replace(".csv","")
        df  = resample_df(raw, tf)
        df  = add_indicators(df)
        stock_data[sym] = df

    # From Yahoo Finance
    for sym, raw_yf in yahoo_data.items():
        df_yf = resample_df(raw_yf, tf)
        df_yf = add_indicators(df_yf)
        stock_data[sym] = df_yf

    if not stock_data:
        st.error("Could not parse any files."); return

    # ── Tabs ──
    tab_labels=[f"📈 {s}" for s in stock_data]
    extra_tabs=["📊 DMA Analysis", "🛠 Strategy Builder"]
    if len(stock_data)>1: extra_tabs.append("📋 Comparison")
    tabs=st.tabs(tab_labels + extra_tabs)

    all_sum=[]

    for idx,(symbol,df) in enumerate(stock_data.items()):
        with tabs[idx]:
            last=df.iloc[-1]; prev=df.iloc[-2] if len(df)>1 else last
            cl=last["Close"]
            chg=cl-prev["Close"]; chgp=chg/prev["Close"]*100 if prev["Close"] else 0
            sig_data=generate_signals(df)
            builtin_strats=run_builtin_strategies(df)

            # Run enabled custom strategies
            custom_rendered=[]
            all_active_strats = (
                list(st.session_state.custom_strategies) +
                list(st.session_state.library_strategies)
            )
            for cs in all_active_strats:
                if not cs.get("enabled", False): continue
                parsed = parse_custom_strategy(cs["text"])
                bars   = run_custom_strategy(df, parsed)
                custom_rendered.append((parsed["name"], bars, parsed["signal"]))

            # ── Surge analysis (always on raw daily-equivalent data) ──
            surge = surge_analysis(df, lookback=15)

            # Timeframe pill
            tf_clr={"Daily":"#38bdf8","Weekly":"#a78bfa","Monthly":"#fb923c"}[tf]
            st.markdown(f"""
            <div style="display:inline-block;padding:0.2rem 0.9rem;border-radius:20px;
                        border:1px solid {tf_clr};font-size:0.68rem;
                        letter-spacing:2px;text-transform:uppercase;margin-bottom:0.7rem;">
                <span style="color:{tf_clr} !important;">⏱ {tf} · {len(df)} bars ·
                {df['Date'].min().strftime('%d %b %Y')} → {df['Date'].max().strftime('%d %b %Y')}</span>
            </div>""", unsafe_allow_html=True)

            # KPI row
            cols=st.columns(6)
            e9=last.get("EMA_9",np.nan); s14=last.get("SMA_14",np.nan)
            s20=last.get("SMA_20",np.nan); s50=last.get("SMA_50",np.nan)
            s200=last.get("SMA_200",np.nan)
            kpis=[
                ("LTP",      f"₹{cl:,.2f}",                 f"{'▲' if chg>=0 else '▼'} {chgp:+.2f}%","clr-up" if chg>=0 else "clr-dn"),
                ("Open",     f"₹{last.get('Open',0):,.2f}", "","clr-neu"),
                ("High",     f"₹{last.get('High',0):,.2f}", "","clr-up"),
                ("Low",      f"₹{last.get('Low',0):,.2f}",  "","clr-dn"),
                ("RSI",      f"{last.get('RSI',0):.1f}",    ">70 OB · <30 OS","clr-neu"),
                ("Delivery%",f"{last.get('Delivery%',0):.1f}%","Institutional strength","clr-neu"),
            ]
            for col,(lbl,val,delta,cls) in zip(cols,kpis):
                dh=f'<div class="metric-delta {cls}">{delta}</div>' if delta else ""
                col.markdown(f"""<div class="metric-card">
                    <div class="metric-label">{lbl}</div>
                    <div class="metric-value">{val}</div>{dh}
                </div>""", unsafe_allow_html=True)

            st.markdown("")

            # ── 50/200 DMA Trend Indicator ────────────────────────────────────
            dma_valid = not (np.isnan(s50) or np.isnan(s200))
            if dma_valid:
                dma_gap    = ((s50 - s200) / s200 * 100)
                dma_up     = s50 > s200
                dma_cls    = "v-buy" if dma_up else "v-sell"
                dma_badge  = "b-buy" if dma_up else "b-sell"
                dma_icon   = "🟢" if dma_up else "🔴"
                dma_label  = "BULL TREND — 50 DMA above 200 DMA" if dma_up else "BEAR TREND — 50 DMA below 200 DMA"
                dma_detail = (f"SMA50 ₹{s50:,.2f}  ·  SMA200 ₹{s200:,.2f}  ·  Gap {dma_gap:+.2f}%  ·  "
                              f"{'Golden Cross zone — long-term uptrend confirmed.' if dma_up else 'Death Cross zone — long-term downtrend confirmed.'}")
                st.markdown(f"""
                <div class="verdict-banner {dma_cls}" style="margin-bottom:0.3rem;">
                    <span class="badge {dma_badge}">DMA TREND</span>
                    <span style="font-family:'Syne',sans-serif;font-size:0.9rem;color:#dce8f5;">
                        {dma_icon} <b>{dma_label}</b>
                    </span>
                    <span style="font-size:0.75rem;color:#8aa0c0;margin-left:auto;">{dma_detail}</span>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="verdict-banner" style="background:rgba(100,116,139,0.07);
                     border:1px solid #475569;margin-bottom:0.3rem;">
                    <span class="badge b-neu">DMA TREND</span>
                    <span style="font-size:0.85rem;color:#8aa0c0;">
                        ⚪ Insufficient data for 200 DMA (need 200+ bars)
                    </span>
                </div>""", unsafe_allow_html=True)

            # ── CMP vs ALL DMA Strategy ───────────────────────────────────────
            s100 = last.get("SMA_100", np.nan)
            dma_res = dma_cmp_analysis(df)
            phase     = dma_res["phase"]
            phase_clr = dma_res["phase_color"]

            # Phase header banner
            p_bg  = f"rgba(52,211,153,0.08)"  if "BULL" in phase else \
                    f"rgba(248,113,113,0.08)"  if "BEAR" in phase else \
                    f"rgba(251,191,36,0.08)"   if "RECOVERING" in phase or "EXTENDED" in phase else \
                    f"rgba(251,146,60,0.08)"   if "WEAKEN" in phase else \
                    f"rgba(100,116,139,0.07)"

            # Build DMA distance chips
            def _chip(label, pct_val, threshold_bull=0):
                if np.isnan(pct_val): return ""
                clr = "#34d399" if pct_val > threshold_bull else "#f87171"
                return (f'<span class="surge-metric">{label}: '
                        f'<b style="color:{clr};">{pct_val:+.2f}%</b></span>')

            chips = (
                _chip("vs SMA20",  dma_res["pct_vs_20"]) +
                _chip("vs SMA50",  dma_res["pct_vs_50"]) +
                _chip("vs SMA100", dma_res["pct_vs_100"]) +
                _chip("vs SMA200", dma_res["pct_vs_200"])
            )

            bull_target = dma_res["bull_target"]
            target_str  = f"🎯 Bull Target: <b style='color:#34d399;'>₹{bull_target:,.2f}</b> (+7%)" \
                          if "BULL" in phase or "RECOVERING" in phase else \
                          f"⬇ Bear Target: <b style='color:#f87171;'>₹{dma_res['bear_stop']:,.2f}</b> (−7%)" \
                          if "BEAR" in phase else "Target: await DMA alignment"

            st.markdown(f"""
            <div style="background:{p_bg};border:1px solid {phase_clr};border-radius:12px;
                        padding:1rem 1.4rem;margin:0.5rem 0;">
              <div style="display:flex;align-items:center;gap:0.8rem;flex-wrap:wrap;margin-bottom:0.6rem;">
                <span class="badge" style="background:rgba(0,0,0,0.3);
                      color:{phase_clr};border:1px solid {phase_clr};">CMP vs ALL DMA</span>
                <span style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;
                      color:{phase_clr};">{phase}</span>
                <span style="font-size:0.78rem;color:#8aa0c0;">
                    CMP above <b style="color:#dce8f5;">{dma_res['above_count']}/4</b> DMAs
                </span>
                <span style="margin-left:auto;font-size:0.78rem;color:#b8d0e8;">{target_str}</span>
              </div>
              <div style="margin:0.3rem 0;">{chips}</div>
              <div style="margin-top:0.5rem;">
                <span class="surge-metric">SMA20 <b style="color:#38bdf8;">₹{dma_res['sma20']:,.0f}</b></span>
                <span class="surge-metric">SMA50 <b style="color:#fb923c;">₹{dma_res['sma50']:,.0f}</b></span>
                <span class="surge-metric">SMA100 <b style="color:#a78bfa;">{("N/A" if np.isnan(dma_res["sma100"]) else f"₹{dma_res['sma100']:,.0f}")}</b></span>
                <span class="surge-metric">SMA200 <b style="color:#f472b6;">{("N/A" if np.isnan(dma_res["sma200"]) else f"₹{dma_res['sma200']:,.0f}")}</b></span>
              </div>
            </div>""", unsafe_allow_html=True)

            # Insight rows
            for ins_line in dma_res["insights"]:
                brd = "#34d399" if "BULL" in ins_line or "✅" in ins_line else \
                      "#f87171" if "BEAR" in ins_line or "⚠️" in ins_line else "#475569"
                st.markdown(f'<div class="ins-row" style="border-left:3px solid {brd};">{ins_line}</div>',
                            unsafe_allow_html=True)

            # Dedicated DMA chart in expander to keep page clean
            with st.expander("📊 CMP vs All DMA — Dedicated Strategy Chart", expanded=False):
                dma_fig = build_dma_chart(df, dma_res, symbol, tf)
                if dma_fig:
                    st.plotly_chart(dma_fig, use_container_width=True)

            # ── IMPORTANT FIX EXPLANATION BANNER ──
            # The verdict is purely indicator-based, not P&L based
            verdict,vtype=sig_data["verdict"]; score=sig_data["score"]
            vc={"buy":"v-buy","sell":"v-sell","neu":"v-neu"}[vtype]
            bc={"buy":"b-buy","sell":"b-sell","neu":"b-neu"}[vtype]
            st.markdown(f"""
            <div class="verdict-banner {vc}">
                <span class="badge {bc}">{verdict}</span>
                <span style="font-family:'Syne',sans-serif;font-size:0.9rem;color:#dce8f5;">
                    Composite Score: <b style="color:#e8f4ff;">{score:+d}</b>
                    &nbsp;·&nbsp; Based on: RSI · MACD · BB · EMA9 · MA Trend · Volume · Stoch · Delivery
                </span>
            </div>
            <div style="font-size:0.72rem;color:#4a6a8a;margin:0.2rem 0 0.5rem;padding-left:0.3rem;">
                ℹ️ Signal direction is based on <b style="color:#5a8ab0;">current indicator readings</b>, 
                not portfolio P&amp;L. A stock up 50% YTD can still show SELL if indicators are bearish.
            </div>""", unsafe_allow_html=True)

            # ── Built-in Strategy Cards ──
            st.markdown('<div class="sec-title">🎯 Built-in Strategy Signals</div>', unsafe_allow_html=True)
            sc=st.columns(3)
            icons={"buy":"🟢","sell":"🔴","wait":"🟡"}
            cls_map={"buy":"sc-buy","sell":"sc-sell","wait":"sc-wait"}
            bc_map={"buy":"b-buy","sell":"b-sell","wait":"b-neu"}
            for i,s in enumerate(builtin_strats):
                sc[i%3].markdown(f"""<div class="strat-card {cls_map[s['signal']]}">
                    <div class="st-name">{icons[s['signal']]} {s['name']}</div>
                    <div class="st-desc">{s['desc']}</div>
                    <div class="st-detail">{s['detail']}</div>
                    <div style="margin-top:0.45rem;">
                        <span class="badge {bc_map[s['signal']]}">{s['signal'].upper()}</span>
                        &nbsp;<span style="font-size:0.68rem;color:#5a7898;">
                        {len(s['bars'])} trigger{'s' if len(s['bars'])!=1 else ''}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

            # ── Trigger Log for Built-in Strategies ──
            st.markdown('<div class="sec-title">📋 Built-in Strategy Trigger Log</div>', unsafe_allow_html=True)
            strat_tabs = st.tabs([s["name"] for s in builtin_strats])
            for si, s in enumerate(builtin_strats):
                with strat_tabs[si]:
                    render_trigger_log(df, s["bars"], s["signal"], s["name"],
                                       widget_key=f"bi_{symbol}_{si}")

            # ── Custom Strategy Results ──
            if custom_rendered:
                st.markdown('<div class="sec-title">🛠 Custom Strategy Results</div>', unsafe_allow_html=True)
                cust_cols=st.columns(min(len(custom_rendered),3))
                for ci,(cname,cbars,csig) in enumerate(custom_rendered):
                    badge_c="b-buy" if csig=="buy" else "b-sell"
                    card_c="sc-buy" if csig=="buy" else "sc-sell"
                    icon="🟢" if csig=="buy" else "🔴"
                    status="TRIGGERED" if cbars else "NO SIGNAL"
                    cust_cols[ci%3].markdown(f"""<div class="strat-card {card_c}">
                        <div class="st-name">{icon} {cname}</div>
                        <div class="st-detail">Triggers: <b style="color:#e8f4ff;">{len(cbars)}</b>
                        {'&nbsp;· Last: '+df["Date"].iloc[cbars[-1]].strftime("%d %b %Y") if cbars else ''}</div>
                        <div style="margin-top:0.4rem;">
                            <span class="badge {badge_c}">{csig.upper()}</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                st.markdown('<div class="sec-title">📋 Custom Strategy Trigger Log</div>', unsafe_allow_html=True)
                if len(custom_rendered)==1:
                    cname,cbars,csig=custom_rendered[0]
                    render_trigger_log(df, cbars, csig, cname,
                                       widget_key=f"cu_{symbol}_0")
                else:
                    ctabs=st.tabs([f"C{i+1}: {c[0][:20]}" for i,c in enumerate(custom_rendered)])
                    for ci,(cname,cbars,csig) in enumerate(custom_rendered):
                        with ctabs[ci]:
                            render_trigger_log(df, cbars, csig, cname,
                                               widget_key=f"cu_{symbol}_{ci}")

            # ── Technical Chart ──
            st.markdown('<div class="sec-title">📊 Technical Chart</div>', unsafe_allow_html=True)
            st.plotly_chart(build_chart(df,symbol,builtin_strats,custom_rendered,tf),
                            use_container_width=True)

            # ── Indicator Signals ──
            st.markdown('<div class="sec-title">📡 Indicator Signal Breakdown</div>', unsafe_allow_html=True)
            sig_cols=st.columns(2)
            smap={"buy":"s-buy","sell":"s-sell","neu":"s-neu"}
            for i,(key,(text,stype)) in enumerate(sig_data["signals"].items()):
                sig_cols[i%2].markdown(f"""<div class="sig-box {smap[stype]}">
                    <b style="color:#e8f4ff;">{key}</b><br>{text}
                </div>""", unsafe_allow_html=True)

            # ── BB + RSI Strategy Section ─────────────────────────────────────
            st.markdown('<div class="sec-title">🎯 Bollinger Bands + RSI Strategy  <span style="font-size:0.72rem;color:#4a6a8a;font-weight:400;">· John Bollinger + RSI dual-confirmation system</span></div>',
                        unsafe_allow_html=True)

            bb_status = bb_rsi_current_status(df)
            bb_pct    = bb_status["bb_pct"]
            is_sq     = bb_status["is_squeeze"]
            active_bb = bb_status["active_signals"]

            # ── Current reading card ──
            bbu_v = bb_status["bbu"]; bbl_v = bb_status["bbl"]
            bbm_v = bb_status["bbm"]; bbw_v = bb_status["bbw"]
            rsi_v = bb_status["rsi"]; vr_v  = bb_status["vr"]

            # Band position colour
            if not np.isnan(bb_pct):
                if   bb_pct >= 85: bp_clr="#f87171"; bp_lbl="Near UPPER band — overbought zone"
                elif bb_pct >= 60: bp_clr="#fbbf24"; bp_lbl="Upper half — bullish momentum"
                elif bb_pct <= 15: bp_clr="#34d399"; bp_lbl="Near LOWER band — oversold zone"
                elif bb_pct <= 40: bp_clr="#a78bfa"; bp_lbl="Lower half — bearish momentum"
                else:              bp_clr="#8aa0c0"; bp_lbl="Middle — neutral zone"
            else:
                bp_clr="#475569"; bp_lbl="N/A"; bb_pct=50

            squeeze_note = (" 🔴 SQUEEZE ACTIVE — Breakout imminent!" if is_sq
                            else " ✅ Normal volatility")

            st.markdown(f"""
            <div style="background:#0c1828;border:1px solid #1a3050;border-radius:12px;
                        padding:1rem 1.4rem;margin-bottom:0.6rem;">
              <div style="display:flex;flex-wrap:wrap;gap:0.5rem;align-items:center;margin-bottom:0.7rem;">
                <span class="surge-metric">BB Upper <b style="color:#818cf8;">₹{bbu_v:,.2f}</b></span>
                <span class="surge-metric">BB Mid <b style="color:#fbbf24;">₹{bbm_v:,.2f}</b></span>
                <span class="surge-metric">BB Lower <b style="color:#818cf8;">₹{bbl_v:,.2f}</b></span>
                <span class="surge-metric">RSI <b style="color:{'#f87171' if rsi_v>65 else '#34d399' if rsi_v<35 else '#dce8f5'};">{rsi_v:.1f}</b></span>
                <span class="surge-metric">BB Position <b style="color:{bp_clr};">{bb_pct:.0f}%</b></span>
                <span class="surge-metric">Volatility<b style="color:{'#fbbf24' if is_sq else '#8aa0c0'};">{squeeze_note}</b></span>
              </div>
              <div style="background:#0a1020;border-radius:6px;height:8px;margin-bottom:0.5rem;position:relative;">
                <div style="width:{min(bb_pct,100):.0f}%;height:100%;border-radius:6px;
                            background:linear-gradient(90deg,#34d399,#fbbf24,#f87171);"></div>
              </div>
              <div style="font-size:0.75rem;color:{bp_clr};">📍 Price is at {bb_pct:.0f}% of the BB range — {bp_lbl}</div>
            </div>""", unsafe_allow_html=True)

            # ── Active signals ──
            if active_bb:
                for sig_name, sig_type, sig_desc in active_bb:
                    brd = "#34d399" if sig_type=="buy" else "#f87171"
                    bg  = "rgba(52,211,153,0.07)" if sig_type=="buy" else "rgba(248,113,113,0.07)"
                    st.markdown(f"""
                    <div style="background:{bg};border:1px solid {brd};border-left:4px solid {brd};
                                border-radius:8px;padding:0.7rem 1rem;margin:0.3rem 0;">
                        <b style="color:{brd};font-size:0.88rem;">{sig_name}</b>
                        <div style="color:#c4d4ea;font-size:0.78rem;margin-top:0.2rem;">{sig_desc}</div>
                    </div>""", unsafe_allow_html=True)
            else:
                st.markdown('<div class="ins-row">⚪ No BB+RSI signal active on the current bar. Waiting for price to touch a band with RSI confirmation.</div>',
                            unsafe_allow_html=True)

            # ── BB+RSI chart ──
            bb_fig = build_bb_rsi_chart(df, symbol, tf)
            if bb_fig:
                st.plotly_chart(bb_fig, use_container_width=True)

            # ── Surge Analysis (2-3 week window) ──────────────────────────────
            st.markdown('<div class="sec-title">🔥 Recent Surge Analysis  <span style="font-size:0.72rem;color:#4a6a8a;font-weight:400;">· Last 15 sessions (≈3 weeks)</span></div>',
                        unsafe_allow_html=True)

            s_dir   = surge["direction"]
            s_score = surge["surge_score"]
            s_level = surge["alert_level"]

            # Card class by direction
            card_cls = {"bullish":"surge-bullish","bearish":"surge-bearish",
                        "neutral":"surge-neutral"}.get(s_dir,"surge-neutral")
            if s_level == "caution": card_cls = "surge-caution"

            # Direction icon & label
            dir_icon  = {"bullish":"🟢 BULLISH SURGE","bearish":"🔴 BEARISH SURGE",
                         "neutral":"⚪ NO SURGE"}.get(s_dir,"⚪ NEUTRAL")
            if s_level == "caution": dir_icon = "🟠 CAUTION"

            # Score bar (visual)
            score_pct = (s_score + 10) / 20 * 100
            bar_clr   = "#34d399" if s_score > 0 else ("#f87171" if s_score < 0 else "#64748b")

            # Metric chips
            pc  = surge["price_chg_pct"]
            vsr = surge["vol_surge_ratio"]
            dc  = surge["deliv_chg"]
            price_chip  = f"Price {pc:+.1f}%"  if not np.isnan(pc)  else "Price N/A"
            vol_chip    = f"Vol {vsr:.1f}× avg" if not np.isnan(vsr) else "Vol N/A"
            deliv_chip  = f"Delivery Δ{dc:+.1f}pp" if not np.isnan(dc) else "Delivery N/A"
            pt_clr = "#34d399" if (not np.isnan(pc) and pc>3) else ("#f87171" if (not np.isnan(pc) and pc<-3) else "#8aa0c0")
            vt_clr = "#34d399" if (not np.isnan(vsr) and vsr>1.5) else ("#fbbf24" if (not np.isnan(vsr) and vsr>1.2) else "#8aa0c0")
            dt_clr = "#34d399" if (not np.isnan(dc) and dc>5) else ("#f87171" if (not np.isnan(dc) and dc<-5) else "#8aa0c0")

            st.markdown(f"""
            <div class="surge-card {card_cls}">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:0.5rem;">
                <div class="surge-title">{dir_icon} &nbsp; Surge Score: {s_score:+d} / 10</div>
                <div>
                  <span class="surge-metric"><b style="color:{pt_clr};">{price_chip}</b></span>
                  <span class="surge-metric"><b style="color:{vt_clr};">{vol_chip}</b></span>
                  <span class="surge-metric"><b style="color:{dt_clr};">{deliv_chip}</b></span>
                </div>
              </div>
              <div style="background:#0a1020;border-radius:6px;height:6px;margin:0.6rem 0;overflow:hidden;">
                <div style="width:{score_pct:.0f}%;height:100%;background:{bar_clr};border-radius:6px;
                            transition:width 0.4s;"></div>
              </div>
              <div style="font-size:0.72rem;color:#4a6a8a;margin-bottom:0.3rem;">
                Trend signals: Price={surge['price_trend']} · Volume={surge['vol_trend']} · Delivery={surge['deliv_trend']}
              </div>
            </div>""", unsafe_allow_html=True)

            # Commentary lines
            for line in surge["commentary"]:
                brd = "#34d399" if "bullish" in line.lower() or "surge" in line.lower() or "accumulation" in line.lower() or "rally" in line.lower() else \
                      "#f87171" if "bearish" in line.lower() or "sell" in line.lower() or "distribut" in line.lower() or "decline" in line.lower() or "selloff" in line.lower() else \
                      "#fbbf24" if "caution" in line.lower() or "divergence" in line.lower() or "watch" in line.lower() or "low volume" in line.lower() else "#475569"
                st.markdown(f'<div class="ins-row" style="border-left:3px solid {brd};">{line}</div>',
                            unsafe_allow_html=True)

            # Surge chart
            surge_fig = build_surge_chart(df, lookback=15, symbol=symbol)
            if surge_fig:
                st.plotly_chart(surge_fig, use_container_width=True)

            # ── Forecast ──
            st.markdown('<div class="sec-title">🔮 Price Forecast  <span style="font-size:0.7rem;color:#4a6a8a;font-weight:400;">· Recent price-action anchored model</span></div>',
                        unsafe_allow_html=True)
            fd_dates, bv, unc, fmeta = forecast_prices(df, forecast_days, tf, signal_score=score)
            st.plotly_chart(build_forecast_chart(df, fd_dates, bv, unc, symbol, tf, fmeta),
                            use_container_width=True)
            exp_chg = (bv[-1] / cl - 1) * 100

            # Forecast methodology explainer
            eff_slope = fmeta["effective_slope_pct"]
            s20_slope = fmeta["short_slope_pct"]
            m50_slope = fmeta["medium_slope_pct"]
            rsi_m     = fmeta["rsi_mult"]
            sc_adj    = fmeta["score_adj_pct"]
            f_dir     = fmeta["direction"]
            f_rsi     = fmeta["rsi_val"]
            f_atr     = fmeta["atr_val"]
            g_target  = fmeta["gravity_target"]

            dir_clr = "#34d399" if eff_slope > 0 else "#f87171"
            st.markdown(f"""
            <div style="background:#0c1828;border:1px solid #1a3050;border-radius:10px;
                        padding:0.8rem 1.2rem;margin-bottom:0.5rem;font-size:0.78rem;line-height:1.7;">
                <b style="color:#38bdf8;">Forecast Model Breakdown:</b>
                &nbsp;Direction: <b style="color:{dir_clr};">{f_dir}</b>
                &nbsp;·&nbsp; 20-bar slope: <b style="color:#dce8f5;">{s20_slope:+.3f}%/bar</b>
                &nbsp;·&nbsp; 50-bar slope: <b style="color:#dce8f5;">{m50_slope:+.3f}%/bar</b>
                &nbsp;·&nbsp; Effective slope: <b style="color:{dir_clr};">{eff_slope:+.3f}%/bar</b>
                <br>
                RSI={f_rsi:.1f} → multiplier <b style="color:#dce8f5;">×{rsi_m:.2f}</b>
                &nbsp;·&nbsp; Signal score adj: <b style="color:#dce8f5;">{sc_adj:+.4f}%/bar</b>
                &nbsp;·&nbsp; EMA9 gravity target: <b style="color:#fbbf24;">₹{g_target:,.2f}</b>
                &nbsp;·&nbsp; ATR band: <b style="color:#dce8f5;">±₹{f_atr:,.0f}/bar</b>
            </div>""", unsafe_allow_html=True)

            fdf = pd.DataFrame({
                "Date":         [d.strftime("%d %b %Y") for d in fd_dates],
                "Forecast ₹":   [f"{v:,.2f}" for v in bv],
                "Low (−2σ) ₹":  [f"{v-2*u:,.2f}" for v,u in zip(bv,unc)],
                "High (+2σ) ₹": [f"{v+2*u:,.2f}" for v,u in zip(bv,unc)],
                "vs LTP":       [f"{'▲' if v>cl else '▼'} {(v/cl-1)*100:+.2f}%" for v in bv],
            })
            st.dataframe(fdf, use_container_width=True, hide_index=True)

            # ── Pro Insights ──
            st.markdown('<div class="sec-title">🧠 Pro-Trader Insights</div>', unsafe_allow_html=True)
            ins=[]
            if not(np.isnan(s20) or np.isnan(s50)):
                if   cl>s20 and s20>s50: ins.append("📈 <b>Trend:</b> UPTREND confirmed (Price>SMA20>SMA50). Trail stops below SMA20.")
                elif cl<s20 and s20<s50: ins.append("📉 <b>Trend:</b> DOWNTREND confirmed. Avoid buying into weakness.")
                else: ins.append("↔️ <b>Trend:</b> Mixed MA alignment — transition zone. Wait for clarity.")
            # 50/200 DMA long-term trend
            if not (np.isnan(s50) or np.isnan(s200)):
                dma_g = (s50-s200)/s200*100
                if s50 > s200:
                    ins.append(f"📊 <b>Long-Term DMA Trend (50/200):</b> 🟢 GOLDEN CROSS — SMA50 (₹{s50:,.2f}) is {dma_g:+.2f}% above SMA200 (₹{s200:,.2f}). Long-term uptrend intact. Buy dips with confidence.")
                else:
                    ins.append(f"📊 <b>Long-Term DMA Trend (50/200):</b> 🔴 DEATH CROSS — SMA50 (₹{s50:,.2f}) is {dma_g:+.2f}% below SMA200 (₹{s200:,.2f}). Long-term downtrend. Avoid fresh longs until SMA50 recrosses SMA200.")
            if not np.isnan(e9):
                rel="above" if cl>e9 else "below"
                ins.append(f"🎯 <b>EMA9 (₹{e9:,.2f}):</b> Price {rel} EMA9 — {'dips to EMA9 are entry zones in an uptrend.' if cl>e9 else 'EMA9 is now dynamic resistance.'}")
            if not np.isnan(s14):
                ins.append(f"📐 <b>SMA14 (₹{s14:,.2f}):</b> Price {'above' if cl>s14 else 'below'} — {'intermediate trend bullish.' if cl>s14 else 'intermediate trend bearish.'}")
            act=[s for s in builtin_strats if s["signal"] in ("buy","sell") and s["bars"]]
            if act:
                sigs_set=set(s["signal"] for s in act)
                names=", ".join(s["name"] for s in act)
                if sigs_set=={"buy"}: ins.append(f"✅ <b>Strategy Confluence:</b> {len(act)} built-in signals BULLISH ({names}). High conviction.")
                elif sigs_set=={"sell"}: ins.append(f"❌ <b>Strategy Alignment:</b> {len(act)} signals BEARISH ({names}). Protect longs.")
                else: ins.append(f"⚠️ <b>Mixed:</b> Conflicting signals — await clearer alignment before committing.")
            # Surge insight in Pro section
            if surge["has_data"] and surge["alert_level"] in ("alert","caution","watch"):
                if surge["direction"]=="bullish":
                    ins.append(f"🔥 <b>Surge Alert:</b> Score {surge['surge_score']:+d}/10 — {surge['price_trend'].title()} price, {surge['vol_trend']} volume, {surge['deliv_trend']} delivery over 15 sessions. Elevated probability of continued upside. Enter on confirmed pullback.")
                elif surge["direction"]=="bearish":
                    ins.append(f"⚠️ <b>Surge Warning:</b> Score {surge['surge_score']:+d}/10 — {surge['price_trend'].title()} price with {surge['deliv_trend']} delivery suggests distribution. Risk of sharp correction. Tighten stops.")
            atr=last.get("ATR%",np.nan)
            if not np.isnan(atr):
                if   atr>2.5: ins.append(f"⚡ <b>Volatility HIGH:</b> ATR {atr:.2f}% — widen stops, reduce position size.")
                elif atr<0.8: ins.append(f"😴 <b>Volatility COMPRESSED:</b> ATR {atr:.2f}% — breakout may be imminent.")
                else: ins.append(f"⚖️ <b>Volatility Normal:</b> ATR {atr:.2f}% — standard risk parameters apply.")
            d=last.get("Delivery%",np.nan)
            if not np.isnan(d):
                if   d>60: ins.append(f"🏦 <b>Delivery {d:.1f}%:</b> Institutional/investor buying dominant — quality move.")
                elif d<25: ins.append(f"🎲 <b>Delivery {d:.1f}%:</b> Speculative activity dominant — breakouts may fail.")
                else: ins.append(f"📦 <b>Delivery {d:.1f}%:</b> Healthy investor-trader mix.")
            piv=last.get("Pivot",np.nan)
            if not np.isnan(piv):
                r1v,r2v=last.get("R1",np.nan),last.get("R2",np.nan)
                s1v,s2v=last.get("S1",np.nan),last.get("S2",np.nan)
                ins.append(f"🎯 <b>Pivot Levels:</b> Pivot ₹{piv:,.0f} · R1 ₹{r1v:,.0f} · R2 ₹{r2v:,.0f} · S1 ₹{s1v:,.0f} · S2 ₹{s2v:,.0f}")
            ins.append(f"🔮 <b>{tf} Forecast ({forecast_days}b):</b> Target ₹{bv[-1]:,.2f} ({exp_chg:+.2f}%) · ±₹{2*unc[-1]:,.0f} band · Model: {fmeta['direction']} (slope {fmeta['effective_slope_pct']:+.3f}%/bar, RSI×{fmeta['rsi_mult']:.2f})")
            for i_ in ins:
                st.markdown(f'<div class="ins-row">{i_}</div>', unsafe_allow_html=True)

            # ── Institutional Report ─────────────────────────────────────────
            # Determine ticker for yfinance lookups
            ticker_yf = symbol if symbol in (yahoo_data or {}) else symbol
            # Compute S/R levels
            sr_data = compute_sr_levels(df, cl)
            # Fetch fundamentals (only if yfinance source or ticker looks valid)
            fd_data = {}
            oc_data = {}
            if YF_AVAILABLE and "." in ticker_yf or ticker_yf.startswith("^"):
                with st.spinner(f"Fetching live fundamentals & options for {ticker_yf}…"):
                    fd_data = fetch_fundamentals(ticker_yf)
                    oc_data = fetch_option_chain(ticker_yf, cl)
            elif YF_AVAILABLE and data_source == "🌐 Yahoo Finance":
                with st.spinner(f"Fetching live data for {ticker_yf}…"):
                    fd_data = fetch_fundamentals(ticker_yf)
                    oc_data = fetch_option_chain(ticker_yf, cl)
            render_institutional_report(df, symbol, ticker_yf, cl, score, sig_data,
                                        sr_data, fd_data, oc_data, surge)

            # Summary row — includes surge_score and DMA trend
            strat_buy=[s for s in builtin_strats if s["signal"]=="buy" and s["bars"]]
            strat_sell=[s for s in builtin_strats if s["signal"]=="sell" and s["bars"]]
            strat_sig="🟢 BUY" if strat_buy and not strat_sell else ("🔴 SELL" if strat_sell else "🟡 WAIT")
            surge_label = (f"🔥 {surge['direction'].upper()} ({surge['surge_score']:+d})"
                           if surge["has_data"] else "N/A")
            trend_str=("↑ UP" if cl>s20>s50 else "↓ DOWN" if cl<s20<s50 else "↔ SIDE") if not np.isnan(s20) else "N/A"

            # 50/200 DMA trend label
            if not (np.isnan(s50) or np.isnan(s200)):
                dma_gap_val = (s50 - s200) / s200 * 100
                if s50 > s200:
                    dma_trend_label = f"🟢 BULL ({dma_gap_val:+.1f}%)"
                else:
                    dma_trend_label = f"🔴 BEAR ({dma_gap_val:+.1f}%)"
            else:
                dma_trend_label = "⚪ N/A (<200 bars)"

            all_sum.append({
                "Symbol":symbol,"TF":tf,"LTP ₹":f"{cl:,.2f}","Chg%":f"{chgp:+.2f}%",
                "RSI":f"{last.get('RSI',0):.1f}",
                "vs EMA9":"▲" if cl>e9 else "▼","vs SMA14":"▲" if cl>s14 else "▼",
                "50/200 DMA Trend": dma_trend_label,
                "Trend":trend_str,"Delivery%":f"{last.get('Delivery%',0):.1f}%",
                "Surge":surge_label,
                "Price Trend":surge.get("price_trend","–"),
                "Vol Trend":surge.get("vol_trend","–"),
                "Deliv Trend":surge.get("deliv_trend","–"),
                "Strategy":strat_sig,"Classic":verdict,
                "Fcst ₹":f"{bv[-1]:,.2f}","Exp%":f"{exp_chg:+.2f}%",
                "Score":f"{score:+d}",
                "Surge Score":f"{surge['surge_score']:+d}",
            })

    # ── STRATEGY BUILDER TAB ──────────────────────────────────────────────────
    # ── DMA ANALYSIS TAB ─────────────────────────────────────────────────────
    dma_tab_idx = len(stock_data)
    with tabs[dma_tab_idx]:
        st.markdown('<div class="sec-title">📊 DMA Analysis — All Stocks</div>', unsafe_allow_html=True)
        st.markdown('<div class="ins-row">DMA 5/10/20/50/100/200 · Bull/Bear Run · 10-Day Cumulative Average · BUY / SELL / HOLD</div>',
                    unsafe_allow_html=True)

        # ── Helper functions for DMA tab ──────────────────────────────────────
        def compute_all_dmas(df):
            """Add DMA 5,10,20,50,100,200 to df."""
            for p in [5, 10, 20, 50, 100, 200]:
                df[f"DMA_{p}"] = df["Close"].rolling(p).mean()
            return df

        def get_dma_trend(row, price):
            """Bull/Bear based on price vs key DMAs (50,100,200)."""
            key_dmas = []
            for p in [50, 100, 200]:
                v = row.get(f"DMA_{p}", float("nan"))
                if not (isinstance(v, float) and np.isnan(v)):
                    key_dmas.append(float(v))
            if not key_dmas:
                return "⚪ Insufficient"
            above = all(price > d for d in key_dmas)
            below = all(price < d for d in key_dmas)
            if above:
                return "🟢 Bull Run"
            elif below:
                return "🔴 Bear Run"
            elif price > key_dmas[0]:
                return "🟡 Recovering"
            else:
                return "🟠 Weakening"

        def compute_car(close_series, n=10):
            """Cumulative Average Result over last n days."""
            closes = close_series.dropna().tail(n).values
            if len(closes) < 2:
                return "—", 0.0, []
            cum_avgs = np.cumsum(closes) / np.arange(1, len(closes) + 1)
            slope = cum_avgs[-1] - cum_avgs[0]
            direction = "↑ Increasing" if slope >= 0 else "↓ Decreasing"
            return direction, round(slope, 4), list(closes)

        def get_recommendation(row, price, car_direction):
            """BUY / SELL / HOLD logic."""
            key_dmas = []
            for p in [50, 100, 200]:
                v = row.get(f"DMA_{p}", float("nan"))
                if not (isinstance(v, float) and np.isnan(v)):
                    key_dmas.append(float(v))
            if not key_dmas:
                return "⏳ HOLD"
            above_all = all(price > d for d in key_dmas)
            below_all = all(price < d for d in key_dmas)
            increasing = "Increasing" in car_direction
            if above_all and increasing:
                return "✅ BUY"
            elif below_all and not increasing:
                return "🚫 SELL"
            return "⏳ HOLD"

        # ── Build DMA table ───────────────────────────────────────────────────
        dma_rows = []
        sparkline_data = {}   # for mini charts

        for sym, df_s in stock_data.items():
            df_s = compute_all_dmas(df_s)
            last = df_s.iloc[-1]
            price = float(last["Close"])

            row_data = {"Ticker": sym, "Price ₹": round(price, 2)}

            # DMA values
            for p in [5, 10, 20, 50, 100, 200]:
                val = last.get(f"DMA_{p}", float("nan"))
                try:
                    fval = float(val)
                    row_data[f"DMA {p}"] = round(fval, 2) if not np.isnan(fval) else "—"
                except Exception:
                    row_data[f"DMA {p}"] = "—"

            # Bull / Bear trend
            row_data["Trend"] = get_dma_trend(last, price)

            # CAR — 10-day cumulative average
            car_dir, car_slope, closes_10 = compute_car(df_s["Close"])
            row_data["CAR (10d)"] = car_dir
            sparkline_data[sym] = closes_10

            # Recommendation
            row_data["Recommendation"] = get_recommendation(last, price, car_dir)

            dma_rows.append(row_data)

        if dma_rows:
            dma_df = pd.DataFrame(dma_rows)

            # ── Styled table ──────────────────────────────────────────────────
            def style_rec(val):
                if "BUY" in str(val):
                    return "background-color:#052e16;color:#4ade80;font-weight:700;text-align:center;"
                elif "SELL" in str(val):
                    return "background-color:#2d0a0a;color:#f87171;font-weight:700;text-align:center;"
                elif "HOLD" in str(val):
                    return "background-color:#1c1700;color:#fbbf24;font-weight:700;text-align:center;"
                return ""

            def style_trend(val):
                if "Bull" in str(val):
                    return "color:#4ade80;font-weight:700;"
                elif "Bear" in str(val):
                    return "color:#f87171;font-weight:700;"
                elif "Recover" in str(val):
                    return "color:#fbbf24;font-weight:700;"
                elif "Weaken" in str(val):
                    return "color:#fb923c;font-weight:700;"
                return ""

            def style_car(val):
                if "↑" in str(val):
                    return "color:#4ade80;font-weight:600;"
                elif "↓" in str(val):
                    return "color:#f87171;font-weight:600;"
                return ""
            styled = (
                dma_df.style
                .map(style_rec, subset=["Recommendation"])
                .map(style_trend, subset=["Trend"])
                .map(style_car, subset=["CAR (10d)"])
            )

            st.dataframe(styled, use_container_width=True, hide_index=True)

            # ── Summary KPI cards ────────────────────────────────────────────
            total   = len(dma_rows)
            n_buy   = sum(1 for r in dma_rows if "BUY"  in r["Recommendation"])
            n_sell  = sum(1 for r in dma_rows if "SELL" in r["Recommendation"])
            n_hold  = sum(1 for r in dma_rows if "HOLD" in r["Recommendation"])
            n_bull  = sum(1 for r in dma_rows if "Bull" in r["Trend"])
            n_bear  = sum(1 for r in dma_rows if "Bear" in r["Trend"])

            st.markdown("")
            kk = st.columns(6)
            kpi_meta = [
                ("Stocks", str(total),         "#38bdf8"),
                ("✅ BUY",  str(n_buy),         "#4ade80"),
                ("🚫 SELL", str(n_sell),        "#f87171"),
                ("⏳ HOLD", str(n_hold),        "#fbbf24"),
                ("🟢 Bull", str(n_bull),        "#34d399"),
                ("🔴 Bear", str(n_bear),        "#ef4444"),
            ]
            for col_, (lbl_, val_, clr_) in zip(kk, kpi_meta):
                col_.markdown(f"""<div class="metric-card">
                    <div class="metric-label">{lbl_}</div>
                    <div class="metric-value" style="color:{clr_};">{val_}</div>
                </div>""", unsafe_allow_html=True)

            # ── Individual stock DMA detail charts ────────────────────────────
            st.markdown('<div class="sec-title" style="margin-top:1.2rem;">📈 DMA Detail — Per Stock</div>', unsafe_allow_html=True)

            for sym, df_s in stock_data.items():
                df_s = compute_all_dmas(df_s)
                last = df_s.iloc[-1]
                price = float(last["Close"])

                car_dir, car_slope, closes_10 = compute_car(df_s["Close"])
                trend_label = get_dma_trend(last, price)
                rec_label   = get_recommendation(last, price, car_dir)

                trend_clr = ("#4ade80" if "Bull" in trend_label else
                             "#f87171" if "Bear" in trend_label else
                             "#fbbf24" if "Recover" in trend_label else "#fb923c")
                rec_clr   = ("#4ade80" if "BUY" in rec_label else
                             "#f87171" if "SELL" in rec_label else "#fbbf24")
                car_clr   = "#4ade80" if "↑" in car_dir else "#f87171"

                with st.expander(f"📊 {sym}  ·  ₹{price:,.2f}  ·  {trend_label}  ·  {rec_label}", expanded=False):
                    # Mini metric row
                    mc = st.columns(4)
                    mc[0].markdown(f"""<div class="metric-card">
                        <div class="metric-label">Price</div>
                        <div class="metric-value" style="color:#e8f4ff;">₹{price:,.2f}</div>
                    </div>""", unsafe_allow_html=True)
                    mc[1].markdown(f"""<div class="metric-card">
                        <div class="metric-label">Trend</div>
                        <div class="metric-value" style="color:{trend_clr};font-size:1rem;">{trend_label}</div>
                    </div>""", unsafe_allow_html=True)
                    mc[2].markdown(f"""<div class="metric-card">
                        <div class="metric-label">CAR (10d)</div>
                        <div class="metric-value" style="color:{car_clr};font-size:1rem;">{car_dir}</div>
                    </div>""", unsafe_allow_html=True)
                    mc[3].markdown(f"""<div class="metric-card">
                        <div class="metric-label">Signal</div>
                        <div class="metric-value" style="color:{rec_clr};font-size:1rem;">{rec_label}</div>
                    </div>""", unsafe_allow_html=True)

                    st.markdown("")

                    # DMA value cards
                    dma_cols = st.columns(6)
                    dma_periods = [5, 10, 20, 50, 100, 200]
                    dma_colors  = ["#38bdf8","#a78bfa","#fbbf24","#fb923c","#f472b6","#34d399"]
                    for dcol, dp, dc in zip(dma_cols, dma_periods, dma_colors):
                        dv = last.get(f"DMA_{dp}", float("nan"))
                        try:
                            dv_f = float(dv)
                            dv_str = f"₹{dv_f:,.2f}" if not np.isnan(dv_f) else "N/A"
                            vs_str = f"{(price/dv_f-1)*100:+.2f}%" if not np.isnan(dv_f) and dv_f>0 else ""
                            vs_clr = "#4ade80" if price>dv_f else "#f87171"
                        except Exception:
                            dv_str, vs_str, vs_clr = "N/A", "", "#8aa0c0"
                        dcol.markdown(f"""<div class="metric-card" style="padding:0.6rem;">
                            <div class="metric-label">DMA {dp}</div>
                            <div style="font-family:'Syne',sans-serif;font-size:0.85rem;
                                 font-weight:700;color:{dc};">{dv_str}</div>
                            <div style="font-size:0.7rem;color:{vs_clr};">{vs_str}</div>
                        </div>""", unsafe_allow_html=True)

                    # 10-day closing price + cumulative average chart
                    if len(closes_10) >= 2:
                        st.markdown('<div style="font-size:0.78rem;color:#4a6a8a;margin:0.5rem 0 0.2rem;">📅 Last 10-Day Closing Price & Cumulative Average</div>', unsafe_allow_html=True)
                        cum_avgs_arr = np.cumsum(closes_10) / np.arange(1, len(closes_10)+1)
                        x_labels = [f"D-{len(closes_10)-i}" for i in range(len(closes_10))]
                        x_labels[-1] = "Today"

                        fig_car = go.Figure()
                        bar_clrs_car = [
                            "rgba(52,211,153,0.7)" if closes_10[i] >= closes_10[i-1] else "rgba(248,113,113,0.7)"
                            for i in range(len(closes_10))
                        ]
                        bar_clrs_car[0] = "rgba(100,116,139,0.5)"

                        fig_car.add_trace(go.Bar(
                            x=x_labels, y=closes_10,
                            marker_color=bar_clrs_car,
                            name="Close", showlegend=True,
                        ))
                        fig_car.add_trace(go.Scatter(
                            x=x_labels, y=cum_avgs_arr,
                            mode="lines+markers",
                            line=dict(color="#fbbf24", width=2.2),
                            marker=dict(size=7, color="#fbbf24"),
                            name="Cumulative Avg",
                        ))
                        # Trend annotation
                        slope_pct = (cum_avgs_arr[-1]/cum_avgs_arr[0]-1)*100 if cum_avgs_arr[0]>0 else 0
                        slope_clr = "#4ade80" if slope_pct >= 0 else "#f87171"
                        fig_car.add_annotation(
                            x=x_labels[-1], y=cum_avgs_arr[-1],
                            text=f"<b>CAR {slope_pct:+.2f}%</b>",
                            font=dict(color=slope_clr, size=11),
                            bgcolor="rgba(10,16,30,0.88)", bordercolor=slope_clr,
                            borderwidth=1, showarrow=True, arrowcolor=slope_clr,
                            ax=40, ay=-25,
                        )
                        fig_car.update_layout(
                            template="plotly_dark", paper_bgcolor="#080c18",
                            plot_bgcolor="#0d1525", height=240,
                            title=dict(
                                text=f"<b>{sym}</b>  ·  10-Day CAR: <span style='color:{slope_clr};'>{car_dir} ({slope_pct:+.2f}%)</span>",
                                font=dict(family="Syne", size=13, color="#dce8f5"), x=0.01,
                            ),
                            legend=dict(orientation="h", x=0, y=1.05,
                                        font=dict(size=11, color="#dce8f5"),
                                        bgcolor="rgba(0,0,0,0)"),
                            margin=dict(l=10, r=60, t=45, b=10),
                            barmode="overlay",
                            xaxis=dict(gridcolor="#111e30", tickfont=dict(color="#8aabcb", size=10)),
                            yaxis=dict(gridcolor="#111e30", tickfont=dict(color="#8aabcb", size=10)),
                            font=dict(color="#94afd4"),
                        )
                        st.plotly_chart(fig_car, use_container_width=True)

                    # DMA vs Price chart (last 60 bars)
                    lb_chart = min(60, len(df_s))
                    df_chart  = df_s.tail(lb_chart)
                    fig_dma2 = go.Figure()

                    if {"Open","High","Low","Close"}.issubset(df_chart.columns):
                        fig_dma2.add_trace(go.Candlestick(
                            x=df_chart["Date"], open=df_chart["Open"], high=df_chart["High"],
                            low=df_chart["Low"], close=df_chart["Close"], name="Price",
                            increasing_line_color="#34d399", decreasing_line_color="#f87171",
                            increasing_fillcolor="rgba(52,211,153,0.72)",
                            decreasing_fillcolor="rgba(248,113,113,0.72)",
                        ))
                    else:
                        fig_dma2.add_trace(go.Scatter(
                            x=df_chart["Date"], y=df_chart["Close"],
                            line=dict(color="#38bdf8", width=1.8), name="Price"))

                    dma_line_cfg = [
                        ("DMA_5",   "#38bdf8",  "solid",    1.0, "DMA 5"),
                        ("DMA_10",  "#a78bfa",  "solid",    1.1, "DMA 10"),
                        ("DMA_20",  "#fbbf24",  "dash",     1.3, "DMA 20"),
                        ("DMA_50",  "#fb923c",  "dash",     1.5, "DMA 50"),
                        ("DMA_100", "#f472b6",  "longdash", 1.6, "DMA 100"),
                        ("DMA_200", "#34d399",  "dot",      2.0, "DMA 200"),
                    ]
                    for col_, clr_, dash_, wid_, lbl_ in dma_line_cfg:
                        if col_ in df_chart.columns:
                            fig_dma2.add_trace(go.Scatter(
                                x=df_chart["Date"], y=df_chart[col_],
                                line=dict(color=clr_, width=wid_, dash=dash_),
                                name=lbl_,
                            ))

                    # Annotate trend phase on chart
                    fig_dma2.add_annotation(
                        x=df_chart["Date"].iloc[-1], y=price,
                        text=f"<b>{trend_label}  {rec_label}</b>",
                        font=dict(color=trend_clr, size=11),
                        bgcolor="rgba(10,16,30,0.88)", bordercolor=trend_clr, borderwidth=1,
                        showarrow=True, arrowcolor=trend_clr, ax=50, ay=-20,
                    )

                    fig_dma2.update_layout(
                        template="plotly_dark", paper_bgcolor="#080c18", plot_bgcolor="#0d1525",
                        height=360,
                        title=dict(
                            text=f"<b>{sym}</b>  ·  DMA 5/10/20/50/100/200  ·  Last {lb_chart} bars",
                            font=dict(family="Syne", size=14, color="#dce8f5"), x=0.01,
                        ),
                        legend=dict(orientation="h", y=1.005, x=0,
                                    font=dict(size=11, color="#dce8f5"),
                                    bgcolor="rgba(10,14,26,0.88)", bordercolor="#2a3d55", borderwidth=1),
                        margin=dict(l=10, r=60, t=50, b=10),
                        xaxis_rangeslider_visible=False,
                        xaxis=dict(gridcolor="#111e30", tickfont=dict(color="#8aabcb", size=10)),
                        yaxis=dict(gridcolor="#111e30", tickfont=dict(color="#8aabcb", size=10)),
                        font=dict(color="#94afd4"),
                    )
                    st.plotly_chart(fig_dma2, use_container_width=True)

            # ── Download DMA table as CSV ─────────────────────────────────────
            st.markdown("---")
            csv_bytes = dma_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="⬇️ Download DMA Analysis as CSV",
                data=csv_bytes,
                file_name="dma_analysis.csv",
                mime="text/csv",
            )

        else:
            st.info("No data available yet. Load stocks via CSV or Yahoo Finance first.")

    builder_tab_idx = len(stock_data) + 1   # +1 for DMA Analysis tab
    with tabs[builder_tab_idx]:

        # ── Sub-tabs inside builder ──
        lib_tab, my_tab, ref_tab = st.tabs([
            "📚 Pro Strategy Library",
            "✏️ My Strategies",
            "📖 Indicator Reference",
        ])

        # ══════════════════════════════════════════════════════════════════════
        #  PRO STRATEGY LIBRARY TAB
        # ══════════════════════════════════════════════════════════════════════
        with lib_tab:
            st.markdown('<div class="sec-title">📚 Pro-Trader Strategy Library</div>', unsafe_allow_html=True)
            st.markdown('<div class="ins-row">Select any strategy to enable it on charts. You can also import it to My Strategies to edit it.</div>',
                        unsafe_allow_html=True)

            # Category filter
            categories = list(PRO_STRATEGY_LIBRARY.keys())
            sel_cat = st.selectbox("Filter by category:", ["All Categories"] + categories,
                                   key="lib_cat_filter")

            shown_cats = categories if sel_cat == "All Categories" else [sel_cat]

            lib_idx = 0   # global index into library_strategies
            for cat in categories:
                strats_in_cat = PRO_STRATEGY_LIBRARY[cat]
                if cat not in shown_cats:
                    lib_idx += len(strats_in_cat)
                    continue

                st.markdown(f'<div class="sec-title">📂 {cat}</div>', unsafe_allow_html=True)

                for strat_name, strat_meta in strats_in_cat.items():
                    sig      = strat_meta["signal"]
                    desc     = strat_meta["desc"]
                    used_by  = strat_meta["used_by"]
                    text     = strat_meta["text"]
                    is_sell  = sig == "SELL"
                    card_brd = "#f87171" if is_sell else "#34d399"
                    sig_icon = "🔴" if is_sell else "🟢"
                    is_en    = st.session_state.library_strategies[lib_idx].get("enabled", False)

                    with st.expander(f"{sig_icon} {strat_name}  ·  {sig}", expanded=False):
                        col_info, col_ctrl = st.columns([3, 1])
                        with col_info:
                            st.markdown(f'<div style="font-size:0.82rem;color:#c4d4ea;">{desc}</div>',
                                        unsafe_allow_html=True)
                            st.markdown(f'<div style="font-size:0.72rem;color:#4a6a8a;margin-top:0.3rem;">👤 Used by: {used_by}</div>',
                                        unsafe_allow_html=True)
                        with col_ctrl:
                            new_en = st.checkbox("Enable on charts",
                                                 value=is_en,
                                                 key=f"lib_en_{lib_idx}")
                            st.session_state.library_strategies[lib_idx]["enabled"] = new_en
                            if st.button("📥 Import to My Strategies",
                                         key=f"lib_import_{lib_idx}"):
                                st.session_state.custom_strategies.append({
                                    "text": text,
                                    "enabled": True,
                                    "category": cat,
                                    "desc": desc,
                                    "used_by": used_by,
                                })
                                st.success(f"Imported '{strat_name}' to My Strategies!")
                                st.rerun()

                        # Show conditions
                        parsed_lib = parse_custom_strategy(text)
                        cond_html  = "  ·  ".join([f"<code style='background:#0a1020;padding:0.1rem 0.4rem;border-radius:4px;color:#38bdf8;font-size:0.73rem;'>{c}</code>"
                                                    for c in parsed_lib["conditions"]])
                        st.markdown(f'<div style="margin-top:0.4rem;">{cond_html}</div>', unsafe_allow_html=True)

                        # Trigger count preview
                        if stock_data and new_en:
                            trigger_preview = []
                            for sym_p, df_p in stock_data.items():
                                bars_p = run_custom_strategy(df_p, parsed_lib)
                                clr_p  = "#34d399" if bars_p else "#475569"
                                trigger_preview.append(
                                    f'<span style="margin-right:1rem;"><b style="color:#dce8f5;">{sym_p}</b>: '
                                    f'<span style="color:{clr_p};">{len(bars_p)} trigger{"s" if len(bars_p)!=1 else ""}</span></span>'
                                )
                            if trigger_preview:
                                st.markdown("**Triggers:** " + " ".join(trigger_preview), unsafe_allow_html=True)

                    lib_idx += 1

            # Quick Enable All / Disable All
            st.markdown("---")
            qa, qb, qc = st.columns(3)
            with qa:
                if st.button("✅ Enable All in Category"):
                    idx2 = 0
                    for c2, s2 in PRO_STRATEGY_LIBRARY.items():
                        for _ in s2:
                            if c2 in shown_cats:
                                st.session_state.library_strategies[idx2]["enabled"] = True
                            idx2 += 1
                    st.rerun()
            with qb:
                if st.button("❌ Disable All"):
                    for s2 in st.session_state.library_strategies:
                        s2["enabled"] = False
                    st.rerun()
            with qc:
                enabled_count = sum(1 for s in st.session_state.library_strategies if s.get("enabled"))
                st.markdown(f'<div class="ins-row">{enabled_count} library strategies currently active on charts</div>',
                            unsafe_allow_html=True)

        # ══════════════════════════════════════════════════════════════════════
        #  MY STRATEGIES TAB
        # ══════════════════════════════════════════════════════════════════════
        with my_tab:
            st.markdown('<div class="sec-title">✏️ My Strategies</div>', unsafe_allow_html=True)
            st.markdown('<div class="ins-row">Import from the Library or create your own. All enabled strategies show on charts.</div>',
                        unsafe_allow_html=True)

            to_delete = []
            for si, cs in enumerate(st.session_state.custom_strategies):
                parsed  = parse_custom_strategy(cs["text"])
                is_sell = parsed["signal"] == "sell"
                sig_icon= "🔴" if is_sell else "🟢"
                cat_lbl = cs.get("category", "Custom")

                with st.expander(
                    f"{sig_icon} {parsed['name']}  ·  {parsed['signal'].upper()}  ·  [{cat_lbl}]  ·  {len(parsed['conditions'])} conditions",
                    expanded=(si == 0)
                ):
                    c_top1, c_top2, c_top3 = st.columns([2, 1, 1])
                    with c_top1:
                        new_en2 = st.checkbox("Enable on charts",
                                              value=cs.get("enabled", True),
                                              key=f"my_en_{si}")
                        st.session_state.custom_strategies[si]["enabled"] = new_en2
                    with c_top2:
                        if st.button("🗑 Delete", key=f"my_del_{si}"):
                            to_delete.append(si)
                    with c_top3:
                        if st.button("📋 Duplicate", key=f"my_dup_{si}"):
                            dup = cs.copy()
                            dup["text"] = dup["text"].replace("Name:", "Name: Copy of", 1)
                            st.session_state.custom_strategies.append(dup)
                            st.rerun()

                    # Description if imported
                    if cs.get("desc"):
                        st.markdown(f'<div style="font-size:0.78rem;color:#8aa0c0;">{cs["desc"]}</div>',
                                    unsafe_allow_html=True)
                    if cs.get("used_by") and cs["used_by"] != "Custom":
                        st.markdown(f'<div style="font-size:0.7rem;color:#4a6a8a;">👤 {cs["used_by"]}</div>',
                                    unsafe_allow_html=True)

                    new_text2 = st.text_area(
                        "Strategy definition (edit freely):",
                        value=cs["text"], height=170,
                        key=f"my_text_{si}",
                    )
                    c_a1, c_a2 = st.columns([1, 3])
                    with c_a1:
                        if st.button("✅ Save Changes", key=f"my_save_{si}"):
                            st.session_state.custom_strategies[si]["text"] = new_text2
                            st.session_state.custom_strategies[si]["category"] = "Custom (edited)"
                            st.success("Saved!")
                            st.rerun()
                    with c_a2:
                        # Live trigger preview
                        if stock_data and new_en2:
                            p_live = parse_custom_strategy(st.session_state.custom_strategies[si]["text"])
                            preview_parts = []
                            for sym_l, df_l in stock_data.items():
                                b_l = run_custom_strategy(df_l, p_live)
                                clr_l = "#34d399" if b_l else "#475569"
                                preview_parts.append(
                                    f'<b style="color:#dce8f5;">{sym_l}</b>: '
                                    f'<span style="color:{clr_l};">{len(b_l)}</span>'
                                )
                            st.markdown("**Triggers:** " + "  ·  ".join(preview_parts), unsafe_allow_html=True)

            for d_idx in sorted(to_delete, reverse=True):
                st.session_state.custom_strategies.pop(d_idx)
            if to_delete: st.rerun()

            # ── Create new strategy ──
            st.markdown("---")
            st.markdown('<div class="sec-title">➕ Create New Strategy</div>', unsafe_allow_html=True)

            help_col, editor_col = st.columns([1, 2])
            with help_col:
                st.markdown(f'<div class="ins-row" style="font-size:0.75rem;">{CUSTOM_STRATEGY_HELP}</div>',
                            unsafe_allow_html=True)
            with editor_col:
                new_strat_text = st.text_area(
                    "Write your strategy:",
                    value="Name: My Strategy\nSignal: BUY\nConditions:\nRSI > 50\nClose > SMA20\nMACD > MACD_Signal",
                    height=180, key="new_strat_input",
                )
                n1, n2 = st.columns(2)
                with n1:
                    if st.button("➕ Add Strategy"):
                        p_new = parse_custom_strategy(new_strat_text)
                        if p_new["conditions"]:
                            st.session_state.custom_strategies.append({
                                "text": new_strat_text,
                                "enabled": True,
                                "category": "Custom",
                                "desc": "",
                                "used_by": "Custom",
                            })
                            st.success(f"Added: {p_new['name']}")
                            st.rerun()
                        else:
                            st.error("No valid conditions found.")
                with n2:
                    if st.button("🔍 Preview"):
                        p_pre = parse_custom_strategy(new_strat_text)
                        st.markdown(f"**Parsed:** `{p_pre['name']}` · `{p_pre['signal']}` · {len(p_pre['conditions'])} conditions")
                        if stock_data:
                            for sym_p2, df_p2 in stock_data.items():
                                b_p2 = run_custom_strategy(df_p2, p_pre)
                                st.markdown(f"**{sym_p2}:** {len(b_p2)} trigger(s)")
                                if b_p2:
                                    render_trigger_log(df_p2, b_p2, p_pre["signal"], p_pre["name"],
                                                       widget_key=f"prev_{sym_p2}")

        # ══════════════════════════════════════════════════════════════════════
        #  INDICATOR REFERENCE TAB
        # ══════════════════════════════════════════════════════════════════════
        with ref_tab:
            st.markdown('<div class="sec-title">📖 Indicator Reference</div>', unsafe_allow_html=True)
            ref_data = {"Alias": list(AVAILABLE_COLS.keys()), "Maps to": list(AVAILABLE_COLS.values())}
            st.dataframe(pd.DataFrame(ref_data), use_container_width=True, hide_index=True)
            st.markdown("""
            <div class="ins-row">
                <b>Operators:</b> <code>&gt;</code> <code>&lt;</code> <code>&gt;=</code> <code>&lt;=</code>
                <code>crosses_above</code> <code>crosses_below</code><br>
                <b>Example:</b> <code>RSI crosses_above 50</code> · <code>Close > SMA20</code> · <code>Vol_Ratio > 1.5</code>
            </div>""", unsafe_allow_html=True)

    # ── COMPARISON TAB ────────────────────────────────────────────────────────
    if len(stock_data)>1:
        with tabs[-1]:
            st.markdown('<div class="sec-title">📋 Multi-Stock Snapshot</div>', unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(all_sum),use_container_width=True,hide_index=True)

            st.markdown('<div class="sec-title">📈 Normalised Price Performance</div>', unsafe_allow_html=True)
            fig_r=go.Figure()
            pal=["#38bdf8","#fbbf24","#34d399","#f87171","#818cf8","#fb923c"]
            for i,(sym,df) in enumerate(stock_data.items()):
                norm=(df["Close"]/df["Close"].iloc[0]-1)*100
                fig_r.add_trace(go.Scatter(x=df["Date"],y=norm,name=sym,
                                           line=dict(color=pal[i%len(pal)],width=2)))
            fig_r.add_hline(y=0,line_dash="dot",line_color="#2d4060")
            fig_r.update_layout(
                template="plotly_dark",paper_bgcolor="#080c18",plot_bgcolor="#0d1525",
                height=380,yaxis_title="Return (%)",
                margin=dict(l=10,r=10,t=30,b=10),
                xaxis=dict(gridcolor="#111e30",tickfont=dict(color="#8aabcb",size=11)),
                yaxis=dict(gridcolor="#111e30",tickfont=dict(color="#8aabcb",size=11)),
                legend=dict(font=dict(size=12,color="#dce8f5"),bgcolor="rgba(0,0,0,0)"),
                font=dict(color="#7a9cc0"),
            )
            st.plotly_chart(fig_r,use_container_width=True)

            st.markdown('<div class="sec-title">🏆 Rankings</div>', unsafe_allow_html=True)
            ra, rb, rc = st.columns(3)

            with ra:
                st.markdown("**By Signal Score**")
                for r in sorted(all_sum, key=lambda x: int(x["Score"]), reverse=True):
                    bc_="b-buy" if "BUY" in r["Classic"] else ("b-sell" if "SELL" in r["Classic"] else "b-neu")
                    st.markdown(f"""<div class="ins-row"><span class="badge {bc_}">{r['Classic']}</span>
                        &nbsp;<b style="color:#e8f4ff;">{r['Symbol']}</b>
                        <span style="color:#4a6a8a;"> · Score {r['Score']}</span></div>""",
                        unsafe_allow_html=True)

            with rb:
                st.markdown("**By Surge Score**")
                for r in sorted(all_sum, key=lambda x: int(x.get("Surge Score","0").replace("+","")), reverse=True):
                    ss = int(r.get("Surge Score","0").replace("+",""))
                    sc_ = "clr-up" if ss > 0 else ("clr-dn" if ss < 0 else "clr-neu")
                    surge_txt = r.get("Surge","N/A")
                    st.markdown(f"""<div class="ins-row">
                        <span class="{sc_}"><b>{surge_txt}</b></span>
                        &nbsp;<b style="color:#e8f4ff;">{r['Symbol']}</b>
                        <span style="color:#4a6a8a;"> · P:{r['Price Trend']} V:{r['Vol Trend']} D:{r['Deliv Trend']}</span>
                    </div>""", unsafe_allow_html=True)

            with rc:
                st.markdown("**By Strategy Signal**")
                for r in sorted(all_sum, key=lambda x:(0 if "BUY" in x["Strategy"] else (2 if "SELL" in x["Strategy"] else 1))):
                    c_="clr-up" if "BUY" in r["Strategy"] else ("clr-dn" if "SELL" in r["Strategy"] else "clr-neu")
                    st.markdown(f"""<div class="ins-row"><span class="{c_}"><b>{r['Strategy']}</b></span>
                        &nbsp;{r['Symbol']} · ₹{r['Fcst ₹']}
                        <span style="color:#4a6a8a;"> ({r['Exp%']})</span></div>""",
                        unsafe_allow_html=True)

            # ── 50/200 DMA Trend comparison ──
            if len(all_sum) >= 2:
                st.markdown('<div class="sec-title">📊 50 / 200 DMA Long-Term Trend</div>', unsafe_allow_html=True)

                # Grouped bar: SMA50 vs SMA200 per stock
                dma_syms, dma_50, dma_200, dma_clrs = [], [], [], []
                for sym, df_s in stock_data.items():
                    last_s   = df_s.iloc[-1]
                    sma50_v  = last_s.get("SMA_50",  np.nan)
                    sma200_v = last_s.get("SMA_200", np.nan)
                    dma_syms.append(sym)
                    dma_50.append(sma50_v if not np.isnan(sma50_v) else None)
                    dma_200.append(sma200_v if not np.isnan(sma200_v) else None)
                    if not np.isnan(sma50_v) and not np.isnan(sma200_v):
                        dma_clrs.append("rgba(52,211,153,0.8)" if sma50_v > sma200_v else "rgba(248,113,113,0.8)")
                    else:
                        dma_clrs.append("rgba(100,116,139,0.5)")

                fig_dma = go.Figure()
                fig_dma.add_trace(go.Bar(
                    name="SMA 50",
                    x=dma_syms, y=dma_50,
                    marker_color=dma_clrs,
                    marker_line_color="rgba(255,255,255,0.2)",
                    marker_line_width=1,
                    text=[f"₹{v:,.0f}" if v else "N/A" for v in dma_50],
                    textposition="outside",
                    textfont=dict(color="#dce8f5", size=10),
                ))
                fig_dma.add_trace(go.Scatter(
                    name="SMA 200",
                    x=dma_syms, y=dma_200,
                    mode="markers",
                    marker=dict(symbol="line-ew", size=20, color="#fbbf24",
                                line=dict(color="#fbbf24", width=3)),
                ))
                fig_dma.update_layout(
                    template="plotly_dark", paper_bgcolor="#080c18", plot_bgcolor="#0d1525",
                    height=340,
                    title=dict(
                        text="SMA50 vs SMA200  ·  Green bar = SMA50 above SMA200 (Bull) · Red = Bear",
                        font=dict(family="Syne", size=13, color="#dce8f5"), x=0.01),
                    legend=dict(font=dict(size=12, color="#dce8f5"),
                                bgcolor="rgba(10,14,26,0.88)", bordercolor="#2a3d55", borderwidth=1),
                    margin=dict(l=10, r=10, t=48, b=10),
                    xaxis=dict(gridcolor="#111e30", tickfont=dict(color="#8aabcb", size=12)),
                    yaxis=dict(gridcolor="#111e30", tickfont=dict(color="#8aabcb", size=11),
                               title="Price ₹", title_font=dict(color="#8aabcb")),
                    font=dict(color="#94afd4"),
                    barmode="group",
                )
                st.plotly_chart(fig_dma, use_container_width=True)

                # DMA Trend status cards
                dma_card_cols = st.columns(len(dma_syms))
                for ci, sym in enumerate(dma_syms):
                    sv50  = dma_50[ci]
                    sv200 = dma_200[ci]
                    if sv50 and sv200:
                        is_bull = sv50 > sv200
                        gap_pct = (sv50 - sv200) / sv200 * 100
                        card_bg  = "rgba(52,211,153,0.07)"  if is_bull else "rgba(248,113,113,0.07)"
                        card_brd = "#34d399" if is_bull else "#f87171"
                        icon     = "🟢" if is_bull else "🔴"
                        label    = "GOLDEN CROSS" if is_bull else "DEATH CROSS"
                        advice   = "Uptrend intact" if is_bull else "Avoid fresh longs"
                        dma_card_cols[ci].markdown(f"""
                        <div style="background:{card_bg};border:1px solid {card_brd};
                             border-radius:10px;padding:0.8rem;text-align:center;">
                            <div style="font-size:1.4rem;">{icon}</div>
                            <div style="font-family:'Syne',sans-serif;font-weight:700;
                                 color:#e8f4ff;font-size:0.85rem;">{sym}</div>
                            <div style="font-size:0.68rem;color:{'#34d399' if is_bull else '#f87171'};
                                 font-weight:600;letter-spacing:1px;">{label}</div>
                            <div style="font-size:0.72rem;color:#8aa0c0;margin-top:0.3rem;">
                                Gap: <b style="color:#e8f4ff;">{gap_pct:+.2f}%</b>
                            </div>
                            <div style="font-size:0.68rem;color:#4a6a8a;margin-top:0.2rem;">{advice}</div>
                        </div>""", unsafe_allow_html=True)
                    else:
                        dma_card_cols[ci].markdown(f"""
                        <div style="background:rgba(100,116,139,0.07);border:1px solid #475569;
                             border-radius:10px;padding:0.8rem;text-align:center;">
                            <div style="font-size:1.4rem;">⚪</div>
                            <div style="font-family:'Syne',sans-serif;font-weight:700;
                                 color:#e8f4ff;font-size:0.85rem;">{sym}</div>
                            <div style="font-size:0.68rem;color:#4a6a8a;">Need 200+ bars</div>
                        </div>""", unsafe_allow_html=True)

            # ── Surge comparison mini-chart ──
            if len(all_sum) >= 2:
                st.markdown('<div class="sec-title">🔥 Surge Score Comparison</div>', unsafe_allow_html=True)
                syms_   = [r["Symbol"] for r in all_sum]
                scores_ = [int(r.get("Surge Score","0").replace("+","")) for r in all_sum]
                dirs_   = [r.get("Surge","") for r in all_sum]
                bar_c_  = ["rgba(52,211,153,0.75)" if s>0 else ("rgba(248,113,113,0.75)" if s<0 else "rgba(100,116,139,0.55)")
                           for s in scores_]
                fig_surge = go.Figure(go.Bar(
                    x=syms_, y=scores_,
                    marker_color=bar_c_,
                    marker_line_color="rgba(255,255,255,0.15)",
                    text=[f"{s:+d}" for s in scores_],
                    textposition="outside",
                    textfont=dict(color="#dce8f5", size=11),
                    customdata=dirs_,
                    hovertemplate="<b>%{x}</b><br>Surge Score: %{y:+d}<br>%{customdata}<extra></extra>",
                ))
                fig_surge.add_hline(y=0, line_dash="solid", line_color="rgba(148,163,184,0.3)", line_width=1)
                fig_surge.add_hrect(y0=3, y1=10, fillcolor="rgba(52,211,153,0.04)", line_width=0)
                fig_surge.add_hrect(y0=-10, y1=-3, fillcolor="rgba(248,113,113,0.04)", line_width=0)
                fig_surge.update_layout(
                    template="plotly_dark", paper_bgcolor="#080c18", plot_bgcolor="#0d1525",
                    height=300,
                    title=dict(text="Surge Score by Stock  (−10 bearish ↔ +10 bullish)",
                               font=dict(family="Syne", size=13, color="#dce8f5"), x=0.01),
                    margin=dict(l=10,r=10,t=45,b=10),
                    yaxis=dict(range=[-11,11], gridcolor="#111e30", tickfont=dict(color="#8aabcb",size=11),
                               zeroline=False),
                    xaxis=dict(gridcolor="#111e30", tickfont=dict(color="#7a9cc0")),
                    font=dict(color="#7a9cc0"),
                    showlegend=False,
                )
                st.plotly_chart(fig_surge, use_container_width=True)

if __name__ == "__main__":
    main()

