import streamlit as st

with st.sidebar:
    st.write()
    with st.container(border=True):
        sensitivity_threshold = st.slider("Sensitivity Threshold", 0.0, 1.0, 0.5)

