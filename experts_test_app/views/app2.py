import streamlit as st
import json
import os
from dotenv import load_dotenv
import pandas as pd
import sys
from datetime import datetime
import codecs
from utils.aidialogexpert import AiDialogExpert
from textwrap import dedent
from streamlit_gsheets import GSheetsConnection

import gspread
from google.oauth2.service_account import Credentials

st.session_state['return_btn_label'] = 'Zurück'

tickets_link = "https://docs.google.com/spreadsheets/d/175gz5oOXyfAJZjGKumuPd30YKGQl5ORitKZ-lJDGoRc/edit?usp=sharing"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

groq_key = st.secrets.groq.groqkey
deepseek_key = st.secrets.deepseek.deepseek_key

if "GROQAPI" not in os.environ:
    os.environ['GROQAPI'] = groq_key
if "DEEPSEEK_API_KEY" not in os.environ:
    os.environ['DEEPSEEK_API_KEY'] = deepseek_key

card_style = """
    <style>
        .description {
            border: 1px solid lightgray;
            padding:10px;
        }
        .comment {
            border: 1px solid lightgray;
            padding:10px;
            margin-bottom:10px;
        }
        .comment-date-author {
            display:flex;
            justify-content:end;
        }
        .comment-date-author >p{
            color:gray;
        }
    </style>
"""
st.markdown(card_style, unsafe_allow_html=True)

def update_tickets(keys,deletion=False):
    
    credentials = Credentials.from_service_account_info(keys, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_url(tickets_link)
    worksheet = spreadsheet.get_worksheet(0)
    data_dict = worksheet.get_all_records()
    for x in st.session_state["tickets"]:
        found = False
        for i in range(len(data_dict)):
            if x["User_id"] == data_dict[i]["User_id"] and x["Ticket_id"] == data_dict[i]["Ticket_id"]:
                x["Comments"] = json.dumps(x["Comments"])
                data_dict[i] = x
                found = True
                break
        if not found:
            data_dict.append(x)

    #conn.update(spreadsheet=spreadsheet,data=data_dict)
    keys = list(data_dict[0].keys())
    values = [list(d.values()) for d in data_dict]
    df = pd.DataFrame([keys] + values)
    
    if deletion:
        worksheet.clear()
    worksheet.update([keys] + values)


def save_user_tickets():
    tickets = st.session_state["tickets"] 
    print(tickets)
    with open(f"experts_test_app/users_data/{st.session_state['user_id']}/tickets.json", "w") as f:
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


load_dotenv()
if "current_ticket" not in st.session_state:
    st.switch_page("views/tickets_dashboard.py")

if "aidialogexpert" not in st.session_state:
    # instantate with dummy data
    TEST_USER_DATA = dedent("""
        Der Kunde heißt Peter Parker, hat ein Kleinunternehmen mit Umsatz ca. 200000 EUR / Jahr, ist geboren am 01.12.1972, hat Familie mit 3 Kindern und eine nur zur Hälfte abbezahltes Eigenheim.
        Das aktuelle Datum ist der 10. September 2024
        Der Kunde lässt seine gesamte Buchführung sowie alle Pflichtmeldungen an das Finanzamt durch unser Steuerbüro erledigen. 
        Für die Umsatzsteuererklärung ist hier im Steuerbüro Frau Steinmeier zuständig. 
    """)

    st.session_state.aidialogexpert = AiDialogExpert(
                                        st.session_state["tickets"][st.session_state["current_ticket"]]["User_id"],
                                        st.session_state["tickets"][st.session_state["current_ticket"]]["username"],
                                        st.session_state["tickets"][st.session_state["current_ticket"]]["user_email"],
                                        TEST_USER_DATA, 
                                        None
                                    )
with st.sidebar:
    try:
        st.sidebar.image(f"assets/{st.session_state["tickets"][st.session_state["current_ticket"]]["State"]}.jpg",width=525) 
        
    except:
        pass

# Display chat messages from history on app rerun
try:
    #st.sidebar.image(f"test_app/assets/{st.session_state["tickets"][st.session_state["current_ticket"]]["State"]}.jpg",width=525) 
    st.markdown(f"<p><b>{st.session_state["tickets"][st.session_state["current_ticket"]]["Header"]}</b></p>"
        ,unsafe_allow_html=True)
    st.markdown(f"""<div class='description'>
        {st.session_state["tickets"][st.session_state["current_ticket"]]["Description"]}
        </div>
        <p><b>Kommentare:</b></p>
    """,unsafe_allow_html=True)   
    for comment in st.session_state["tickets"][st.session_state["current_ticket"]]["Comments"]:

        st.markdown(f"""
            <div class='comment'>
            <p>{comment["comment"]}</p>
            <div class='comment-date-author'><p>{comment["expert"]} at {comment["date"]}</p></div>
            </div>""",unsafe_allow_html=True)
except:
    pass
# Accept user input
comment = st.chat_input("Add a comment")
if comment is not None:
    # Display user message in chat message container
    comment_date = datetime.today().strftime("%Y-%m-%d")
    expert_id = st.session_state["username"]
    st.markdown(f"""
        <div class='comment'>
        <p>{comment}</p>
        <div class='comment-date-author'><p>{expert_id} at {comment_date}</p></div>
        </div>""",
        unsafe_allow_html=True)
   
    st.session_state["tickets"][st.session_state["current_ticket"]]["Comments"].append(
            {"comment":comment,"expert":expert_id,"date":comment_date}
        )
    st.session_state["tickets"][st.session_state["current_ticket"]]["Description"] = st.session_state.aidialogexpert.get_new_protocol(
        st.session_state["tickets"][st.session_state["current_ticket"]]["Description"],comment)
    status = st.session_state.aidialogexpert.get_status(st.session_state["tickets"][st.session_state["current_ticket"]]["Description"])
    st.session_state["tickets"][st.session_state["current_ticket"]]["State"] = status

    update_tickets(dict(st.secrets.google_creds))
    st.switch_page("views/app2.py")
    #save_user_tickets()              
    #except:
    #    pass
