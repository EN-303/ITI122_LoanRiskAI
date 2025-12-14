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

def build_flowise_history(messages):
    history = []
    for m in messages:
        if m["role"] == "user":
            history.append({
                "role": "userMessage",
                "content": m["content"]
            })
        elif m["role"] == "assistant":
            history.append({
                "role": "apiMessage",
                "content": m["content"]
            })
    return history

def format_loan_response(data: dict) -> str:
    customer = data.get("customer information", {})

    return f"""### 🧾 Loan Risk Assessment Report

**Customer ID:** {customer.get("id", "N/A")}
**Name:** {customer.get("name", "N/A")}
**Email:** {customer.get("email", "N/A")}

**Credit Score:** {data.get("credit score", "N/A")}
**Account Status:** {data.get("account status", "N/A")}
**Nationality:** {data.get("nationality", "N/A")}
**PR Status:** {data.get("pr status", "N/A")}

### ⚠️ Overall Risk: **{data.get("overall risk", "N/A")}**
### 💰 Interest Rate: **{data.get("interest rate", "N/A")}**

### Recommendation: 
**{data.get("recommendation", "N/A")}**
"""

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
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    payload = {
        "question": user_input,
        "history": build_flowise_history(
            st.session_state.messages[:-1]
        )
    }

    # st.json(payload) #debug
    
    with st.spinner("Analyzing loan risk..."):
        response = requests.post(
            FLOWISE_API_URL,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            st.error("Flowise API error")
            st.code(response.text)
            st.stop()

        try:
            data = response.json()
        except ValueError:
            result_text = response.text
        else:
            # st.code(data) #debug

             # Structured loan JSON
            if isinstance(data, dict) and "text" in data:
                raw_text = data["text"]
            
                # Try to parse text as JSON
                try:
                    parsed = json.loads(raw_text)
                    if "customer information" in parsed:
                        result_text = format_loan_response(parsed)
                    else:
                        result_text = raw_text
                except json.JSONDecodeError:
                    result_text = raw_text
            
            elif isinstance(data, dict):
                result_text = format_loan_response(data)
            
            else:
                result_text = str(data)


    st.session_state.messages.append(
        {"role": "assistant", "content": result_text}
    )
    st.chat_message("assistant").markdown(result_text)
    st.stop()
