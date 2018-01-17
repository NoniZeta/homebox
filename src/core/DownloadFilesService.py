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

import hashlib, os
import socket, time, threading

from .Bus import Bus
from core import KEYPHRASE, ACOUSTIC_MODEL_MDEF, ACOUSTIC_MODEL_README,\
    DICTIONARY, ACOUSTIC_MODEL_MEANS, MODEL_LM_VOCAL,\
    ACOUSTIC_MODEL_TRANSITION_MATRICES, ACOUSTIC_MODEL_VARIANCES,\
    ACOUSTIC_MODEL_MIXTURE_WEIGHTS, ACOUSTIC_MODEL_FEAT_PARAMS,\
    ACOUSTIC_MODEL_LICENSE, ACOUSTIC_MODEL_NOISEDICT, PORT_UPDATE_FILES_ADD,\
    PATH_VOCAL


class DownloadFiles(object):

    threads = {}  
    vocal_files = {}
    LIST_FILE_VOCAL = [KEYPHRASE, DICTIONARY, MODEL_LM_VOCAL, ACOUSTIC_MODEL_FEAT_PARAMS, ACOUSTIC_MODEL_LICENSE, 
                 ACOUSTIC_MODEL_MDEF, ACOUSTIC_MODEL_MEANS, ACOUSTIC_MODEL_MIXTURE_WEIGHTS, ACOUSTIC_MODEL_NOISEDICT, 
                 ACOUSTIC_MODEL_README, ACOUSTIC_MODEL_TRANSITION_MATRICES, ACOUSTIC_MODEL_VARIANCES]

    def __init__(self):
        self.bus= Bus()
        self.bus.subscribe('newDeviceConnected', self.lanceClient) 
        self.bus.subscribe('filesChange', self.recalcul) 
        self.checkSumFiles() 

    def getFilesVocal(self):
        return self.vocal_files        

    def recalcul(self, bus, key, obj):
        self.checkSumFiles()  

    def contains(self, ip):
        exist = False
        for t in self.threads:   
            if ip == t:
                exist = True
                break
        return exist

    def lanceClient(self, bus, key, obj):
        ip = obj['ip']
        port= obj['port'] + PORT_UPDATE_FILES_ADD
        try:
            if not self.contains(ip) :
                thread = FileTransfertThread(self, ip, port)
                self.threads[ip] = thread
                thread.start()
        except Exception as e:
            print('DownloadFiles.py : erreur lanceClient : ' + e.__str__())


    def checkSumFiles(self):
        for file_vocal in self.LIST_FILE_VOCAL :
            path_file_vocal = os.path.join(PATH_VOCAL, file_vocal)
            sumMd5 = self.calculSumMD5(path_file_vocal)
            self.vocal_files[file_vocal] = sumMd5 
        
    def calculSumMD5(self, fileToCalcul):
        md5 = hashlib.md5()
        with open(fileToCalcul, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5.update(chunk)
        return md5.hexdigest()            

class FileTransfertThread(threading.Thread):
    
    def __init__(self, parent, ip, port):
        super(FileTransfertThread, self).__init__()
        self.parent = parent   
        self.ip = ip
        self.port = port
        current_dir = os.path.dirname(__file__)
        print("*** port download file   **** : " + str(self.port))
        self.path_file = os.path.join(current_dir, self.parent.path_vocal)    
        
    def run(self): 
        while 1 :
            connect = False
            while not connect:
                try :
                    #      print 'Création socket....'
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    s.bind(('', self.port))
                    s.listen(5)
                    #      print 'En attente du client....'
                    client, address = s.accept()
                    connect = True
                    #     print 'Connected by', address
                except Exception as e:
                    print("DownloadFiles.py => erreur socket : " + e.__str__())  
                    time.sleep(2)

            fileToUpdate = client.recv(1024)
            #print fileToUpdate
            client.send("ok")
            time.sleep(1)
              
            fn = os.path.join(self.path_file, fileToUpdate)
            #print 'Envoi en cours'
            with open(fn, 'rb') as f:
                client.sendall(f.read())
            #print('Envoi effectué')
            time.sleep(0.5)
            client.send("None")
   
