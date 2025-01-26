from views.airesponsegenerator import AiResponseGenerator
import json
import os
from dotenv import load_dotenv
import sys
import codecs
from views.status_classifier import StatusClassification, States
from views.system_prompts import SystemPrompts

LLM_MODEL_ANALYSE = "llama-3.3-70b-versatile"         # GROQ: llama-3.2-90b-vision-preview llama-3.3-70b-versatile gemma2-9b-it
                                            # OPENAI: gpt-3.5-turbo gpt-4o 
                                            # XAI: "grok-beta"
                                            # DEEPSEEK: deepseek-chat
                                            # GOOGLE: gemini-1.5-pro
LLM_PROVIDER_ANALYSE = "GROQ"             # GOOGLE GROQ OPENAI XAI DEEPSEEK

LLM_MODEL_PROTOCOL = "llama-3.3-70b-versatile"        # GROQ: llama-3.2-90b-vision-preview llama-3.3-70b-versatile gemma2-9b-it
LLM_PROVIDER_PROTOCOL = "GROQ"          # GOOGLE GROQ OPENAI XAI DEEPSEEK

LLM_MODEL_CLASSIFIER = "gemma2-9b-it"      # GROQ: llama-3.2-90b-vision-preview llama-3.3-70b-versatile gemma2-9b-it
LLM_PROVIDER_CLASSIFIER = "GROQ"           # GOOGLE GROQ OPENAI XAI DEEPSEEK

LLM_TEMPERATURE = 0
LLM_CONTEXT_WIN = 8000

FILE_PATH = ""
FNAME_AUTO_SAVE = "autosave.json"
FNAME_SYS_PROMPT = "sp_steuer_berater_dialog_02.txt"
FNAME_SYS_PROMPT2 = "sp_steuer_berater_protokoll_03.txt"
FNAME_SYS_PROMPT3 = "sp_steuer_berater_classifier_02.txt"
FNAME_SYS_PROMPT4 = "sp_steuer_berater_notifier.txt"

class AiDialogExpert:
    def __init__(self, userid, name, email, user_data, dialog):
        self.user_data = user_data
        self.set_dialog(dialog)

        self.llm_dialog = AiResponseGenerator(LLM_PROVIDER_ANALYSE, LLM_MODEL_ANALYSE, LLM_CONTEXT_WIN, LLM_TEMPERATURE)
        self.llm_protocol = AiResponseGenerator(LLM_PROVIDER_PROTOCOL, LLM_MODEL_PROTOCOL, LLM_CONTEXT_WIN, LLM_TEMPERATURE)
        self.llm_class = AiResponseGenerator(LLM_PROVIDER_CLASSIFIER, LLM_MODEL_CLASSIFIER, LLM_CONTEXT_WIN, LLM_TEMPERATURE)
        self.userid = userid
        self.name = name
        self.email = email
        self.status_classifier = StatusClassification()

    def set_dialog(self, dialog):
        sp = SystemPrompts.SYSTEMPROMPT_DIALOG.replace("{user_data}", self.user_data)
        self.messages = [
            {
                "role": "system",
                "content": sp
            }
        ]
        if dialog != None:
            #self.messages.append(dialog)
            self.messages += dialog

    def set_user_data(self, userid, name, email, user_data):
        self.userid = userid
        self.name = name
        self.email = email
        self.user_data = user_data

    def get_next_response(self, user_input):
        print('# add user input to messages')
        self.messages.append({"role": "user", "content": user_input})
        # generate response
        response = self.llm_dialog.response_generator(self.messages)
        print('# add repsonse to messsages')
        self.messages.append({"role": "assistant", "content": response})
        return response

    # get current dialog     
    def get_current_dialog(self):
        dialog = []    
        print("self.messages",self.messages)
        for msg in self.messages:
            # filter systemprompt
            if msg["role"] != "system": 
                dialog.append(msg)

        return dialog

    def get_protocol(self):
        protocol = ""
        for msg in self.messages:
            if msg["role"] == "system": 
                continue

            if msg["role"] == "user":
                protocol = protocol + "User:\n\n" + msg["content"] + "\n\n" 

            if msg["role"] == "assistant":
                protocol = protocol + "Berater:\n\n" + msg["content"] + "\n\n" 

        messages = [
            {
            "role": "system",
            "content": SystemPrompts.SYSTEMPROMPT_PROTOCOL,
            },
            {
            "role": "user",
            "content": protocol,
            }
        ]
        protocol = self.llm_protocol.response_generator(messages)
        return protocol
    
    def get_status(self, protocol):
        messages_class = [
            {
            "role": "system",
            "content": SystemPrompts.SYSTEMPROMPT_CLASSIFIER,
            },
            {
            "role": "user",
            "content": protocol,
            }
        ]
        status_response = self.llm_class.response_generator(messages_class)
        status = self.status_classifier.set_status(status_response)
        return status
    
