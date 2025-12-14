import streamlit as st
import requests
import json
import os

st.set_page_config(
    page_title="Loan Risk Assessment",
    page_icon="💼"
)

#streamlit cloud
FLOWISE_API_URL = os.getenv("FLOWISE_API_URL")

if not FLOWISE_API_URL:
    st.error("FLOWISE_API_URL is not set")
    st.stop()
    
print(FLOWISE_API_URL)

def format_loan_response(data: dict) -> str:
    customer = data.get("customer information", {})
    
    lines = [
        "Loan Risk Assessment Result",
        "",
        f"**Customer ID:** {customer.get('id', 'N/A')}",
        f"**Name:** {customer.get('name', 'N/A')}",
        f"**Email:** {customer.get('email', 'N/A').strip()}",
        "",
        f"**Credit Score:** {data.get('credit score', 'N/A')}",
        f"**Account Status:** {data.get('account status', 'N/A')}",
        f"**Nationality:** {data.get('nationality', 'N/A')}",
        f"**PR Status:** {data.get('pr status', 'N/A')}",
        "",
        f"**Overall Risk:** {data.get('overall risk', 'N/A')}",
        f"**Interest Rate:** {data.get('interest rate', 'N/A')}",
        "",
        f"**Recommendation:** {data.get('recommendation', 'N/A')}",
    ]

    return "\n".join(lines)

# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hi, I am G, Loan risk assessment assistant. How can I help you today?"
        }
    ]


# --- Display chat messages ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- User input ---
user_input = st.chat_input("Type your question here...")

if user_input:
    # Show user message in UI
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    # Prepare Flowise payload
    payload = {
        "question": user_input,
        "history": [
            [m["role"], m["content"]]
            for m in st.session_state.messages[:-1] 
        ]
    }

    print(payload)

    # Call Flowise ONLY when user inputs
    with st.spinner("Analyzing loan risk..."):
        response = requests.post(FLOWISE_API_URL, json=payload)

        if response.status_code != 200:
            st.error("Flowise API error")
            st.write(response.text)
            st.stop()

        data = response.json()

    # Format structured JSON to text
    result_text = format_loan_response(data)

    # Save & display assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": result_text}
    )
    st.chat_message("assistant").markdown(result_text)
    st.stop()

    # # Call Flowise
    # with st.spinner("Analyzing loan risk..."):
    #     response = requests.post(FLOWISE_API_URL, json=payload)
    #     result = response.json().get("text", "Sorry, something went wrong.")

    # # Add assistant response
    # st.session_state.messages.append(
    #     {"role": "assistant", "content": result}
    # )
    # st.chat_message("assistant").write(result)

# user_input = st.text_input("Ask something:")

# if st.button("Send") and user_input:
#     payload = {
#         "question": user_input
#     }

#     response = requests.post(FLOWISE_API_URL, json=payload)

#     if response.status_code == 200:
#         result = response.json()
#         st.markdown("### Agent Response")
#         st.write(result["text"])
#     else:
#         st.error("Failed to get response from Flowise")