import streamlit as st
import json
import os
from dotenv import load_dotenv
import pandas as pd
import sys
import codecs
from utils.aidialogexpert import AiDialogExpert
from textwrap import dedent
from streamlit_gsheets import GSheetsConnection
import gspread
from google.oauth2.service_account import Credentials
st.session_state['return_btn_label'] = 'Zurück'

groq_key = st.secrets.groq.groqkey
deepseek_key = st.secrets.deepseek.deepseek_key

tickets_link = "https://docs.google.com/spreadsheets/d/175gz5oOXyfAJZjGKumuPd30YKGQl5ORitKZ-lJDGoRc/edit?usp=sharing"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

if "GROQAPI" not in os.environ:
    os.environ['GROQAPI'] = groq_key
if "DEEPSEEK_API_KEY" not in os.environ:
    os.environ['DEEPSEEK_API_KEY'] = deepseek_key


def update_tickets(keys):
    credentials = Credentials.from_service_account_info(keys, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_url(tickets_link)
    worksheet = spreadsheet.get_worksheet(0)
    data_dict = st.session_state["tickets"]
    #conn.update(spreadsheet=spreadsheet,data=data_dict)
    keys = list(data_dict[0].keys())
    values = [list(d.values()) for d in data_dict]
    df = pd.DataFrame([keys] + values)
    worksheet.update([keys] + values)


def save_user_tickets():
    tickets = st.session_state["tickets"] 
    with open(f"test_app/users_data/{st.session_state['user_id']}/tickets.json", "w") as f:
        json.dump(tickets, f)

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

    st.session_state.aidialogexpert = AiDialogExpert(st.session_state["user_id"],
                                        st.session_state["username"],
                                        st.session_state["user_email"],
                                        TEST_USER_DATA, 
                                        None
                                    )

# Display chat messages from history on app rerun
dialog = st.session_state.aidialogexpert.get_current_dialog()
with st.sidebar:
    #if st.button("Save ticket"):
        #dump_messages(dialog, "")
    #    dialog = st.session_state.aidialogexpert.get_current_dialog()
    #    st.session_state["tickets"][st.session_state["current_ticket"]]["Dialog"] = json.dumps(dialog, allow_nan=True)
        #update_tickets()
    #    save_user_tickets()              

    #if st.button("Load dialog"):
    #    dialog = get_saved_messages("")              
        
    st.session_state.aidialogexpert.set_dialog(dialog)
    try:
        #st.markdown(st.session_state["tickets"][st.session_state["current_ticket"]]["Description"])
        st.sidebar.image(f"assets/{st.session_state["tickets"][st.session_state["current_ticket"]]["State"]}.jpg",width=525) 
        st.markdown(f"<p><b>{st.session_state["tickets"][st.session_state["current_ticket"]]["Header"]}</b></p>"
        ,unsafe_allow_html=True)
    except:
        pass

for message in dialog:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# Accept user input
text_prompt = st.chat_input("Was möchten Sie wissen?")

if text_prompt is not None:
    if "current_ticket" not in st.session_state:
        st.switch_page("views/tickets_dashboard.py")
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(text_prompt)
    
    response = st.session_state.aidialogexpert.get_next_response(text_prompt)

    with st.chat_message("assistant"):
        st.markdown(response)

    # build protocol
    protocol = st.session_state.aidialogexpert.get_protocol() 
    st.session_state["tickets"][st.session_state["current_ticket"]]["Description"] = protocol           
    
    status = st.session_state.aidialogexpert.get_status(protocol)
    st.session_state["tickets"][st.session_state["current_ticket"]]["State"] = status
    
    dialog = st.session_state.aidialogexpert.get_current_dialog()
    st.session_state["tickets"][st.session_state["current_ticket"]]["Dialog"] = json.dumps(dialog, allow_nan=True)
    
    header = st.session_state.aidialogexpert.get_ticket_header(protocol)
    st.session_state["tickets"][st.session_state["current_ticket"]]["Header"] = header
    
    update_tickets(dict(st.secrets.google_creds))              
    st.switch_page("views/app2.py")
    # debug output in sidebar
    #with st.sidebar:
        #st.markdown(protocol)
        # generate status
    #    st.markdown("## Klassifikation: ##")
    #    st.sidebar.image(f"test_app/assets/{status}.jpg",width=50)

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