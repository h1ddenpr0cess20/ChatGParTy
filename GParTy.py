'''
ChatGParTy (name subject to change)
Multicharacter AI conversations

Dustin Whyte
October 2023
'''

from openai import OpenAI
import random
import logging
from rich.console import Console
import time
import os
import re
import sys

class character:
    def __init__(self, personality, convo_type, topic, setting):
        
        self.personality = personality
        self.convo_type = convo_type
        self.topic =  topic
        self.setting = setting

    def respond(self, history):
        message = [
            {"role": "system", "content": f"assume the personality of {self.personality}. roleplay as them and stay in character at all times. your responses should be short and conversational, between one word to one paragraph in length."},
            {"role": "user", "content": f'''you're the next speaker in a {self.convo_type} about {self.topic}.  the setting is {self.setting}.
here are the last few messages:

{history}

[if the {self.convo_type} is getting repetitive, feel free to move on to a related subject]'''}
            ]
        try:
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview", #change to gpt-3.5-turbo if you want to save money
                temperature=1, 
                messages=message)
            self.response_text = response.choices[0].message.content
            
            name = re.findall(r"^[^\n:]+:", self.response_text)
            if len(name)>0:
                self.response_text = self.response_text.lstrip(name[0])
            return self.response_text
        except Exception as e:
            print(e)


class conversation:
    def __init__(self, convo_type, topic, setting, *participants):
        self.convo_type = convo_type
        self.topic = topic
        self.setting = setting
        self.participants = list(participants)
        self.participants_names = []
        for p in self.participants:
            self.participants_names.append(p.personality)

        self.history = [f"[{self.convo_type} hasn't started yet]"]
    

    def next_speaker(self, history):
        if len(self.participants) == 2:
            last_message = self.history[-1]
            if last_message.startswith(self.participants_names[0]):
                return [self.participants_names[1], "because there are only two participants"]
            else:
                return [self.participants_names[0], "because there are only two participants"]
        else:
            for x in range(3):
                message = [{"role": "user", 
                            "content": f'''based on this {self.convo_type} history and listed participants, reply with the name of the most likely next speaker as it appears before their line and an explanation of your reasoning in the format of "<name>|<reason>" and nothing else.

    participant names: {', '.join(self.participants_names)}  

    {history}'''}]
                response = openai.chat.completions.create(
                    model='gpt-4-1106-preview', #this will not work properly with gpt-3.5-turbo, do not change
                    temperature=0, 
                    messages=message)
                response_text = response.choices[0].message.content
                response_text = response_text.split("|", 1)
                
                if response_text[0] in self.participants_names:
                    next_speaker = response_text
                    break     
            try:
                return next_speaker
            except:
                return [random.choice(self.participants_names), "because the function failed so we choose randomly"]
    
    def start(self):
        # logging
        logging.basicConfig(filename='cc.log', format='%(message)s')
        
        # text wrap and color
        pretty = Console()
        pretty.width=80
        pretty.wrap_text = True
        names = ' and '.join(self.participants_names)
        #information about conversation for the log
        logging.info(f"\n{names.upper()} have a {self.convo_type} about {self.topic}.  the setting is {self.setting}.")

        #first speaker starts conversation
        speaker = random.choice(self.participants)
        participants = [x for x in self.participants_names if x != speaker.personality]
        intro = f"start a {self.convo_type} about {self.topic} with {participants}.  the setting is {self.setting}."
        message = speaker.respond(intro)
        self.history.append(f"{speaker.personality}: {message}")
        pretty.print(f"\n{speaker.personality.upper()}\n{message}\n", justify="left", highlight=False)
        logging.info(f"{speaker.personality.upper()}: {message}")

        while True:
            time.sleep(6)
            decision = self.next_speaker(self.history[-8:])
            logging.info(f"     *** {decision[0].upper()} is speaking next because {decision[1]} ***")
            speaker_personality = decision[0]
            speaker_index = self.participants_names.index(speaker_personality)
            speaker = self.participants[speaker_index]
            message = speaker.respond(self.history[-8:])
            self.history.append(f"{speaker.personality}: {message}")
            pretty.print(f"{speaker.personality.upper()}\n{message}\n", justify="left", highlight=False)
            logging.info(f"{speaker.personality.upper()}: {message}")
    

if __name__ == "__main__":
    api_key = "API_KEY"
    openai = OpenAI(api_key=api_key)

    #clear terminal    
    os.system('clear')
    
    types = {
        1: "conversation", 
        2: "debate",  
        3: "argument",
        4: "meeting",
        5: "brainstorming session",
        6: "lighthearted conversation"
        }
    typelist = ", ".join([f"{key}: {value}" for key, value in types.items()])
    type = int(input(f"[{typelist}]\nEnter a conversation type: "))
    conversation_type = types[type]

    topic = input("Enter a topic: ")

    setting = input("Enter a setting: ")

    # Create a list to store character instances
    characters = []

    # Get user input for characters
    while True:
        character_name = input("Enter character name (blank to stop adding characters): ")
        if character_name == '':
            break
            
        character_instance = character(character_name, conversation_type, topic, setting)
        characters.append(character_instance)
    if len(characters) > 1:
        test = conversation(conversation_type, topic, setting, *characters)

        test.start()
    else:
        sys.exit(1)