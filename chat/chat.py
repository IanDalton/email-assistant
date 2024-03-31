import pathlib
import textwrap
import os

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown

class Chatbot():
    def __init__(self, key:str,personality:str,functions:list,instructions:list) -> None:
        self.key = key
        self.personality = personality
        self.functions = functions
        self.instructions = instructions
        genai.configure(api_key=self.key)
        self.model = genai.GenerativeModel(tools=functions)
        
        
    def add_funtion(self,func):
        if func not in self.functions:
            self.functions.append(func)
        self.functions.append()
        self.model = genai.GenerativeModel(tools=self.functions)

    def new_chat(self,store = False):
        chat = self.model.start_chat(enable_automatic_function_calling=True)
        chat.send_message(self.personality + "\n".join(self.instructions))
        if store:
            self.chat = chat
        
        return chat
