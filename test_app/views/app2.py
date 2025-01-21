import streamlit as st
import json
import os
from dotenv import load_dotenv
import sys
import codecs
from views.aidialogexpert import AiDialogExpert
from textwrap import dedent

FNAME_MESSAGES_SAVE = "messages.json"
key = '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'
if "GROQAPI" not in os.environ:
    os.environ['GROQAPI'] = key
def dump_messages(messages, filepath):
    with open(filepath + FNAME_MESSAGES_SAVE, "w") as f:
        json.dump(messages, f)

    return

def get_saved_messages(filepath):
    if os.path.isfile(filepath + FNAME_MESSAGES_SAVE) == False:
        messages = []
        return messages
    
    with open(filepath + FNAME_MESSAGES_SAVE, "r") as f:
        messages = json.load(f)
        return messages  

def generate_new_ai_reply(prompt):
    with st.chat_message("assistant"):
        response = st.session_state.aidialogexpert.get_next_response(prompt)
        st.markdown(response)



st.title("AI Helpdesk Assistant")
load_dotenv()

if "aidialogexpert" not in st.session_state:
    # instantate with dummy data
    TEST_USER_DATA = dedent("""
        Der Kunde heißt Peter Parker, hat ein Kleinunternehmen mit Umsatz ca. 200000 EUR / Jahr, ist geboren am 01.12.1972, hat Familie mit 3 Kindern und eine nur zur Hälfte abbezahltes Eigenheim.
        Das aktuelle Datum ist der 10. September 2024
        Der Kunde lässt seine gesamte Buchführung sowie alle Pflichtmeldungen an das Finanzamt durch unser Steuerbüro erledigen. 
        Für die Umsatzsteuererklärung ist hier im Steuerbüro Frau Steinmeier zuständig. 
    """)

    st.session_state.aidialogexpert = AiDialogExpert(1, "Peter Parker", "peterparker@ticket01.com", TEST_USER_DATA, None)

  
# Display chat messages from history on app rerun
dialog = st.session_state.aidialogexpert.get_current_dialog()
with st.sidebar:
    if st.button("Save dialog"):
        dump_messages(dialog, "")              

    if st.button("Load dialog"):
        dialog = get_saved_messages("")              
        st.session_state.aidialogexpert.set_dialog(dialog)          

for message in dialog:
    if message["role"] != "system":
        print(message["role"], ":", message["content"] )
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Accept user input
text_prompt = st.chat_input("Was möchten Sie wissen?")

if text_prompt is not None:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(text_prompt)
    
    response = st.session_state.aidialogexpert.get_next_response(text_prompt)

    with st.chat_message("assistant"):
        st.markdown(response)

    # build protocol
    protocol = st.session_state.aidialogexpert.get_protocol()            
    # debug output in sidebar
    with st.sidebar:
        st.markdown(protocol)
   
        # generate status
        status = st.session_state.aidialogexpert.get_status(protocol) 

        st.markdown("## Klassifikation: ##")
        st.markdown(status)

