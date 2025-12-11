import streamlit as st
from menu import authenticated_menu, home_menu
import openpyxl
from openpyxl import load_workbook
from datetime import datetime

# Create an empty container
placeholder = st.empty()

#actual_email = "email"
actual_password = "ileague2025.epa"

# Insert a form in the container
with placeholder.form("login"):
    st.markdown("#### Halo! Selamat datang kembali.")
    email = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

if submit and password == actual_password:
    # If the form is submitted and the email and password are correct,
    # clear the form/container and display a success message
    placeholder.empty()
    home_menu()
    st.success("Login successful")
    #authenticated_menu()
elif submit and password != actual_password:
    st.error("Login failed")
else:
    pass
