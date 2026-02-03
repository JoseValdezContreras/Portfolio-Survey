import streamlit as st
import pandas as pd

st.set_page_config(layout="centered", page_icon="📊")
st.title("📊 Community Insights")

# Your Google Sheet URL - just paste it here
SHEET_URL = "https://docs.google.com/spreadsheets/d/1uAU0MQ1P8j_zY7BFudHjSXJBd-FzB3WnRszucn93PJs/edit?usp=sharing"

# Convert to CSV export URL
csv_url = SHEET_URL.replace('/edit?usp=sharing', '/export?format=csv')

@st.cache_data(ttl=60)  # Refresh every 60 seconds
def load_data():
    return pd.read_csv(csv_url)

# Load data
df = load_data()

if not df.empty:
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # ─── Metrics ─────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    col1.metric("📝 Total Responses", len(df))
    
    # Find rating column
    rating_col = None
    for col in df.columns:
        if 'rate' in col.lower() and 'interactivity' in col.lower():
            rating_col = col
            break
    
    if rating_col:
        avg_rating = pd.to_numeric(df[rating_col], errors='coerce').mean()
        col2.metric("⭐ Avg Interactivity", f"{avg_rating:.1f}/10")
    
    st.divider()
    
    # ─── Expertise Chart ─────────────────────────────────────────────────
    st.write("### 👥 Audience Expertise")
    
    expertise_col = None
    for col in df.columns:
        if 'expertise' in col.lower() or 'area' in col.lower():
            expertise_col = col
            break
    
    if expertise_col:
        st.bar_chart(df[expertise_col].value_counts())
    
    # ─── Rating Distribution ─────────────────────────────────────────────
    if rating_col:
        st.write("### ⭐ Rating Distribution")
        ratings = pd.to_numeric(df[rating_col], errors='coerce').dropna()
        st.bar_chart(ratings.value_counts().sort_index())
    
    st.caption("🔄 Auto-refreshes every minute")

else:
    st.error("Could not load data. Make sure your sheet is public!")
