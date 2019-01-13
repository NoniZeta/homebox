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


import os

from core.PlayerTTSService import PlayerTTS

from core.Bus import Bus
from core.DecodeThread import DecodeThread
from core import PORT_VOCAL_ADD, PATH_VOCAL, ACOUSTIC, DICTIONARY,\
    MODEL_LM_VOCAL
#from pocketsphinx.pocketsphinx import Decoder

#hmmd_file = 'acoustic'
#dictp_file = 'custom.dic'
#lmdir_file = 'custom.lm.bin'

hmmd = os.path.join(PATH_VOCAL, ACOUSTIC)
dictp = os.path.join(PATH_VOCAL, DICTIONARY)
lmdir = os.path.join(PATH_VOCAL, MODEL_LM_VOCAL)


class Module():
        
    def getIstance(self):
        print( "Chargement du module Vocal.....")
        return "vocal", Vocal()


class Vocal(object):
    
    VARIABLES = {}

    ORDRES = {
        "fin_ordre"        : { "function"      : "finOrdre",
                                "action"        : ["launch"],
                                "message_fr"    : ["fin ordre"],
                              },
        "reboot_box"       : { "function"      : "rebootBox",
                                "action"        : ["launch", "reboot"],
                                "message_fr"    : ["redémarrage complet", "complet"],
                              },
        "reboot_sat"       : { "function"      : "rebootsat",
                                "action"        : ["launch", "reboot"],
                                "message_fr"    : ["redémarrage satellite",  "satellite"],
                              },
              }

    
    threads = {} 
    
    decoder = None 
   
    def __init__(self):
        self.bus= Bus()
        self.gtts = PlayerTTS()
        self.isActive = True
        self.bus.subscribe('newDeviceConnected', self.lanceVocalconnect) 
        self.bus.subscribe('deviceDeconnected', self.deconnectVocal) 
        self.bus.subscribe('vocalOrdre', self.lanceVocalOrdre) 
        self.bus.subscribe('loadDic', self.lanceLoadDecoder) 

    def lanceVocalOrdre(self, bus, key, obj):
        """
         Point d'entré du module pour gérer les ordres associés par la reconnaissance vocale
        """    
        groupe = obj['groupe']
        if groupe != 'vocal' :
            return     
        
        ordre = self.ORDRES[obj['ordre']]
        
        print ("Ordre lancé : " + obj['ordre'])
        #print ("appel de la function : " + ordre["function"])
        print ("origine  : " + obj["origine"])
        # print ("recognised  : " + str(obj["recognised"]))
        print ("input  : " + str(obj["input"]))

    def contains(self, ip):
        """"
             Utils qui permet de vérifier si l'IP est deja contenu dans la liste
             return @boolean 
        """
        exist = False
        for t in self.threads:   
            if ip == t:
                exist = True
                break
        return exist        

    
    def lanceVocalconnect(self, bus, key, obj):
        """
            Reçu sur le bus par le déclenchement de l'événement 'newDeviceConnected'
            obj = {
                ip : 'ip du satelite',
                port : 'port de connexion + 1'
            }
            
            Création d'un thread VocalThread
        """
        ip = obj['ip']
        port= obj['port'] + PORT_VOCAL_ADD
        try:
            if not self.contains(ip) :
                thread = DecodeThread(self,  ip, port)
                self.threads[ip] = thread
                if self.isActive :
                    thread.startSatelliteSynchro()
                    thread.start()
        except Exception as e:
            print ('Vocal.py : erreur lanceVocalconnect : ' + str(e.__str__()))
        
    def deconnectVocal(self, bus, key, obj):
        """
            Reçu sur le bus par le déclenchement de l'événement 'deviceDeconnected'
            va détruire le thread a la deconnexion du satelite
        """   
        ipDeconnected = obj['ip']
        for thread in self.threads: 
            if ipDeconnected == thread :
                print ("Destruction du thread vocal : " + ipDeconnected)
                t = self.threads[thread] 
                if t.isAlive() :
                    t.stop()
        del self.threads[ipDeconnected]     
        
    def isVocalActive(self, args = None):
        """
            return un objet JSON de isVocal
            utiliser lors de la connexion du satellite pour lui renvoyer si le vocal est actif ou pas. Activation par IHM  
        """
        obj = {}
        obj['vocalActive'] = self.isVocal()
        return obj
           
    def isVocal(self):
        return self.isActive
    
    def getFilesVocal(self):
        return self.vocal_files

    def setLang(self, args):
        lang = args[0].lang    
        self.gtts.setLang(lang)
        return 'test'

    def activate(self):
        self.lanceLoadDecoder()
        
    
    def lanceLoadDecoder(self, bus = None, key = None, obj = None):
        config = Decoder.default_config()
        config.set_string(str('-hmm'), str(hmmd))
        config.set_string(str('-lm'), str(lmdir))
        config.set_string(str('-dict'), str(dictp))
        self.decoder = Decoder(config)
        
        self.decoder.start_utt()
    
    def startVocal(self, args = None):    
        """
            Activer par l'IHM
        """
        print ("vocal.py : Start vocal")
        self.isActive = True
        for ip in self.threads: 
            thread =  self.threads[ip]
            ip, port = thread.getInfo()
            print ("vocal.py : Start vocal thread = > " + str(ip))
            newT = DecodeThread(self, self.decoder, ip, port)
            self.threads[ip] = newT
            if not newT.isAlive() :
                newT.startSatelliteSynchro()
                newT.start()
                print ("vocal.py : Start vocal thread = > " + str(ip) + " => Ok ")
        
        
    def stopVocal(self, args = None):   
        """
            Activer par l'IHM
        """
        print ("vocal.py : Stop vocal")
        self.isActive = False
        for thread in self.threads: 
            t = self.threads[thread] 
            ip, port = t.getInfo()
            print ("vocal.py : Stop vocal thread = > " + str(ip))
            if t.isAlive() :
                t.stop()
                print ("vocal.py : Stop vocal thread = > " + str(ip) + " => Ok ")
                    
    def synchronize(self, text, play = False, label = None, ip=None):
        try :
            self.bus.publish('monitoringVocalService' , text)
            textToRead = label if label else text
            #   print textToRead 
            if play and textToRead != '': 
                self.gtts.play(textToRead, ip)
        except Exception as e :
            print ('Vocal.py => synchronize : ' + e.__str__()   )         
     
     
    def loadActions(self, actions):
        self.actions = actions       

    def loadOrdres(self, ordres):
        self.ordres = ordres       

    def loadVariables(self, variables):
        self.variables = variables       

    def loadNumeric(self, numeric):
        self.numeric = numeric       


  
def main():
    vocal = Vocal()
    vocal.startVocal()

if __name__ == "__main__":
    hmmd = '../model_vocal/acoustic/'
    lmdir = '../model_vocal/french3g62K.lm.dmp'
    dictp = '../model_vocal/frenchWords_light.dic'
    key_phrase_list = '../doc/keyphrase.list'
    main()
