import streamlit as st

st.set_page_config(page_title="North Bengal Research App")
st.title("North Bengal Research App")
st.write("This is the first version of my research app for Darjeeling, Kalimpong, Jalpaiguri, and Alipurduar.")

question = st.text_input("Enter your research question")
if st.button("Search"):
    st.write("You asked:", question)
