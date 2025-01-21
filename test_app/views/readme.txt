AI modules 
==========

The following additional modules are needed:

pip install python-dotenv
pip install ollama
pip install groq
pip install openai
pip install google-generativeai

Currently Groq is used as LLM provioder. 
A .env file is needed which contains the Groq api key:

GROQ_API_KEY=xxxxxx

Start the test app with:

$ streamlit run app2.py

The test app app2.py shows the usage of this class.
The test app instantiates a AiDialogExpert() object which do the main work. 
This class have this methods:

get_next_response(text_prompt): 
get the next chat response from LLM

set_dialog(dialog): 
set an existing dialog

get_current_dialog(): 
returns the current dialog, so it could be stored somewhere

get_protocol(): 
generates and returns a summary of the current dialog

get_status(summary): 
based on the summary a status is generated. Currently thsi states are suppported:
    1: dialog is in work, issue is not fully described, AI waits for more information
    2: issue is described and understood by AI, and is in work, customer wait for feedback
    3: issue is solved
              
              