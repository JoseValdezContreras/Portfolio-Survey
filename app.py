import streamlit as st
   from streamlit_gsheets import GSheetsConnection  ✅
st.set_page_config(layout="centered")

st.title("📊 Community Insights")

# Link to your Google Sheet (from your Google Form)
# Replace this with your actual sheet URL
url = "https://docs.google.com/spreadsheets/d/1uAU0MQ1P8j_zY7BFudHjSXJBd-FzB3WnRszucn93PJs/edit?usp=sharing"

conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(spreadsheet=url)

if not df.empty:
    # 1. Metric Row
    col1, col2 = st.columns(2)
    col1.metric("Total Responses", len(df))
    avg_rating = df['Rate the interactivity (1-10)'].mean()
    col2.metric("Avg. Interactivity Score", f"{avg_rating:.1f}/10")

    # 2. Visualization
    st.write("#### Audience Expertise")
    st.bar_chart(df['primary area of expertise'].value_counts())
else:

    st.info("Waiting for the first response!")

