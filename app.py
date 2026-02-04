import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(layout="wide", page_icon="📊", page_title="Portfolio Feedback")

# ─── Configuration ───────────────────────────────────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/1uAU0MQ1P8j_zY7BFudHjSXJBd-FzB3WnRszucn93PJs/edit?usp=sharing"
CSV_URL = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

# Profanity filter
PROFANITY_LIST = [
    'damn', 'hell', 'shit', 'fuck', 'ass', 'bitch', 'bastard', 'crap',
    'piss', 'dick', 'pussy', 'cock', 'whore', 'slut', 'fag', 'nigger',
    'cunt', 'twat', 'bollocks', 'wanker', 'arse'
]

# Column names (exact match from Google Form)
COL_SEEN_FORM = "Have you ever seen a google form on a Portfolio?"
COL_RATING = "Rate the Interactivity of the Dashboards from 1-10"
COL_SUGGESTIONS = "Do you have any suggestions on what I should add to my portfolio?"


# ─── Helper Functions ────────────────────────────────────────────────────────
def clean_text(text):
    """Remove or mask profanity from text."""
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


@st.cache_data(ttl=60)  # Refresh every 60 seconds
def load_data():
    """Load data from public Google Sheet with error handling."""
    try:
        df = pd.read_csv(CSV_URL)
        return df, None
    except Exception as e:
        error_msg = str(e)
        return pd.DataFrame(), error_msg


# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0a0e1a; }
    h1 { color: #e2e8f0; font-family: 'Inter', -apple-system, sans-serif; }
    h2, h3 { color: #cbd5e1; }
    .suggestion-card {
        background: #1a1d27;
        border-left: 3px solid #00e676;
        padding: 16px;
        margin: 12px 0;
        border-radius: 6px;
    }
    .suggestion-text {
        color: #e2e8f0;
        font-size: 1rem;
        line-height: 1.6;
    }
    .timestamp {
        color: #94a3b8;
        font-size: 0.85rem;
        margin-bottom: 8px;
    }
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #00e676;
    }
</style>
""", unsafe_allow_html=True)


# ─── Header ──────────────────────────────────────────────────────────────────
st.title("📊 Portfolio Feedback Dashboard")
st.markdown("Real-time insights from visitor responses")

# ─── Load Data ───────────────────────────────────────────────────────────────
df, error = load_data()

# ─── Network/Connection Failsafe ─────────────────────────────────────────────
if error or df.empty:
    st.error("⚠️ Unable to connect to Google Sheets")
    
    st.markdown("""
    ### 🔒 Connection Issue Detected
    
    The dashboard cannot load data right now. This is most likely because:
    
    **📋 The Google Sheet needs to be made public:**
    1. Open the [response sheet](https://docs.google.com/spreadsheets/d/1uAU0MQ1P8j_zY7BFudHjSXJBd-FzB3WnRszucn93PJs/edit?usp=sharing)
    2. Click "Share" (top right)
    3. Change to "Anyone with the link" → **Viewer**
    4. Click "Done"
    
    **OR you're on a restricted network:**
    - Corporate firewall blocking Google services
    - VPN or proxy interference
    - Network admin restrictions
    """)
    
    st.markdown(f"""
    <div style="text-align: center; margin: 30px 0;">
        <a href="{FORM_URL}" target="_blank">
            <button style="
                background: linear-gradient(135deg, #00e676 0%, #00c853 100%);
                color: white;
                padding: 18px 36px;
                font-size: 18px;
                font-weight: 600;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 4px 12px rgba(0, 230, 118, 0.3);
            ">
                📝 Submit Feedback Anyway
            </button>
        </a>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("🔍 Technical Details"):
        st.code(f"Error: {error}")
        st.code(f"Attempting to fetch: {CSV_URL}")
    
    st.stop()


# ─── Data Processing ─────────────────────────────────────────────────────────
df.columns = df.columns.str.strip()

required_cols = [COL_SEEN_FORM, COL_RATING, COL_SUGGESTIONS]
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.warning(f"⚠️ Missing expected columns: {missing_cols}")
    with st.expander("🔍 Available Columns"):
        st.write(df.columns.tolist())
    st.stop()

df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors='coerce')
df['suggestions_clean'] = df[COL_SUGGESTIONS].fillna('').apply(clean_text)

# ─── Key Metrics ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📝 Total Responses", len(df))

with col2:
    avg_rating = df[COL_RATING].mean()
    st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/10" if pd.notna(avg_rating) else "N/A")

with col3:
    yes_count = (df[COL_SEEN_FORM].str.lower().str.strip() == 'yes').sum()
    yes_pct = (yes_count / len(df) * 100) if len(df) > 0 else 0
    st.metric("👀 Seen Form Before", f"{yes_pct:.0f}%")

with col4:
    suggestion_count = (df['suggestions_clean'].str.strip() != '').sum()
    st.metric("💬 Suggestions", suggestion_count)

st.markdown("---")

# ─── Visualizations ──────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📋 Seen Google Form on Portfolio?")
    
    form_counts = df[COL_SEEN_FORM].str.lower().str.strip().value_counts()
    form_data = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Count': [form_counts.get('yes', 0), form_counts.get('no', 0)]
    })
    
    st.bar_chart(form_data.set_index('Response'))
    
    total = len(df)
    yes_pct = (form_data[form_data['Response'] == 'Yes']['Count'].values[0] / total * 100) if total > 0 else 0
    no_pct = (form_data[form_data['Response'] == 'No']['Count'].values[0] / total * 100) if total > 0 else 0
    st.caption(f"✅ Yes: {yes_pct:.1f}% | ❌ No: {no_pct:.1f}%")

