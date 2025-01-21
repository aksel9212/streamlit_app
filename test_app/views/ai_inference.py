import ollama
import os
from groq import Groq
from openai import OpenAI
#import google.generativeai as genai
import base64
import time

class AiResponseGenerator:
    def __init__(self, provider, model_name, max_tokens=None, temperature=None):
        """
        Initialisiert die Klasse
        """
        self.provider = provider
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature

    def __response_generator_groq(self, messages):
        groq_api_key = os.getenv("GROQAPI")
        # Create the Groq client
        client = Groq(api_key=groq_api_key, )
        
        ai_response = client.chat.completions.create(model=self.model_name,
                                                messages=messages,
                                                max_tokens=self.max_tokens,
                                                temperature=self.temperature)
        return ai_response.choices[0].message.content

    def ___response_generator_ollama(self, messages):
        options = {
            'temperature': self.temperature,
            "num_ctx": self.max_tokens,
        }
        ai_response = ollama.chat(model=self.model_name, messages=messages, options=options)
        return ai_response["message"]["content"]

    def __response_generator_openai(self, messages):
        openai_api_key = os.getenv("OPENAIAPI")
        client = OpenAI(api_key=openai_api_key,)
        
        ai_response = client.chat.completions.create(
                                                model=self.model_name,
                                                messages=messages,
                                                temperature=self.temperature)
        return ai_response.choices[0].message.content

    def __response_generator_deepseek(self, messages):
        api_key = os.getenv("DEEPSEEK_API_KEY")
        client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
        
        ai_response = client.chat.completions.create(
                                                model=self.model_name,
                                                messages=messages,
                                                temperature=self.temperature)
        return ai_response.choices[0].message.content

    def __response_generator_xai(self, messages):
        xai_api_key = os.getenv("XAI_API_KEY")

        # Create the client
        client = OpenAI(
            api_key=xai_api_key,
            base_url="https://api.x.ai/v1",
        )
        
        ai_response = client.chat.completions.create(
                                                model=self.model_name,
                                                messages=messages,
                                                temperature=self.temperature)
                                                
        return ai_response.choices[0].message.content
    """
    def __response_generator_google(self, messages):
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        generation_config = {"temperature" : self.temperature, "top_p" : 1, "top_k" : 1, "max_output_tokens" : self.max_tokens}
        
        # change messages data structure
        history = []
        system_instruction = ""
        last_msg = messages.pop()
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                role = msg["role"]
                if role == "assistant":
                    role = "model"

                history.append({"role": role, "parts" : msg["content"]})

        model = genai.GenerativeModel(
            model_name=self.model_name, 
            generation_config=generation_config,
            system_instruction=system_instruction
        )

        chat_session = model.start_chat(history=history)
        # send last msg as message
        response = chat_session.send_message(last_msg["content"])
        return response.text
    """
    # Function to encode the image
    @staticmethod
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def __image_classification_groq(self, image_path, user_prompt):
        base64_image = self.encode_image(image_path)
        groq_api_key = os.getenv("GROQAPI")
        client = Groq(api_key=groq_api_key,)

        start = time.time()
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                            },
                        },
                    ],
                }
            ],
            model=self.model_name,
            temperature=self.temperature,
        )
        response = chat_completion.choices[0].message.content
        end = time.time()
        self.duration = end - start
        #print(f'Ausführungszeit: {self.duration} Sekunden')
        return response

    def response_generator(self, messages):
        if self.provider == "OLLAMA":
            return self.___response_generator_ollama(messages)
        elif self.provider == "GROQ":
            return self.__response_generator_groq(messages)
        elif self.provider == "OPENAI":
            return self.__response_generator_openai(messages)
        elif self.provider == "GOOGLE":
            return None #self.__response_generator_google(messages)
        elif self.provider == "XAI":
            return self.__response_generator_xai(messages)
        elif self.provider == "DEEPSEEK":
            return self.__response_generator_deepseek(messages)
        else:
            print("ERROR: invalid provider.")
            return None
        
    def image_classification(self, image_path, user_prompt):
        if self.provider == "OLLAMA":
            return self.__image_classification_ollama(image_path, user_prompt)
        elif self.provider == "GROQ":
            return self.__image_classification_groq(image_path, user_prompt)
        else:
            print("ERROR: invalid provider.")
            return None    