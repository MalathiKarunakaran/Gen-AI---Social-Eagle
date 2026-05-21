import streamlit as st
st.title("My First Streamlit app")
name = st.text_input("Enter your name")

if st.button("Say Hello"):
    if name:
        st.success(f"hello {name}, welcome to my page")
    else:
        st.warning("Please enter your name")