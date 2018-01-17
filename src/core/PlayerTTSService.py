#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018 <boutin_arnaud@hotmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import json
import os
import socket

from gtts import gTTS
import pygame
from core import PORT_TTS


CURRENT_DIR = os.path.dirname(__file__)
DIR_MP3 = os.path.join(CURRENT_DIR, "../resources")

# install requests.2.2.1 python setup.py install
class PlayerTTS:    
 
    lang = 'fr'

    def __init__(self):
        pass
        
    def setLang(self, lang):
        self.lang = lang

    def save(self, savefile, text):
        if not os.path.exists(savefile):
            tts = gTTS(text=text, lang=self.lang)
            tts.save(savefile)
            
              
    def play(self, text_key, ip = None):   
        try: 
            fileTmp = DIR_MP3 + "/" + self.lang + "/mp3/" + text_key + ".mp3"
            
            current_dir = os.path.dirname(__file__)
            script = '../src/static/resources/locales/' + self.lang + '/messages.json'
            newDirection = os.path.join(current_dir, script)

            with open(newDirection) as locale_file:    
                locale_data = json.load(locale_file)
        
            text = locale_data[text_key]["message"]
           
            self.save(fileTmp, text)
            if ip == None: 
                self.playLocal(fileTmp)
            else :
                self.sendToHost(fileTmp, ip)    
        except Exception as e :
            print("Player_TTS play : " + e.__str__())      
            print("textto play : " + text_key.__str__())

          
    def sendToHost(self, fileTmp, ip):      
        try:    
            print("Google_tts.py : adresse ip d'envoi : %s ", ip) 
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((ip, PORT_TTS))
            with open(fileTmp, 'rb') as f:
                s.sendall(f.read())
                  
        except Exception as e :
            print("Google_TTS connect and send : " + str(e))      
        finally:
            s.close()    
        
    def playLocal(self, fileTmp):
        try:
            pygame.mixer.init(18000, 16, 1, 4096)
            pygame.mixer.music.load(fileTmp)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy(): 
                pygame.time.Clock().tick(10)
            
        except Exception as e:
            print("Player pygame erreur : " + e.__str__())      
        finally:    
            pygame.mixer.quit()

if __name__ == "__main__":
#    DIR_MP3 = "../resources/fr/hello.mp3"
    text_fr = "Bonjour monsieur Noni, que puis-je pour vous"
    text_es = "Hola señorita Topi, que puedo hacer por usted"
    gtts = PlayerTTS()
    gtts.lang = 'fr'
    gtts.play("plus_fort")
    
#    gtts = PlayerTTS()
#    gtts.play()
    #pygame.mixer.pre_init(44100, -8, 2, 2048)
    #pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=2048)

    print('fin')
