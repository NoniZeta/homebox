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

from collections import namedtuple
import socket, threading, json, time


class SocketBidir():
    
    def __init__(self, ipToConnect, portReceiver, portSender,  master, socketCallback):
        self.ipToConnect = ipToConnect
        self.portReceiver = portReceiver 
        self.portSender = portSender
        self.isConnected = False
        self.isVocalActif = True
        self.master = master
        self.utils = Utils()
        
        self.socketReceiver = SocketReicever(self, self.portReceiver, socketCallback)
        self.socketReceiver.setDaemon(True)
        self.socketReceiver.start()
        
        self.socketSender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if self.master :
            while not self.isConnected :     
                if self.isVocalActif == False:
                    break;
                try:    
                    self.socketSender.connect((self.ipToConnect, self.portSender))    
                    self.isConnected = True
                    self.send(key="connected")
                except Exception as e :
                    self.isConnected = False
                    print("SocketBidir.py, Synchronisation en cours !!! " + self.ipToConnect+ e.__str__())    
                    time.sleep(5)
            print("SocketBidir connected")

    def slaveSenderConnexion(self):
        self.socketSender.connect((self.ipToConnect, self.portSender))               
        self.isConnected = True
        self.send(key="connected")
    
    def send(self, input_time=0, repete_time=0, key=None, message=None):
        try:
            json2Send = self.utils.obj2Json(input_time, repete_time, key, message)
            self.socketSender.send(json2Send.encode())    
        except Exception as e:
            print("Error SocketBiDir send => " + json2Send  )
            print("Error SocketBiDir error=> " + e.__str__())

    def stop(self):
        print("Stop SocketBidir")
        self.isVocalActif = False
        self.socketReceiver.stop()    
        del self.socketSender
        del self.socketReceiver
        print("Stop SocketBidir hecho")
        
 


class SocketReicever(threading.Thread):    
           
    
    def __init__(self, parent, port, socketCallback):
        super(SocketReicever, self).__init__()      
        self.parent = parent
        self.port = port
        self.socketCallback = socketCallback
        self.kill = False
        
    def run(self):

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind(('', self.port))
        self.s.listen(5)
        self.client, self.address = self.s.accept()
            
        while True :
            if self.kill:
                break
            print("Socket_bidir en attente de reception  ")
            dataJson = self.client.recv(4096).decode()
            if dataJson != "": 
                data = self.parent.utils.json2obj(dataJson)
                if data: 
                    if data.key == "connected":
                        if self.parent.master :
                            print("socket ready...")
                        elif not self.parent.master :
                            self.parent.slaveSenderConnexion()     
                    else :
                        self.socketCallback(data)  
            else:
                time.sleep(1)        
        print("Sortie de SocketReicever")            
     
    def stop(self):
        print("Stop SocketReicever")
        self.kill = True   
        self.s.close()  
        
     
class Utils():
    
    def __init__(self):
        pass

    def obj2Json(self, input_time=0, repete_time=0, key=None, message=None ):
        obj = {}
        obj['key'] = key if key else ""
        obj['repete_time'] = repete_time 
        obj['message'] = message if message else  "pas_de_message"
        obj['input_time'] = input_time
        
        if hasattr(obj, "__dict__"):
            jsonObj = json.dumps(obj.__dict__, default=lambda o: o.__dict__)
        else:
            jsonObj = json.dumps(obj, default=lambda o: o.__dict__)
        
        print("Send to the server : " + str(jsonObj))
        return jsonObj
    
    
    def json2obj(self, data): 
            # text_erreur = {"message" : "erreur"}
        result = None
        try:
            eltscount = data.count('{')
            if eltscount > 1 :
                index = data.index('}') + 1
                print(data[:index])
                print(data[index:])
                data = data[:index]
            result = json.loads(data, object_hook=self._json_object_hook)
        except Exception as e:
            print("SocketBidirection json2obj => " + e.__str__())
            #  result = json.loads(text_erreur, object_hook= self._json_object_hook)

        return result
    
    def _json_object_hook(self, d): 
        return namedtuple('X', list(d.keys()))(*list(d.values()))
    

    