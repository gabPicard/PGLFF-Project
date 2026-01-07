import streamlit as st

st.set_page_config(
    page_title="Main Menu",
    page_icon="📘",
    layout="centered",
)

st.title("Main Menu")
st.markdown("---")

st.header("Choose a section")

st.page_link(
    "pages/SingleAsset.py",
    label="Single Asset Analysis (Quant A)",
    icon="📊"
)

st.page_link(
    "pages/Portfolio.py",
    label="Portfolio Analysis (Quant B)",
    icon="🧮"
)

st.page_link(
    "pages/Settings.py",
    label="Settings & Configuration",
    icon="⚙️"
)

st.markdown("---")
st.header("Project by")

st.write("**Gabriel PICARD**")  
st.write("**Alex THEAGENE**")  
st.write("**Python, Git, Linux for Finance**  \nIF5")

st.markdown("---")