with col_right:
    st.subheader("⭐ Rating Distribution (1-10)")
    
    rating_counts = df[COL_RATING].value_counts().sort_index()
    all_ratings = pd.Series(0, index=range(1, 11))
    all_ratings.update(rating_counts)
    
    st.bar_chart(all_ratings)
    
    ratings = df[COL_RATING].dropna()
    if len(ratings) > 0:
        st.caption(f"📊 Min: {ratings.min():.0f} | Median: {ratings.median():.1f} | Max: {ratings.max():.0f}")

# ─── Rating Trend ────────────────────────────────────────────────────────────
if 'Timestamp' in df.columns and len(df) > 1:
    st.markdown("---")
    st.subheader("📈 Rating Trend Over Time")
    
    df_time = df[['Timestamp', COL_RATING]].copy()
    df_time['Timestamp'] = pd.to_datetime(df_time['Timestamp'])
    df_time = df_time.sort_values('Timestamp')
    df_time = df_time.set_index('Timestamp')
    
    st.line_chart(df_time[COL_RATING])

# ─── Suggestions ─────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💬 Recent Suggestions")

suggestions_df = df[df['suggestions_clean'].str.strip() != ''].copy()

if len(suggestions_df) > 0:
    if 'Timestamp' in suggestions_df.columns:
        suggestions_df['Timestamp'] = pd.to_datetime(suggestions_df['Timestamp'])
        suggestions_df = suggestions_df.sort_values('Timestamp', ascending=False)
    
    for idx, row in suggestions_df.head(15).iterrows():
        suggestion = row['suggestions_clean']
        
        if 'Timestamp' in row and pd.notna(row['Timestamp']):
            timestamp = pd.to_datetime(row['Timestamp']).strftime('%B %d, %Y at %I:%M %p')
            timestamp_html = f'<div class="timestamp">📅 {timestamp}</div>'
        else:
            timestamp_html = ''
        
        st.markdown(f"""
        <div class="suggestion-card">
            {timestamp_html}
            <div class="suggestion-text">"{suggestion}"</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("💡 No suggestions yet. Be the first to share your thoughts!")

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(f"🔄 Last updated: {datetime.now().strftime('%I:%M:%S %p')} • Refreshes every 60 seconds")
