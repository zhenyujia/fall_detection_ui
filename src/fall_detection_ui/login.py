import streamlit as st
import os

#st.set_page_config(page_title="Fall Detection System", page_icon=":guardsman:", layout="centered")
def login():
    st.markdown("""
        <style>
        .main {
            background-color: #f0f2f6;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .title {
            font-size: 2rem;
            font-weight: bold;
            color: #4b4b4b;
        }
        .description {
            font-size: 1.2rem;
            color: #6c757d;
            margin-bottom: 2rem;
        }
        .input {
            margin-bottom: 1rem;
        }
        .button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            cursor: pointer;
        }
        .button:hover {
            background-color: #0056b3;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main">', unsafe_allow_html=True)
    st.markdown('<div class="title">Fall Detection System</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="description">Helping to ensure the safety of seniors by detecting falls and sending alerts through email.</div>',
        unsafe_allow_html=True)

    username = st.text_input("Username", key="login_username", placeholder="Enter your username",
                             help="Your unique username")
    password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password",
                             help="Your secure password")

    if st.button("Login", key="login_button", help="Click to login"):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        user_folder = os.path.join(base_dir, "storage", username)
        password_file = os.path.join(user_folder, "password.txt")
        if os.path.exists(password_file):
            with open(password_file, "r") as f:
                saved_password = f.read()
            if password == saved_password:
                st.session_state["logged_in"] = True
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")
        else:
            st.error("Invalid username or password")

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    login()