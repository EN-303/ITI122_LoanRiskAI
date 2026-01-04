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
    sections = ["### Customer Information:\n"]

    # --- Customer Information ---
    customer = data.get("customer information")
    if isinstance(customer, dict):
        sections.append(
            f"""**ID:** {customer.get("id", "N/A")}  
**Name:** {customer.get("name", "N/A")}  
**Email:** {customer.get("email", "N/A")}  
"""
        )

    # st.code("ok1") #debug
    
    # --- Credit / Status Block ---
    credit_fields = [
        ("Credit Score", "credit score"),
        ("Account Status", "account status"),
        ("Nationality", "nationality"),
        ("PR Status", "pr status"),
    ]

    credit_lines = []
    for label, key in credit_fields:
        if key in data:
            credit_lines.append(f"**{label}:** {data.get(key, 'N/A')}  ")

    if credit_lines:
        sections.append("\n".join(credit_lines) + "\n")

    # st.code("ok2") #debug
    
    # --- Risk Summary ---
    if "overall risk" in data:
        sections.append("### 🧾 Loan Risk Assessment Report\n")
        sections.append(
            f"### ⚠️ Overall Risk: **{data.get('overall risk', 'N/A')}**\n"
        )

    if "interest rate" in data:
        sections.append(
            f"### 💰 Interest Rate: **{data.get('interest rate', 'N/A')}**\n"
        )

    # --- Recommendation ---
    if "recommendation" in data:
        sections.append(
            f"""### 📝 Recommendation  
**{data.get("recommendation", "N/A")}**
"""
        )

    return "\n".join(sections)


# --- Initialize chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi, I am Bot, your Loan Risk Assessment Assistant.\n\n"
                "Please choose one of the following options:\n\n"
                "1 - Retrieve customer information (ID and name required)\n\n"
                "2 - Check customer loan risk (ID and name required)\n\n"
                "3 - General loan-related questions\n\n"
                "Reply format:\n\n"
                "1 - <customer_id>, <customer_name>\n\n"
                "3 - <question>\n\n"
                "Examples:\n\n"
                "1 - 1111, Joe\n\n"
                "3 - What are the different risk levels?"
            )
        }
    ]




# --- Display chat messages ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

DEBUG = True

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
    
    with st.spinner("Processing request..."):
        response = requests.post(
            FLOWISE_API_URL,
            json=payload,
            timeout=60
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
            # st.code("print data") #debug
            # st.code(data) #debug

             # Structured loan JSON
            if isinstance(data, dict) and "text" in data:
                raw_text = data["text"]
                
                if DEBUG:
                    st.write("### Debug: raw_text")
                    st.code(raw_text)
                
                # Try to parse text as JSON
                try:
                    parsed = json.loads(raw_text)
                    if "customer information" in parsed:
                        # st.code("test 3") #debug
                        result_text = format_loan_response(parsed)
                    else:
                        # st.code("test 1") #debug
                        result_text = raw_text
                except json.JSONDecodeError:
                    # st.code("test 2") #debug
                    result_text = raw_text
            
            elif isinstance(data, dict):
                result_text = format_loan_response(data)
            
            else:
                result_text = str(data)


    st.session_state.messages.append(
        {"role": "assistant", "content": result_text}
    )
    st.chat_message("assistant").markdown(result_text)
    #st.stop()
