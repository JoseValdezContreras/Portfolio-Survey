import streamlit as st
import pandas as pd
import re
from datetime import datetime

st.set_page_config(layout="wide", page_icon="📊", page_title="Portfolio Feedback")

# ─── Configuration ───────────────────────────────────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/1uAU0MQ1P8j_zY7BFudHjSXJBd-FzB3WnRszucn93PJs/edit?usp=sharing"
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfK7K6v-JIzL2puZ3g8U-xEysbBq-AS19guYMFqCFnYrc4BSQ/viewform?embedded=true"  # Add your Google Form URL here
CSV_URL = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

# Profanity filter - add/remove words as needed
PROFANITY_LIST = [
    'damn', 'hell', 'shit', 'fuck', 'ass', 'bitch', 'bastard', 'crap',
    'piss', 'dick', 'pussy', 'cock', 'whore', 'slut', 'fag', 'nigger',
    'cunt', 'twat', 'bollocks', 'wanker', 'arse'
]

# Column names from your Google Form (exact match)
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
        # Replace profanity with asterisks (keep first letter)
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        if pattern.search(text_lower):
            replacement = word[0] + '*' * (len(word) - 1)
            cleaned = pattern.sub(replacement, cleaned)
    
    return cleaned


@st.cache_data(ttl=60)  # Refresh every 60 seconds
def load_data():
    """Load data from public Google Sheet with error handling."""
    try:
        df = pd.read_csv(CSV_URL, timeout=10)
        return df, None
    except Exception as e:
        error_msg = str(e)
        return pd.DataFrame(), error_msg


# ─── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main {
        background-color: #0a0e1a;
    }
    h1 {
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, sans-serif;
    }
    h2, h3 {
        color: #cbd5e1;
    }
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
    ### 🔒 Network Restrictions or Connection Issue
    
    This dashboard displays live feedback from my portfolio's Google Form, but it looks like 
    there's a connection problem. This could be due to:
    
    - 🏢 **Corporate network restrictions** (blocking Google services)
    - 🌐 **Firewall or proxy settings**
    - 🔌 **Temporary connectivity issues**
    - 🛡️ **VPN or security software**
    
    ### 📋 You can still submit feedback directly:
    """)
    
    # Prominent call-to-action button
    st.markdown(f"""
    <a href="{FORM_URL}" target="_blank">
        <button style="
            background: linear-gradient(135deg, #00e676 0%, #00c853 100%);
            color: white;
            padding: 16px 32px;
            font-size: 18px;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0, 230, 118, 0.3);
            transition: all 0.3s ease;
        ">
            📝 Open Feedback Form
        </button>
    </a>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    with st.expander("🛠️ Troubleshooting for Network Admins"):
        st.markdown(f"""
        **If you're seeing this on a corporate network:**
        
        1. **Required domains to whitelist:**
           - `docs.google.com`
           - `sheets.googleapis.com`
        
        2. **Test the connection:**
           - Try accessing this URL directly: `{CSV_URL}`
           - If it downloads a CSV file, the issue is with Streamlit
           - If it shows an error, Google Sheets is blocked
        
        3. **Alternative:**
           - Access from a personal device/network
           - Use mobile data instead of corporate WiFi
           - Connect via VPN to a different location
        
        **Error details:** `{error}`
        """)
    
    st.stop()  # Stop execution if no data


# ─── Data Processing ─────────────────────────────────────────────────────────
# Clean column names (strip whitespace)
df.columns = df.columns.str.strip()

# Verify columns exist
required_cols = [COL_SEEN_FORM, COL_RATING, COL_SUGGESTIONS]
missing_cols = [col for col in required_cols if col not in df.columns]

if missing_cols:
    st.warning(f"⚠️ Missing expected columns: {missing_cols}")
    with st.expander("🔍 Available Columns"):
        st.write(df.columns.tolist())
    st.stop()

# Convert rating to numeric
df[COL_RATING] = pd.to_numeric(df[COL_RATING], errors='coerce')

