import streamlit as st
import pandas as pd
import json,os
from views.aidialogexpert import AiDialogExpert
from streamlit_gsheets import GSheetsConnection
from streamlit_javascript import st_javascript

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
    load_user_tickets()


# Custom CSS for transparent cards with centered content
card_style = """
    <style>
        .stButton{
            display: flex;
            justify-content: center;
            /*margin-top:-70px;*/
        }
        .stImage{
            display:none;
        }
        .card {
            border: 2px solid green;
            border-radius: 8px;
            padding: 16px;
            padding-bottom: 50px;
            margin: 8px;
            background-color: rgba(0, 0, 0, 0); /* Transparent background */
            text-align: center; /* Center the content inside the card */
            margin-bottom:-70px;
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
        .card-header{
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
            "Ticket_id": len(st.session_state["tickets"]),
            "Expert_id": 1,
            "Creation_date": '2024-01-23',
            "Description":'',
            "Priority": priority,
            "State": 1,
            "Dialog":""
        }
        st.session_state["tickets"].append(ticket)
        st.session_state["current_ticket"] = ticket["Ticket_id"]
        #save_tickets()
        print("st.session_state[tickets]",st.session_state["tickets"])
        st.success("Ticket submitted successfully!")
        if "aidialogexpert" in st.session_state:
            del(st.session_state['aidialogexpert'])
        st.switch_page("views/app2.py")
    else:
        st.error("Please fill in all fields.")

# Display all tickets dynamically
st.header("Submitted Tickets")
if st.session_state["tickets"]:
    print("st.session_state;",st.session_state["tickets"])
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
        for i in range(0, num_cards, 2):
            cols = st.columns(2)  # Create 3 columns
            for j in range(2):
                card_index = i + j
                if card_index < num_cards:
                    with cols[j]:
                        ticket_info = st.session_state["tickets"][card_index]
                        # Card content
                        try:
                            resolve_date = f"Resolve date: {ticket_info['Resolve_date']}."
                        except:
                            resolve_date = ''
                        
                        st.image(f"test_app/assets/{ticket_info['State']}.png")
                        st.markdown(
                            f"""
                            <div class="card">
                                <div class="card-content">
                                    <div class='card-status'>
                                        <h4>0{card_index + 1}</h4>
                                        <img width='36' height='36' src='{url}media/0366849854fd27763c0902b4cda71297e44aa5512bc2ffa8436eb4a3.png'>
                                    </div>
                                    <div class='card-header'>
                                        this is a header
                                    </div>
                                    <div class='card-date'>
                                        <p>Creation date: {ticket_info['Creation_date']}.</p>
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
                                st.session_state["current_ticket"] = ticket_info["Ticket_id"]
                                st.session_state['aidialogexpert'] = AiDialogExpert(
                                                                    st.session_state["user_id"],
                                                                    st.session_state["username"],
                                                                    st.session_state["user_email"],
                                                                    ticket_info['Description'], 
                                                                    json.loads(ticket_info['Dialog'])
                                                                )
                                st.switch_page("views/app2.py")
                        with col2:
                            if st.session_state["tickets"][card_index]["State"] != "Resolved":
                                if st.button(f"Mark as Solved", key=f"solved_{card_index}"):
                                    st.session_state["tickets"][card_index]["State"] = "Resolved"
                                    st.switch_page("views/tickets_dashboard.py")
    
                                    
else:
    st.info("No tickets submitted yet.")


