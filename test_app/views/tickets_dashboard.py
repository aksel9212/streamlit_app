import streamlit as st
import pandas as pd
import json,os
from datetime import datetime
from views.aidialogexpert import AiDialogExpert
from streamlit_gsheets import GSheetsConnection
from streamlit_javascript import st_javascript

import gspread
from google.oauth2.service_account import Credentials


st.session_state['return_btn_label'] = 'Logout'

tickets_link = "https://docs.google.com/spreadsheets/d/175gz5oOXyfAJZjGKumuPd30YKGQl5ORitKZ-lJDGoRc/edit?usp=sharing"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def load_tickets(keys):
    #try:
    credentials = Credentials.from_service_account_info(dict(keys), scopes=SCOPES)
    gc = gspread.authorize(credentials)
    spreadsheet = gc.open_by_url(tickets_link)
    worksheet = spreadsheet.get_worksheet(0)
    st.session_state['tickets'] = worksheet.get_all_records()


def load_user_tickets():
    try:
        with open(f"test_app/users_data/{st.session_state['user_id']}/tickets.json", "r") as f:
            data = json.load(f)
        st.session_state['tickets'] = data       
    except FileNotFoundError:
        pass

# Initialize tickets in session state if not already present

if "tickets" not in st.session_state:
    st.session_state["tickets"] = []
    load_tickets(dict(st.secrets.google_creds))


# Custom CSS for transparent cards with centered content
card_style = """
    <style>
        .stButton{
            display: flex;
            justify-content: center;
            /*margin-top:-70px;*/
        }
        .st-emotion-cache-1dtfyw6 {
            margin-left:30px;
        }
        .stImage{
            display:none;
        }
        .card {
            border: 2px solid #00A2E8;
            border-radius: 8px;
            padding: 16px;
            padding-bottom: 50px;
            margin: 8px;
            background-color: rgba(0, 0, 0, 0); /* Transparent background */
            text-align: center; /* Center the content inside the card */
            margin-bottom:-70px;
            min-height: 300px;
        }
        .card:hover {
            box-shadow: 2px 2px 8px rgba(0, 128, 0, 0.5);
        }
        .card-content {
            margin-bottom: 16px;
        }
        .card-button-container {
            margin-top: 16px;
        }
        .card-button {
            margin-top: 12px;
            padding: 8px 16px;
            background-color: green;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            display:none;
        }
        .card-button:hover {
            background-color: darkgreen;
        }
        .card-date >p {
            font-size:14px;
        }
        .card-header>p {
            font-size:20px;
            font-weight:bold;
        }
        .card-status {
            display:flex;
            justify-content:space-between;
        }
    </style>
"""
st.markdown(card_style, unsafe_allow_html=True)



# App Title
st.title("Help Tickets Service")

# Form for creating a new ticket
#st.header("Create a New Help Ticket")
with st.form("ticket_form", clear_on_submit=True):
    name = st.session_state["username"]
    email = st.session_state["user_email"]
    user_id = st.session_state["user_id"]
    #issue = st.text_area("Describe Your Issue")
    # Use form_submit_button for submission
    submitted = st.form_submit_button("Create New Ticket")
    priority = st.selectbox("Priority", ["Low", "Medium", "High"])

if submitted:
    if name and email:
        ticket = {
            "User_id":user_id,
            "Ticket_id": st.session_state['n_tickets'],
            "Expert_id": 1,
            "Creation_date": datetime.today().strftime("%Y-%m-%d"),
            "Description":'',
            "Priority": priority,
            "State": 1,
            "Dialog":"[]",
            "Comments":"[]",
            "Username":name,
            "Header":"New Ticket",
            "User_email":email
        }
        st.session_state["current_ticket"] = len(st.session_state["tickets"])
        st.session_state["tickets"].append(ticket)
        
        
        st.success("Ticket submitted successfully!")
        if "aidialogexpert" in st.session_state:
            del(st.session_state['aidialogexpert'])
        st.switch_page("views/app2.py")
    else:
        st.error("Please fill in all fields.")

