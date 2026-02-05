import streamlit as st
import pandas as pd
import re
from datetime import datetime
import time

st.set_page_config(layout="wide", page_icon="📊", page_title="Portfolio Feedback")

# ─── Configuration ───────────────────────────────────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/1uAU0MQ1P8j_zY7BFudHjSXJBd-FzB3WnRszucn93PJs/edit?usp=sharing"
CSV_URL = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')
# Define your form URL here for the fallback button
FORM_URL = "https://docs.google.com/forms/d/e/YOUR_FORM_ID/viewform" 

PROFANITY_LIST = [
    'damn', 'hell', 'shit', 'fuck', 'ass', 'bitch', 'bastard', 'crap',
    'piss', 'dick', 'pussy', 'cock', 'whore', 'slut', 'fag', 'nigger',
    'cunt', 'twat', 'bollocks', 'wanker', 'arse'
]

COL_SEEN_FORM = "Have you ever seen a google form on a Portfolio?"
COL_RATING = "Rate the Interactivity of the Dashboards from 1-10"
COL_SUGGESTIONS = "Do you have any suggestions on what I should add to my portfolio?"

# ─── Helper Functions ────────────────────────────────────────────────────────
def clean_text(text):
    if pd.isna(text) or text == "":
        return ""
    text_lower = text.lower()
    cleaned = text
    for word in PROFANITY_LIST:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(text_lower):
            replacement = word[0] + '*' * (len(word) - 1)
            cleaned = pattern.sub(replacement, cleaned)
    return cleaned

@st.cache_data(ttl=60) # Syncs with the fragment timer
def load_data():
    try:
        df = pd.read_csv(CSV_URL)
        return df, None
    except Exception as e:
        return pd.DataFrame(), str(e)

# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a0e1a; }
    h1 { color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; }
    .suggestion-card {
        background: #1a1d27;
        border-left: 3px solid #00e676;
        padding: 16px;
        margin: 12px 0;
        border-radius: 6px;
    }
    .suggestion-text { color: #e2e8f0; font-size: 1rem; line-height: 1.6; }
    .timestamp { color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px; }
    [data-testid="stMetricValue"] { font-size: 2rem; color: #00e676; }
</style>
""", unsafe_allow_html=True)

# ─── Header (Static) ─────────────────────────────────────────────────────────
st.title("📊 Portfolio Feedback Dashboard")
st.markdown("Real-time insights from visitor responses (Auto-refreshes every 60s)")

# ─── Fragmented Content ──────────────────────────────────────────────────────
@st.fragment(run_every="60s")
def render_dashboard():
    df, error = load_data()

    if error or df.empty:
        st.error("⚠️ Unable to connect to Google Sheets")
        st.markdown(f"""
        <div style="text-align: center; margin: 30px 0;">
            <a href="{FORM_URL}" target="_blank">
                <button style="background: #00e676; color: white; padding: 18px; border: none; border-radius: 8px; cursor: pointer;">
                    📝 Submit Feedback Anyway
                </button>
            </a>
        </div>
        """, unsafe_allow_html=True)
        return

    # Data Processing
    df.columns = df.columns.str.strip()
    df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors='coerce')
    df['suggestions_clean'] = df[COL_SUGGESTIONS].fillna('').apply(clean_text)

    # Key Metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("📝 Total Responses", len(df))
    with m2: 
        avg = df[COL_RATING].mean()
        st.metric("⭐ Avg Rating", f"{avg:.1f}/10" if pd.notna(avg) else "N/A")
    with m3:
        unique_count = (df[COL_SEEN_FORM].str.lower().str.strip() == 'No but it is actually pretty cool').sum()
        unique_pct = (unique_count / len(df) * 100) if len(df) > 0 else 0
        st.metric("Form Uniqueness", f"{unique_pct:.0f}%")
    with m4:
        s_count = (df['suggestions_clean'].str.strip() != '').sum()
        st.metric("💬 Suggestions", s_count)

    st.markdown("---")

    # Visualizations
    col_left, col_right = st.columns(2)
    with col_left:
        st.subheader("📋 Seen Google Form on Portfolio?")
        form_counts = df[COL_SEEN_FORM].str.lower().str.strip().value_counts()
        form_data = pd.DataFrame({'Response': ['No but it is actually pretty cool', 'Yes, I am unfazed but good job anyway'], 'Count': [form_counts.get('No but it is actually pretty cool', 0), form_counts.get('Yes, I am unfazed but good job anyway', 0)]})
        st.bar_chart(form_data.set_index('Response'))

    with col_right:
        st.subheader("⭐ Rating Distribution")
        rating_counts = df[COL_RATING].value_counts().sort_index()
        all_ratings = pd.Series(0, index=range(1, 11))
        all_ratings.update(rating_counts)
        st.bar_chart(all_ratings)

    # Suggestions Section
    st.markdown("---")
    st.subheader("💬 Recent Suggestions")
    s_df = df[df['suggestions_clean'].str.strip() != ''].copy()
    if not s_df.empty:
        for _, row in s_df.tail(10).iterrows():
            st.markdown(f"""<div class="suggestion-card"><div class="suggestion-text">"{row['suggestions_clean']}"</div></div>""", unsafe_allow_html=True)
    
    st.caption(f"🔄 Last updated: {datetime.now().strftime('%I:%M:%S %p')}")

# Execute the fragment
render_dashboard()





