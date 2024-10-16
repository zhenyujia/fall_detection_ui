import streamlit as st
from fall_detection_ui.login import login
from fall_detection_ui.register import register


st.set_page_config(page_title="Fall Detection System", page_icon=":guardsman:", layout="centered")

# Check if the user is logged in
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

# Check if the user is on the register page
if "on_register_page" not in st.session_state:
    st.session_state["on_register_page"] = False

def show_register():
    st.session_state["on_register_page"] = True

if not st.session_state["logged_in"]:
    if st.session_state["on_register_page"]:
        register()
    else:
        st.sidebar.button("Register", key="register_button", on_click=show_register)
        login()
else:

    st.logo("images/icons8-menu-48.png", icon_image="images/icons8-menu-48.png")

    pages = {
        "Custom View": [
            st.Page("user/real_time.py", title="condition"),
            st.Page("user/video_demo.py", title="video demos")
        ],
        "Developer View": [
            st.Page("developer/conv2d_lstm.py", title="conv2d lstm model"),
            st.Page("developer/conv3d.py", title="3D Cov Model")
        ]
    }

    pg = st.navigation(pages)
    pg.run()