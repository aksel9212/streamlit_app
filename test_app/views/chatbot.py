import random
import time

import streamlit as st


# Streamed response emulator
def response_generator():
    response = random.choice(
        [
            "Hey there! Need help? Please ask a question",
            "Hi! What's up? Do you need some help?",
            "aaaa aaaa aaaa  aaaa  aaaa aaaaa  aaaa",
            "nnnnn nnnnz nnnn nnnnn nnnnn  nnnnn nnnn"
        ]
    )
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
st.markdown("Please, describe your issue.")
# Accept user input
if prompt := st.chat_input("What is up?"):

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator())
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})


# JavaScript for auto-scrolling to the bottom
scroll_script = """
<script>
    const chatContainer = parent.document.querySelector('.stChatContainer');
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
</script>
"""
st.markdown(scroll_script, unsafe_allow_html=True)