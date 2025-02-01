import random, time, os
import streamlit as st
from views.ai_inference import AiResponseGenerator


key = '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'
if "GROQAPI" not in os.environ:
    os.environ['GROQAPI'] = key
inference = AiResponseGenerator("GROQ","llama-3.1-8b-instant")
def response_generator(message):
    response = inference.response_generator(message)
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

with st.chat_message("assistant"):
    response = st.write("Please, describe your issue.")

# Accept user input
if prompt := st.chat_input("What is up?"):

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        response = st.write_stream(response_generator(st.session_state.messages))
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