import streamlit as st
import requests
import json

# ---------- Page Settings ----------
st.set_page_config(page_title="OpenRouter Chatbot", page_icon="🤖")
st.title("🤖 OpenRouter Chatbot")

# ---------- API Key ----------
api_key = st.text_input("🔑 Enter your OpenRouter API Key:", type="password")
if not api_key:
    st.warning("Please enter your API key to continue.")
    st.stop()

model = "deepseek/deepseek-chat-v3-0324:free"
url = "https://openrouter.ai/api/v1/chat/completions"

# ---------- Initialize Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "persona" not in st.session_state:
    st.session_state.persona = None

if "custom_persona" not in st.session_state:
    st.session_state.custom_persona = ""

# ---------- Persona Selection ----------
st.subheader("🎭 Choose Your Assistant's Persona")

persona_options = [
    "Helpful Assistant 🤝",
    "Doctor 👨‍⚕️",
    "Lawyer ⚖️",
    "Storyteller 📚",
    "Custom (Type your own)"
]

selected_persona = st.selectbox(
    "Select a persona:",
    persona_options,
    index=persona_options.index(st.session_state.persona) if st.session_state.persona in persona_options else 0
)

if selected_persona == "Custom (Type your own)":
    custom_persona_input = st.text_input(
        "✏️ Define your custom assistant persona here:",
        value=st.session_state.custom_persona
    )
    if custom_persona_input:
        st.session_state.persona = custom_persona_input
        st.session_state.custom_persona = custom_persona_input
    else:
        st.warning("Please enter a custom persona.")
        st.stop()
else:
    st.session_state.persona = selected_persona
    st.session_state.custom_persona = ""

# ---------- Show Current Persona ----------
st.markdown(f"🧭 **Current Assistant Persona:** _{st.session_state.persona}_")

# ---------- Add System Message if Starting New Chat ----------
if not any(msg["role"] == "system" for msg in st.session_state.messages):
    st.session_state.messages.insert(0, {"role": "system", "content": f"You are {st.session_state.persona}."})

# ---------- Start New Chat Button ----------
if st.button("🆕 Start New Chat"):
    st.session_state.messages = [{"role": "system", "content": f"You are {st.session_state.persona}."}]
    st.rerun()

# ---------- Display Chat History ----------
st.subheader("💬 Chat History")
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"**🧑 You:** {msg['content']}")
    elif msg["role"] == "assistant":
        st.markdown(f"**🤖 Assistant:** {msg['content']}")

# ---------- User Input ----------
user_input = st.chat_input("Type your message here...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": st.session_state.messages
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    try:
        assistant_reply = result["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        assistant_reply = "❗️ Error getting response. Please check your API key or try again."

    st.session_state.messages.append({"role": "assistant", "content": assistant_reply})
    st.rerun()

# ---------- Save / Load Conversation ----------
st.divider()
st.subheader("💾 Save / Load Conversation")

if st.button("💾 Save Conversation"):
    filename = st.text_input("Enter filename to save:", "chat_history.json")
    if filename:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success(f"✅ Conversation saved to {filename}")

if st.button("📂 Load Conversation"):
    uploaded_file = st.file_uploader("Choose a .json file", type="json")
    if uploaded_file:
        st.session_state.messages = json.load(uploaded_file)
        st.success("✅ Conversation loaded!")
        st.rerun()