# Display all tickets dynamically
st.header("Submitted Tickets")
if st.session_state["tickets"]:
    
    #tickets_df = pd.DataFrame(st.session_state["tickets"])
    #st.table(tickets_df)

    # Option to mark tickets as resolved
    #with st.expander("Mark Tickets as Resolved"):
    #    ticket_to_resolve = st.selectbox(
    #        "Select a ticket to mark as resolved (by index):",
    #        options=range(len(st.session_state["tickets"])),
    #        #format_func=lambda x: f"{x} - {st.session_state['tickets'][x]['Issue'][:30]}..."
    #    )

    # Layout the cards in rows of 3
    url = st_javascript("await fetch('').then(r => window.parent.location.href)")
    with st.container():
        num_cards = len(st.session_state["tickets"])
        hashes = {
            '1':'0366849854fd27763c0902b4cda71297e44aa5512bc2ffa8436eb4a3',
            '2':'43bfe808ec124a660daca73038eba839992a5e768230bb0a365160c7',
            '3':'dc3d5aaa1974444cf9d8aab82d439c2ab69c373a656e4ab787710ded'
        }

        st.session_state['n_tickets'] = 0
        j = 0
        cols = st.columns(2)
        for i in range(num_cards):
            if(j==2):
                cols = st.columns(2)  # Create 2 columns
                j = 0
            #for j in range(2):
            card_index = i
            if card_index < num_cards:
                with cols[j]:
                    ticket_info = st.session_state["tickets"][card_index]
                    if ticket_info['User_id'] != st.session_state['user_id']:
                        continue
                    j+=1
                    st.session_state['n_tickets'] +=1
                    # Card content
                    try:
                        resolve_date = f"Gelöst am: {ticket_info['Resolve_date']}"
                    except:
                        resolve_date = ''
                    
                    ago = (datetime.now() - datetime(*[int(i) for i in ticket_info['Creation_date'].split("-")])).days
                    if ago == 0:
                        ago = ''
                    else:
                        ago = f"   ( vor {ago} tagen )"
                    st.markdown(
                        f"""
                        <div class="card">
                            <div class="card-content">
                                <div class='card-status'>
                                    <h4>0{st.session_state['n_tickets']}</h4>
                                    <img width='36' height='36' src='{url}media/{hashes[str(ticket_info['State'])]}.png'>
                                </div>
                                <div class='card-header'>
                                    <p>{ticket_info['Header']}</p>
                                </div>
                                <div class='card-date'>
                                    <p>Erstellt am: {ticket_info['Creation_date']} {ago}</p>
                                    <p>{resolve_date}</p>
                                </div>
                                <p>Priority: {ticket_info['Priority']}</p> 
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    # Button interaction in Streamlit


                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Edit Ticket", key=f"btn_{card_index}",type='primary'):
                            

                            # Save the parameter in the session state
                            ticket_info = st.session_state["tickets"][card_index]
                            st.session_state["current_ticket"] = card_index
                            st.session_state['aidialogexpert'] = AiDialogExpert(
                                                                st.session_state["user_id"],
                                                                st.session_state["username"],
                                                                st.session_state["user_email"],
                                                                ticket_info['Description'], 
                                                                json.loads(ticket_info['Dialog'])
                                                            )
                            st.switch_page("views/app2.py")
                    with col2:
                        if st.session_state["tickets"][card_index]["State"] != 3:
                            if st.button(f"Mark as Solved", key=f"solved_{card_index}"):
                                st.session_state["tickets"][card_index]["State"] = 3
                                st.switch_page("views/tickets_dashboard.py")

        if st.session_state['n_tickets'] == 0:
            st.info("No tickets submitted yet.")
                                        
else:
    st.info("No tickets submitted yet.")


st.image(f"test_app/assets/1.png")
st.image(f"test_app/assets/2.png")
st.image(f"test_app/assets/3.png")