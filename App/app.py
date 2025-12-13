import streamlit as st
import requests
import json
#from dotenv import load_dotenv
import os

#load_dotenv("env.txt")
FLOWISE_API_URL = os.getenv("FLOWISE_API_URL")
#FLOWISE_API_KEY = os.getenv("FLOWISE_API_KEY")

#FLOWISE_API_URL = "https://cloud.flowiseai.com/api/v1/prediction/dfcfa804-49e4-41ad-a770-a41cb82029d9"

st.set_page_config(page_title="Loan Risk Assessment", layout="centered")
st.title("🏦 Loan Risk Assessment Assistant")

#st.subheader("Customer Input")
#customer_id = st.text_input("Customer ID")
#customer_name = st.text_input("Customer Name")

user_input = st.text_input("Ask something:")

if st.button("Send") and user_input:
    payload = {
        "question": user_input
    }

    response = requests.post(FLOWISE_API_URL, json=payload)

    if response.status_code == 200:
        result = response.json()
        st.markdown("### Agent Response")
        st.write(result["text"])
    else:
        st.error("Failed to get response from Flowise")