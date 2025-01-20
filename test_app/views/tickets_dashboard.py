import streamlit as st
import pandas as pd
import json


def save_tickets():
    tickets = {"tickets":st.session_state["tickets"]}
    with open(f"users_tickets.json", "w") as f:
        json.dump(tickets, f)
def load_tickets():
    try:
        with open(f"users_tickets.json", "r") as f:
            data = json.load(f)
        st.session_state['tickets'] = [t for t in data['tickets'] if t['ID'] == st.session_state["user_id"]]        
    except FileNotFoundError:
        pass

# Initialize tickets in session state if not already present
load_tickets()
if "tickets" not in st.session_state:
    st.session_state["tickets"] = []

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
            "ID":user_id,
            "Name": name,
            "Email": email,
            #"Issue": issue,
            "Priority": priority,
            "Status": "Open"
        }
        st.session_state["tickets"].append(ticket)
        save_tickets()
        st.success("Ticket submitted successfully!")
        st.switch_page("views/chatbot.py")
    else:
        st.error("Please fill in all fields.")

# Display all tickets dynamically
st.header("Submitted Tickets")
if st.session_state["tickets"]:
    tickets_df = pd.DataFrame(st.session_state["tickets"])
    st.table(tickets_df)

    # Option to mark tickets as resolved
    with st.expander("Mark Tickets as Resolved"):
        ticket_to_resolve = st.selectbox(
            "Select a ticket to mark as resolved (by index):",
            options=range(len(st.session_state["tickets"])),
            #format_func=lambda x: f"{x} - {st.session_state['tickets'][x]['Issue'][:30]}..."
        )
        if st.button("Mark as Resolved"):
            st.session_state["tickets"][ticket_to_resolve]["Status"] = "Resolved"
            st.success(f"Ticket {ticket_to_resolve} marked as resolved.")
            save_tickets()
            
else:
    st.info("No tickets submitted yet.")
