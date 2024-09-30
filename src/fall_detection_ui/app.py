import os
import sys

import streamlit as st
from loguru import logger


st.title("Falling Detection System")

st.logo("images/icons8-menu-48.png", icon_image="images/icons8-menu-48.png")


pages = {
    "Custom View": [
        st.Page("user/real_time.py", title="real time"),
        st.Page("user/video_demo.py", title="demo")
    ],
    "Developer View":[
        st.Page("developer/conv2d_lstm.py", title="conv2d lstm model"),
        st.Page("developer/conv3d.py", title="3D Cov Model")
    ]
}
with st.sidebar:
    st.write()
    with st.container(border=True):
        sensitivity_threshold = st.slider("Sensitivity Threshold", 0.0, 1.0, 0.5)

pg = st.navigation(pages)
pg.run()