# Clean suggestions (profanity filter)
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
    st.subheader("📋 Have you seen a Google Form on a portfolio?")
    
    # Count Yes/No responses
    form_counts = df[COL_SEEN_FORM].str.lower().str.strip().value_counts()
    
    # Create clean labels
    form_data = pd.DataFrame({
        'Response': ['Yes', 'No'],
        'Count': [
            form_counts.get('yes', 0),
            form_counts.get('no', 0)
        ]
    })
    
    # Display as bar chart
    st.bar_chart(form_data.set_index('Response'))
    
    # Show percentages
    total = len(df)
    yes_pct = (form_data[form_data['Response'] == 'Yes']['Count'].values[0] / total * 100) if total > 0 else 0
    no_pct = (form_data[form_data['Response'] == 'No']['Count'].values[0] / total * 100) if total > 0 else 0
    
    st.caption(f"✅ Yes: {yes_pct:.1f}% | ❌ No: {no_pct:.1f}%")

with col_right:
    st.subheader("⭐ Rating Distribution (1-10)")
    
    # Get rating distribution
    rating_counts = df[COL_RATING].value_counts().sort_index()
    
    # Ensure all ratings 1-10 are represented
    all_ratings = pd.Series(0, index=range(1, 11))
    all_ratings.update(rating_counts)
    
    st.bar_chart(all_ratings)
    
    # Show stats
    ratings = df[COL_RATING].dropna()
    if len(ratings) > 0:
        st.caption(f"📊 Min: {ratings.min():.0f} | Median: {ratings.median():.1f} | Max: {ratings.max():.0f}")

# ─── Rating Trend Over Time ──────────────────────────────────────────────────
if 'Timestamp' in df.columns and len(df) > 1:
    st.markdown("---")
    st.subheader("📈 Rating Trend Over Time")
    
    df_time = df[['Timestamp', COL_RATING]].copy()
    df_time['Timestamp'] = pd.to_datetime(df_time['Timestamp'])
    df_time = df_time.sort_values('Timestamp')
    df_time = df_time.set_index('Timestamp')
    
    st.line_chart(df_time[COL_RATING])

# ─── Suggestions Section ─────────────────────────────────────────────────────
st.markdown("---")
st.subheader("💬 Recent Suggestions")

# Filter out empty suggestions
suggestions_df = df[df['suggestions_clean'].str.strip() != ''].copy()

if len(suggestions_df) > 0:
    # Sort by timestamp if available
    if 'Timestamp' in suggestions_df.columns:
        suggestions_df['Timestamp'] = pd.to_datetime(suggestions_df['Timestamp'])
        suggestions_df = suggestions_df.sort_values('Timestamp', ascending=False)
    
    # Show most recent 15 suggestions
    for idx, row in suggestions_df.head(15).iterrows():
        suggestion = row['suggestions_clean']
        
        # Format timestamp if available
        if 'Timestamp' in row and pd.notna(row['Timestamp']):
            timestamp = pd.to_datetime(row['Timestamp']).strftime('%B %d, %Y at %I:%M %p')
            timestamp_html = f'<div class="timestamp">📅 {timestamp}</div>'
        else:
            timestamp_html = ''
        
        # Display suggestion card
        st.markdown(f"""
        <div class="suggestion-card">
            {timestamp_html}
            <div class="suggestion-text">"{suggestion}"</div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("💡 No suggestions yet. Be the first to share your thoughts!")
    st.markdown(f"""
    <a href="{FORM_URL}" target="_blank">
        <button style="
            background: #00e676;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
        ">
            Submit Feedback
        </button>
    </a>
    """, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption(f"🔄 Last updated: {datetime.now().strftime('%I:%M:%S %p')} • Auto-refreshes every 60 seconds")

# Add form link in footer
st.markdown(f"""
<div style="text-align: center; padding: 20px;">
    <a href="{FORM_URL}" target="_blank" style="color: #00e676; text-decoration: none;">
        📝 Submit your own feedback →
    </a>
</div>
""", unsafe_allow_html=True)

# ─── Debug Info (Collapsible) ────────────────────────────────────────────────
with st.expander("🔧 Debug Information"):
    st.write("**Total Rows:**", len(df))
    st.write("**Columns:**", df.columns.tolist())
    st.write("**Data Types:**")
    st.write(df.dtypes)
    st.write("**Sample Data:**")
    st.dataframe(df.head(3))


