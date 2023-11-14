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
import sys

class character:
    def __init__(self, personality, convo_type, topic, setting):
        
        self.personality = personality
        self.convo_type = convo_type
        self.topic =  topic
        self.setting = setting

    #sets the personality and responds to the history list
    def respond(self, history):
        message = [
            {"role": "system", "content": f"assume the personality of {self.personality}. roleplay as them and stay in character at all times. do not speak as anyone else. your responses should be around a sentence long. do not preface them with your name."},
            {"role": "user", "content": f'''you're the next speaker in a {self.convo_type} about {self.topic}.  the setting is {self.setting}.
here are the last few messages:

{history}

[if the {self.convo_type} is getting repetitive, feel free to move on to a related subject]'''}
            ]
        try:
            response = openai.chat.completions.create(
                model="gpt-4-1106-preview", #change to gpt-3.5-turbo-1106 if you want to save money, but the quality of the responses will be lower
                temperature=1, 
                messages=message)
            self.response_text = response.choices[0].message.content
            return self.response_text
        except Exception as e: #improve this later
            print(e)

class conversation:
    def __init__(self, convo_type, topic, setting, *participants):
        self.convo_type = convo_type
        self.topic = topic
        self.setting = setting
        self.participants = list(participants) #character objects
        self.participants_names = [p.personality for p in self.participants] #get the personalities from the objects
        self.history = [f"[{self.convo_type} hasn't started yet]"] #setup history list
    
    #determines who speaks next
    def next_speaker(self, history):
        #only two characters
        if len(self.participants) == 2:
            last_message = self.history[-1]
            if last_message.startswith(self.participants_names[0]+":"):
                return [self.participants_names[1], "there are only two participants"]
            else:
                return [self.participants_names[0], "there are only two participants"]
        #Three or more characters
        #Uses GPT-4 to decide who should speak next based on the last several messages of history
        else:
            for x in range(2): #retry if it didn't work the first time
                message = [{"role": "user", 
                            "content": f'''based on this {self.convo_type} history and listed participants, reply with the name of the most likely next speaker as it appears before their line and an explanation of your reasoning in the format of "<name>|<reason>" and nothing else.  avoid a round-robin style.

    participant names: {', '.join(self.participants_names)}  

    {history}'''}]
                response = openai.chat.completions.create(
                    model='gpt-4-1106-preview', #this will not work properly with gpt-3.5-turbo, do not change
                    temperature=0, 
                    messages=message)
                response_text = response.choices[0].message.content
                response_text = response_text.split("|", 1) #split the response into speaker name and reasoning
                
                if response_text[0] in self.participants_names: #validate the result and break if sucessful
                    next_speaker = response_text
                    break     
            try:
                return next_speaker
            except:
                return [random.choice(self.participants_names), "the function failed, chosen randomly"] #choose randomly as a fallback
    
    def start(self):
        #logging
        logging.basicConfig(filename='GParTy.log', level=logging.INFO, format='%(message)s')
        
        #text wrap and formatting
        pretty = Console()
        pretty.width=80
        pretty.wrap_text = True
        #colors = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan'] #list of colors to use to colorize messages, will add more/change later

        names = ', '.join(self.participants_names)
        #information about conversation for the log
        logging.info(f"\n{names} have a {self.convo_type} about {self.topic}.  the setting is {self.setting}.".upper())

        #first speaker starts conversation
        speaker = random.choice(self.participants)
        participants = [x for x in self.participants_names if x != speaker.personality] #list of participants without current speaker
        intro = f"start a {self.convo_type} about {self.topic} with {participants}.  the setting is {self.setting}."
        message = speaker.respond(intro) #start conversation
        self.history.append(f"{speaker.personality}: {message}") #add response to history

        #cc = 0 #color choice
        pretty.print(f"\n[bold]{speaker.personality.upper()}[/bold]\n{message}\n", justify="left", highlight=False) #no color
        #pretty.print(f"\n[bold][{colors[cc]}]{speaker.personality.upper()}[/bold]\n{message}[{colors[cc]}]\n", justify="left", highlight=False)
        #cc+=1 #choose next color in list

        logging.info(f"\n{speaker.personality.upper()}: {message}\n")
        
        
        #rest of conversation
        while True:
            time.sleep(6) #delay
            decision = self.next_speaker(self.history[-8:]) #choose next speaker
            logging.info(f"\n*** {decision[0].upper()} is speaking next because {decision[1]} ***\n") #log speaker choice and reasoning
            speaker_personality = decision[0]

            #figure out what character object this personality refers to
            speaker_index = self.participants_names.index(speaker_personality)
            speaker = self.participants[speaker_index]

            message = speaker.respond(self.history[-8:]) #respond to the last several messages of history
            self.history.append(f"{speaker.personality}: {message}") #add response to history

            pretty.print(f"[bold]{speaker.personality.upper()}[/bold]\n{message}\n", justify="left", highlight=False) #no color
            # pretty.print(f"[bold][{colors[cc]}]{speaker.personality.upper()}[/bold]\n{message}[{colors[cc]}]\n", justify="left", highlight=False) 
            # cc+=1
            # if cc == len(colors):
            #     cc = 0

            logging.info(f"\n{speaker.personality.upper()}: {message}\n")

if __name__ == "__main__":
    api_key = "API_KEY"
    openai = OpenAI(api_key=api_key)

    #clear terminal    
    os.system('clear')
    
    types = {
        "1": "conversation", 
        "2": "debate",  
        "3": "argument",
        "4": "meeting",
        "5": "brainstorming session",
        "6": "lighthearted conversation"
        }
    typelist = ", ".join([f"{key}: {value}" for key, value in types.items()])
    print(f"[{typelist}]")
    while True:
        type = input("Enter a conversation type: ")
        if type in types:
            break
        if type == '':
            type = '1'
            break

    conversation_type = types[type]
    topic = input("Enter a topic: ")
    if topic == '':
        topic = "anything"

    setting = input("Enter a setting: ")
    if setting == '':
        setting = "anywhere"

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
        convo = conversation(conversation_type, topic, setting, *characters)
        convo.start()
    else:
        sys.exit(1)