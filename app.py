import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

st.set_page_config(layout="centered", page_icon="📊")
st.title("📊 Community Insights")

# ─── Google Sheets Connection ────────────────────────────────────────────────
@st.cache_resource
def get_gsheet_data():
    """Fetch data from Google Sheets using gspread."""
    try:
        # Define the scope
        scope = [
            "https://www.googleapis.com/auth/spreadsheets.readonly",
            "https://www.googleapis.com/auth/drive.readonly"
        ]
        
        # Try to get credentials from Streamlit secrets
        try:
            credentials = Credentials.from_service_account_info(
                st.secrets["gcp_service_account"],
                scopes=scope
            )
        except:
            # Fallback: Try loading from local file (for development)
            credentials = Credentials.from_service_account_file(
                "service_account.json",
                scopes=scope
            )
        
        # Authorize and open the sheet
        client = gspread.authorize(credentials)
        
        # Your Google Sheet URL
        sheet_url = "https://docs.google.com/spreadsheets/d/1uAU0MQ1P8j_zY7BFudHjSXJBd-FzB3WnRszucn93PJs/edit?usp=sharing"
        
        # Open the spreadsheet
        spreadsheet = client.open_by_url(sheet_url)
        
        # Get the first worksheet (usually "Form Responses 1")
        worksheet = spreadsheet.get_worksheet(0)
        
        # Get all values
        data = worksheet.get_all_values()
        
        if len(data) > 0:
            # First row is headers
            headers = data[0]
            rows = data[1:]
            df = pd.DataFrame(rows, columns=headers)
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error connecting to Google Sheets: {str(e)}")
        return pd.DataFrame()

# Fetch data with caching (updates every 5 minutes)
df = get_gsheet_data()

if not df.empty:
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Show column names for debugging
    with st.expander("🔍 Available Columns (for debugging)"):
        st.write(df.columns.tolist())
        st.write(f"Total rows: {len(df)}")
    
    # ─── Metrics ─────────────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("📝 Total Responses", len(df))
    
    # Try to find and calculate rating
    rating_col = None
    for col in df.columns:
        if 'rate' in col.lower() and ('interactivity' in col.lower() or '1-10' in col.lower()):
            rating_col = col
            break
    
    with col2:
        if rating_col:
            # Convert to numeric, handling any non-numeric values
            ratings = pd.to_numeric(df[rating_col], errors='coerce')
            avg_rating = ratings.mean()
            if pd.notna(avg_rating):
                st.metric("⭐ Avg. Interactivity", f"{avg_rating:.1f}/10")
            else:
                st.metric("⭐ Avg. Interactivity", "N/A")
        else:
            st.metric("⭐ Avg. Interactivity", "Column not found")
    
    st.divider()
    
    # ─── Visualizations ──────────────────────────────────────────────────────
    st.write("### 👥 Audience Expertise")
    
    # Find expertise column
    expertise_col = None
    for col in df.columns:
        if 'expertise' in col.lower() or 'area' in col.lower():
            expertise_col = col
            break
    
    if expertise_col:
        # Count values and create chart
        expertise_counts = df[expertise_col].value_counts()
        
        if len(expertise_counts) > 0:
            st.bar_chart(expertise_counts)
            
            # Show detailed breakdown
            with st.expander("📊 Detailed Breakdown"):
                for area, count in expertise_counts.items():
                    percentage = (count / len(df)) * 100
                    st.write(f"**{area}**: {count} responses ({percentage:.1f}%)")
        else:
            st.info("No expertise data yet")
    else:
        st.warning("⚠️ Could not find 'expertise' column in your form responses")
        st.write("Make sure your Google Form has a question about expertise/area")
    
    # ─── Rating Distribution ─────────────────────────────────────────────────
    if rating_col:
        st.write("### ⭐ Rating Distribution")
        ratings = pd.to_numeric(df[rating_col], errors='coerce').dropna()
        
        if len(ratings) > 0:
            rating_counts = ratings.value_counts().sort_index()
            st.bar_chart(rating_counts)
            
            with st.expander("📈 Rating Stats"):
                st.write(f"**Highest Rating**: {ratings.max():.0f}")
                st.write(f"**Lowest Rating**: {ratings.min():.0f}")
                st.write(f"**Median Rating**: {ratings.median():.1f}")
                st.write(f"**Total Ratings**: {len(ratings)}")
    
    # ─── Raw Data (optional) ─────────────────────────────────────────────────
    with st.expander("📄 View Raw Data"):
        st.dataframe(df, use_container_width=True)
    
    # Auto-refresh hint
    st.caption("💡 This page caches data for 5 minutes. Refresh the browser to force update.")

else:
    st.info("⏳ Waiting for the first response! Share your Google Form to start collecting data.")
    
    with st.expander("❓ Troubleshooting"):
        st.write("""
        If you're seeing this message and have responses:
        
        1. **Check your service account setup:**
           - Make sure you've created a service account in Google Cloud
           - Downloaded the JSON key file
           - Shared your Google Sheet with the service account email
        
        2. **Verify your secrets (on Streamlit Cloud):**
           - Go to your app settings
           - Click "Secrets"
           - Make sure your service account JSON is properly formatted
        
        3. **For local development:**
           - Save your service account JSON as `service_account.json`
           - Place it in the same folder as this app
        """)
