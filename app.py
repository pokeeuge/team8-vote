import streamlit as st
import pandas as pd

st.title("👋 Hello Streamlit")
st.write("這是一個簡單的資料呈現範例")

uploaded_file = st.file_uploader("請上傳 Excel 檔案", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("上傳成功，內容如下：")
    st.dataframe(df)
