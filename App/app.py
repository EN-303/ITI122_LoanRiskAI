import streamlit as st
import requests
import json
import os

#FLOWISE_API_URL = os.getenv("FLOWISE_API_URL")
#FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY")

st.set_page_config(page_title="Loan Risk Assessment", layout="centered")
st.title("🏦 Loan Risk Assessment Assistant")

st.subheader("Customer Input")
customer_id = st.text_input("Customer ID")
customer_name = st.text_input("Customer Name")