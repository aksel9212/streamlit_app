import os
import streamlit as st
import pandas as pd
import json
from streamlit_gsheets import GSheetsConnection

st.session_state['return_btn_label'] = 'Logout'
def check_login_(username, password):
    
    url = "https://docs.google.com/spreadsheets/d/1RPZ0Pkip0qNRyPrY1QUzsk7UD9ChRHNRJYi-XDl5xrA/edit?usp=sharing"

    conn = st.connection("gsheets", type=GSheetsConnection)
    data = conn.read(spreadsheet=url)
    df = pd.DataFrame(data)
    data_dict = df.to_dict(orient='records') 
    for user_info in data_dict:
        if user_info['Username'] == username:
            return user_info['Password'] == password, user_info
    return False, {}

def save_session():
    session_data = {
        "logged_in":st.session_state["logged_in"],
        "username":st.session_state["username"],
        "user_id":st.session_state["user_id"], 
        "user_email":st.session_state["user_email"]
    }
    with open("session_data.json", "w") as f:
        json.dump(session_data, f)

def load_session():    
    try:
        with open("session_data.json", "r") as f:
            session_data = json.load(f)
        for key, value in session_data.items():
            st.session_state[key] = value
        
    except FileNotFoundError:
        pass

# Define the main function
def main():
    
    load_session()

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if "username" not in st.session_state:
        st.session_state["username"] = ""
    if st.session_state["logged_in"] == False:
        st.title("Login Page")
        
        # Input fields for login
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        # Login button
        if st.button("Login"):
            valid_login, user_info = check_login_(username, password) 
            if valid_login:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["user_id"] = user_info['ID']
                st.session_state["user_email"] = user_info['Email']
                st.success("Successfully logged in!")
                save_session()
                st.rerun()
            else:
                st.error("Invalid username or password.")

    # Dashboard Page
    else:
        project_1_page = st.Page(
            "views/tickets_dashboard.py",
            title="Tickets Dashboard",
            icon=":material/bar_chart:",
            default=True
        )
        project_2_page = st.Page(
            "views/app2.py",
            title="Chat with us",
            icon=":material/smart_toy:",
        )

        pg = st.navigation([project_1_page, project_2_page],)


        # --- RUN NAVIGATION ---
        pg.run()
        # Logout button in sidebar
        if st.sidebar.button(st.session_state['return_btn_label'],key='return'):
            if st.session_state['return_btn_label'] == 'Zurück':
                st.switch_page("views/tickets_dashboard.py")

            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.session_state["user_email"] = ""
            st.session_state["user_id"] = 0
            save_session()
                
            st.navigation([project_1_page, project_2_page],position="hidden")
            st.rerun()
        
        save_session()


# Run the app
if __name__ == "__main__":
    
    main()
