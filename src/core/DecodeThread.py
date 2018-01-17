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


from collections import Counter
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
import threading, time

from core.Bus import Bus
from core.SocketBidirection import SocketBidir
from core import PORT_VOCAL_SENDER_ADD, PORT_VOCAL_RECEIVER_ADD


GObject.threads_init()
Gst.init(None)


class DecodeThread(threading.Thread):    
    """
        Thread pour chaque satellite gerant le vocal
    """
    
    frames = []
    kill = False
    end_decoder = False
    st = None
    numeros_mapping = {}
    repete_utt = False
    
    def __init__(self, parent, ip, port):
        super(DecodeThread, self).__init__()
        self.bus= Bus()
        self.message = None 
        self.ordreDetected = None
        self.decoder = parent.decoder
        self.parent = parent
        self.ip = ip
        self.port = port
        #self.ordrePhrases =  []
        self.inputDetected =  []
        self.result = False 
        
        self.actions = self.parent.actions
        self.ordres = self.parent.ordres
        self.variables = self.parent.variables
        self.numeric_mapping = self.parent.numeric
        
        
        for num_map in self.numeric_mapping :
            for mapping in self.numeric_mapping[num_map].mappings_messages :  
                self.numeros_mapping[mapping.key_vocal] = self.numeric_mapping[num_map].key_ordre
            
#        current_dir = os.path.dirname(__file__)
#        script = '../../resources/fr/numeros_mapping.json'
#        newDirection = os.path.join(current_dir, script)

#        with open(newDirection) as data_file:    
#            self.numeros_mapping = json.load(data_file)

        
        self.pipeline = Gst.parse_launch('udpsrc port=1234  caps="application/x-rtp, media=(string)audio, clock-rate=(int)44100, encoding-name=(string)SPEEX, encoding-params=(string)1, payload=(int)110 "'
                           + ' !  rtpspeexdepay ! speexdec ! audioconvert ! audioresample ! audio/x-raw, rate=16000  !  appsink name=app')
        
        
        print ("DecodeThread run => Initialisation  ")
        
    def startSatelliteSynchro(self):    
        self.parent.synchronize("prete", True)
        port_sender = self.port + PORT_VOCAL_SENDER_ADD
        port_receiver = self.port + PORT_VOCAL_RECEIVER_ADD
        print ("*** port sender   **** : " + str(port_sender))
        print ("*** port receiver **** : " + str(port_receiver))
        self.st = SocketBidir(self.ip, port_receiver, port_sender, True, self.socketCallback)

        sink = self.pipeline.get_by_name('app')
        sink.set_property("emit-signals", True)
        sink.connect("new-sample", self.new_sample)

        print ('Prêt a decoder.....')

    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        loop = GObject.MainLoop()
        loop.run()   

    def socketCallback(self, data):
        try:
            print ("socket callback : " + str(data))
            if data.key == "repete_utterance":
                self.repete_utt = True
                self.ordreDetected, self.inputDetected = self.matchOrden(self.recognised[0], self.recognised[1])
                if self.ordreDetected :
                    self.lancerOrdre(self.ordreDetected.module,self.ordreDetected.key_ordre, self.ip, self.inputDetected)
                self.decoder.end_utt()
                self.decoder.start_utt()
                self.bus.publish('monitoringVocalService' , "repete_utterance")
                
            if data.key == "end_utterance":
                self.pipeline.set_state(Gst.State.NULL)
                self.decoder.end_utt()
                self.decoder.start_utt()
                if not self.repete_utt :
                    self.ordreDetected, self.inputDetected = self.matchOrden(self.recognised[0], self.recognised[1])
                    if self.ordreDetected :
                        self.lancerOrdre(self.ordreDetected.module,self.ordreDetected.key_ordre, self.ip, self.inputDetected)
                self.repete_utt = False
                self.ordreDetected = None  
                self.inputDetected = []
                self.result = True
                self.bus.publish('monitoringVocalService' , "end_utterance")
    
            if data.key == "start_utterance":
                self.parent.synchronize("oui_monsieur", True, ip=self.ip)
                self.decoder.end_utt()
                self.decoder.start_utt()
                self.pipeline.set_state(Gst.State.PLAYING)
                self.result = False    
                self.t_start = time.time()
                self.t_end = self.t_start + 1
                self.bus.publish('monitoringVocalService' , "start_utterance")
        except Exception as e :
            print ("DecodeThread:socketCallback =>" + e.__str__() )
            
    def new_sample(self, sink):
        try:
            sample = sink.emit('pull-sample')
            buffer_ = sample.get_buffer()
            #print (str(sample.get_caps().to_string()))
            (result, mapinfo) = buffer_.map(Gst.MapFlags.READ)
            buf = mapinfo.data
            buffer_.unmap(mapinfo)
            if buf:
                self.decode(buf)
        except Exception as e :
            print ("DecodeThread:new_sample =>" + e.__str__() )
        return self.result        
            

    def decode(self, buf):        
        self.decoder.process_raw(buf, False, False)
        self.recognised = self.decodeSpeech(self.decoder.hyp())
        
        if self.repete_utt and self.ordreDetected:
            repete_detected = self.matchRepete(self.ordreDetected.mappings_repete, self.recognised[0], self.recognised[1])
            if repete_detected == "utt":
                self.decoder.end_utt()
                self.decoder.start_utt()
                self.st.send(key="utt_repete")
                self.lancerOrdre(self.ordreDetected.module, self.ordreDetected.key_ordre, self.ip, self.inputDetected)
            if repete_detected == "end":
                self.st.send(key="end_repete")    
        else :
#        if not self.ordresDetected:
            ordre = None
            self.t_start = time.time()
            if self.t_start > self.t_end :
                self.t_end = self.t_start + 1
                try:
             #       print("Recognised => " + self.recognised[0])
                    ordre, self.inputDetected = self.matchOrden(self.recognised[0], self.recognised[1])
                except Exception as e :
                    print("ERROR Recognised => " + e.__str__())
    
    #        if ordres and not self.ordresDetected:
    #            self.inputPhrases = None
    #            self.decoder.end_utt()
    #            self.decoder.start_utt()
            if ordre and not self.ordreDetected:
                self.ordreDetected = ordre
                self.ordrePhrases = self.recognised
                print ("******************** " + ordre.module + " ***************" )
                print ("ordre_detected       : " + ordre.key_ordre)
                print ("origine              : " + self.ip)
                print ("input_time           : " + str(ordre.input_time))
                print ("*******************************************")
                repete_time = 0
                if len(self.ordreDetected.mappings_repete) > 0 :
                    repete_time = 3
                    
                self.st.send(key="ordre_detected", input_time=ordre.input_time, repete_time=repete_time )
#        elif self.ordresDetected :
#            if recognised[0] != "" :
                #print ("inputPhrases : ", recognised[0])
#                self.inputPhrases = recognised    

#            for best in recognised[1] :
#                print best
        
    
    def decodeSpeech(self, hypothesis):
        resultString = ""
        listeMots = []
        if hypothesis != None :
            resultString = hypothesis.hypstr
            for best, i in zip(self.decoder.nbest(), list(range(10))):
                if best != None and best.hyp() != None:
                    listeMots.append(best.hyp().hypstr)
        
        data = {'bestResult': resultString, 'others_words': listeMots }
        self.bus.publish('decodedWords' , data)
        
        return (resultString, listeMots)     
    
    def matchOrden(self, recognizeWord, listOfMatching=None):
        print("matchOrden debut .....")
        #print ("Reco => " + recognizeWord_utf8)

        phrasePrincipal_utf8 = recognizeWord.decode("utf-8")
        listPhraseSecondaire_utf8 = []
        for matching in listOfMatching:
            listPhraseSecondaire_utf8.append(matching.decode("utf-8"))
    
        actions = self.searchAction(phrasePrincipal_utf8, listPhraseSecondaire_utf8)    
        messages, inputs, ordresMessages = self.searchMappings(phrasePrincipal_utf8, listPhraseSecondaire_utf8)
        variables = self.searchVariables(phrasePrincipal_utf8, listPhraseSecondaire_utf8)
        try:
            ordreCompris, inputSelected = self.defineOrdre(actions, inputs, messages, variables, ordresMessages, phrasePrincipal_utf8, listPhraseSecondaire_utf8)
        except Exception as e:
            print ("actions : " + e.__str__())
        
        return ordreCompris, inputSelected


    def searchAction(self, phrasePrincipal, listPhraseSecondaire):
        
        actions=[]
        actionCompris=[]
        
        for item in self.actions:
            list_action = self.actions[item]
            for a in list_action.mappings_messages:
                index = phrasePrincipal.find(a.key_vocal)
                if index > -1 :
  #                  print("add action principale : " + a.key_vocal)
                    actions.append(item)
                    actions.append(item)
                    actions.append(item)
                for matching in listPhraseSecondaire:
                    index = matching.find(a.key_vocal)
                    if index > -1 :
 #                       print("add action secondaire : " + a.key_vocal)
                        actions.append(item)

        if len(actions) > 0:
            for ordre_possible, nb in Counter(actions).most_common() :
 #               print ("Actions 4x : " + ordre_possible + " / " + str(nb))
                if nb > 4:
                    for item in self.actions:
                        a = self.actions[item]
                        if ordre_possible == a.key_ordre:
                            actionCompris.append(a)
        
        return actionCompris

    def searchMappings(self, phrasePrincipal, listPhraseSecondaire):
        
        messages = []
        messagesCompris = []
        inputs = []
        inputsCompris = []
        ordresFiltres = []
        
        for ordre_i in self.ordres:
            ordre = self.ordres[ordre_i]
            list_mappings_msg = ordre.mappings_messages
            for item in list_mappings_msg :
                index = phrasePrincipal.find(item.key_vocal)
                if index > -1 :
#                    print("add message principale : " + item.key_vocal)
                    messages.append(item)
                    messages.append(item)
                    messages.append(item)
                    if ordre not in ordresFiltres :
                        ordresFiltres.append(ordre)
                for matching in listPhraseSecondaire:
                    index = matching.find(item.key_vocal)
                    if index > -1 :
#                        print("add message secondaire: " + item.key_vocal)
                        messages.append(item)
                        if ordre not in ordresFiltres :
                            ordresFiltres.append(ordre)

            list_mappings_inputs = ordre.mappings_inputs
            for item in list_mappings_inputs :
                input_word_tab = item.key_vocal.split(" ")
                variables_detected = [x for x in input_word_tab if "@" in x ]
                item_input = item.key_vocal
                
                for variable_detected in variables_detected :
             #       print("Variable detected : " + variable_detected + " in " + item.key_vocal)
                    item_input = item_input.replace(variable_detected, '').strip() 
            #        print("item_input : " + item_input + " despues  " + item.key_vocal)

                index = phrasePrincipal.find(item_input)
                if index > -1 :
           #         print("add input principale : " + item.key_vocal)
                    inputs.append(item)
                    inputs.append(item)
                    inputs.append(item)
                for matching in listPhraseSecondaire:
                    index = matching.find(item_input)
                    if index > -1 :
          #              print("add input secondaire : " + item.key_vocal)
                        inputs.append(item)

        if len(messages) > 0 :
            counter = Counter(messages)
            list_possible = counter.most_common()
            for item_possible, nb in list_possible :
                if nb > 4 :
                    #print ("messages 4x : " + item_possible.key_vocal + " / " + str(nb))
                    messagesCompris.append(item_possible)


        if len(inputs) > 0:
            counter = Counter(inputs)
            list_possible = counter.most_common()
            for item_possible, nb in list_possible :
                if nb > 4 :
         #           print ("Input 4x : " + item_possible.key_vocal + " / " + str(nb))
                    inputsCompris.append(item_possible)

    
        return  messagesCompris, inputsCompris, ordresFiltres
    
    def searchVariables(self, phrasePrincipal, listPhraseSecondaire):

        variables = []
        variablesCompris = []
        
        for variable in self.variables:
            list_variables = self.variables[variable].mappings_messages
            for item in list_variables :
                index = phrasePrincipal.find(item.key_vocal)
                if index > -1 :
#                    print("add variable principale : " + item.key_vocal)
                    variables.append(variable)
                    variables.append(variable)
                    variables.append(variable)
                for matching in listPhraseSecondaire:
                    index = matching.find(item.key_vocal)
                    if index > -1 :
 #                       print("add variable : " + item.key_vocal)
                        variables.append(variable)

        if len(variables) > 0:
            counter = Counter(variables)
            list_possible = counter.most_common()
            for ordre_possible, nb in list_possible :
                if nb > 4 :
                    for item in self.variables:
                        v = self.variables[item]
                        if ordre_possible == v.key_ordre:
    #                        print ("Variables 4x : " + ordre_possible + " / " + str(nb))
                            variablesCompris.append(v)                 

        return variablesCompris
    
    def findNumeric(self, phrasePrincipal, listPhraseSecondaire, input_):
        """
            Input contient @numeric. On recherche le numero correspondant
        """    
        #print ("Debut DecodeThread : findNumeric ...")
        #input_word_tab = input_.split(" ")
        numeros = []
        index = input_.index("@numeric")
        #print ("phrase principale")
        first_part_input = input_[:index].strip()
        index_first_part_input = phrasePrincipal.find(first_part_input)
        #print ("first_part_input : "  + first_part_input + " trouvé a l'index "+ str(index_first_part_input))
        if index_first_part_input > 0 :
            #  print("part 0 : " + phrasePrincipal.split(first_part_input)[0])
            #  print("part 1 : " + phrasePrincipal.split(first_part_input)[1])
            
            input_numeric_part_list = phrasePrincipal.split(first_part_input)
            for input_numeric_part in input_numeric_part_list: 
                input_numeric_part = input_numeric_part.strip().split(" ")
                numero = None
                numero_string = ""
                numero_string_clean = ""
                for word in input_numeric_part:
                    #print ("word : "  + word)
                    if word in self.numeros_mapping :
                        numero_string = numero_string_clean + " " + word 
                        numero_string_clean = numero_string.strip()
                        if numero_string_clean in self.numeros_mapping :
                            numero =  self.numeros_mapping[numero_string_clean]
                    #print ("numero trouvé  : " + str(numero))
                    else :
                        if numero :
                            numeros.append(numero)
                            numeros.append(numero)
                            numeros.append(numero)
                            #print ("numero ajouté  : " + str(numero))
                        break
        
        # print ("MAtching")
        for matching in   listPhraseSecondaire :      
            index_first_part_input = matching.find(first_part_input)
            if index_first_part_input > 0 :
                input_numeric_part_list = matching.split(first_part_input)
                for input_numeric_part in input_numeric_part_list:
                    input_numeric_part = input_numeric_part.strip().split(" ")
                    numero = None
                    numero_string = ""
                    for word in input_numeric_part:
                        #print ("word : "  + word)
                        if word in self.numeros_mapping :
                            numero_string = numero_string + " " + word 
                            numero_string_clean = numero_string.strip()
                            if numero_string_clean in self.numeros_mapping :
                                numero =  self.numeros_mapping[numero_string_clean]
                        else :
                            if numero :
                                numeros.append(numero)
                            break
            
        #print ("List des possibles")        
        list_possible = []            
        if len(numeros) > 0:
            list_possible = Counter(numeros).most_common()
        
        numeric, nb = list_possible[0] if len(list_possible) > 0  else (-1,-1) 
        result = None
        if nb > 4 :
            result = self.numeric_mapping[numeric]
        
        return result

    def defineOrdre(self, actionCompris, inputsCompris, messagesCompris, variablesCompris, ordresFiltres, phrasePrincipal, listPhraseSecondaire):        

        #print ("Debut defineOrdre")
        ordresActions = []
        ordreCompris = None
        inputSelected = None

        try:        
            if len(messagesCompris) > 0 and len(actionCompris) > 0:
                for item in ordresFiltres :
                    for action in actionCompris :
                        for a in item.actions : 
                            if action.key_ordre == a.key_vocal :
                                if item not in ordresActions :
                                    ordresActions.append(item) 
            else :                
                ordresActions = ordresFiltres

            ordresActionsInputs = {} 
            if  len(ordresActions) > 0 :
                #print ("ordresActionsInputs")                      
                # ordreCompris = ordresActions[0]
                for ordre in ordresActions : 
                    if len(ordre.mappings_inputs) > 0 and len(inputsCompris) > 0 :
                        for ordreInput in ordre.mappings_inputs :
                            for input_ in inputsCompris :
                                if ordreInput.key_vocal == input_.key_vocal:       
                                    if ordre.key_ordre not in ordresActionsInputs:
                                        ordresActionsInputs[ordre.key_ordre] = {}
                                    if "@" not in input_.key_vocal:
                                        ordresActionsInputs[ordre.key_ordre][input_.key_vocal] = []
                                        #           print ("Add Selected Input : " + input_.key_vocal)
                                    else :
                                        variablesInputs = [x[1:] for x in input_.key_vocal.split(' ') if '@'  in x]
                                        for v_i in variablesInputs:
                                            #print ("variablesInputs : "  + v_i)
                                            if v_i == "numeric" :
                                                numeroSelected = self.findNumeric(phrasePrincipal, listPhraseSecondaire, input_.key_vocal)
                                                if numeroSelected :
                                                    #print ("=====> numero trouvé : " + v_i + " : " + str(numeroSelected.key_ordre))
                                                    if input_.key_vocal not in ordresActionsInputs[ordre.key_ordre] :
                                                        ordresActionsInputs[ordre.key_ordre][input_.key_vocal] = []
                                                    #   print ("Add Selected Input : " + input_.key_vocal)
                                                    ordresActionsInputs[ordre.key_ordre][input_.key_vocal].append(numeroSelected)
                                            #    numero = self.findNumeric()
                                            else :
                                                for item in variablesCompris:
                                                    #print("Variable type : " + item.type)
                                                    if item.type == v_i :
                                                        if input_.key_vocal not in ordresActionsInputs[ordre.key_ordre] :
                                                            ordresActionsInputs[ordre.key_ordre][input_.key_vocal] = []
                                                        #      print ("Add Selected Input : " + input_.key_vocal)
                                                        ordresActionsInputs[ordre.key_ordre][input_.key_vocal].append(item)
        except Exception as e :
            print ("DecodeThread:matchOrden_2 =>" + e.__str__() )

        try:                
            if len(ordresActionsInputs) == 1 :
#                ordreCompris = ordresActionsInputs
                for item in ordresActionsInputs: 
                    ordreCompris = self.ordres[item]
                    inputSelected = ordresActionsInputs[item]
            elif len(ordresActions) == 1 :
                ordreCompris = ordresActions[0]                                           
            else :
                pass
                                                    
        except Exception as e :
            print ("DecodeThread:matchOrden_3 =>" + e.__str__() )

        data = {'actions': actionCompris, 'messages': messagesCompris, 'inputs': inputsCompris, 'variables': variablesCompris }
        self.bus.publish('vocalDetection' , data)

        data = {'ordre': ordreCompris, 'input': inputSelected }
        self.bus.publish('ordreDetected' , data)

        return ordreCompris, inputSelected     

    def matchRepete(self, list_mappings_repete,  phrasePrincipal, listPhraseSecondaire):
        
        repetes = []
        repetesCompris = None
        
        for item in list_mappings_repete :
            index = phrasePrincipal.find(item.key_vocal)
            if index > -1 :
#                    print("add message principale : " + item.key_vocal)
                repetes.append(item)
                repetes.append(item)
                repetes.append(item)
            for matching in listPhraseSecondaire:
                index = matching.find(item.key_vocal)
                if index > -1 :
#                        print("add message secondaire: " + item.key_vocal)
                    repetes.append(item)

        if len(repetes) > 0 :
            counter = Counter(repetes)
            list_possible = counter.most_common()
            for item_possible, nb in list_possible :
                if nb > 4 :
                    if item_possible.key_vocal == "stop" or item_possible.key_vocal == "ok" : 
                        repetesCompris = "end"
                    else :    
                        repetesCompris = "utt"

        return repetesCompris



    
    def stop(self):
        print ("Vocal stop le thread du port : " + str(self.port))
        # self.kill = True
        try :
            self.decoder.end_utt()
            self.decoder.start_utt()
            if hasattr(self, 'st') :
                self.st.stop()
                del self.st 
            if hasattr(self, 'pipeline') :    
                self.pipeline.set_state(Gst.State.NULL)
                del self.pipeline
            self.parent.synchronize("Stop Vocal")
        except Exception as e:
            print ("Error =>  DecodeThread stop : " + str(self.port))   
            print (e.__str__())  
        
    def getInfo(self):
        return self.ip, self.port    
    
    def lancerOrdre(self, groupe, ordre, address=None, input_=None):
        self.parent.synchronize(ordre, True, ip=address)  
        self.parent.synchronize("oui_monsieur", True, ip=address)  
        
        data = {'groupe': groupe, 'origine': address, 'ordre': ordre, 'input' : input_ }
        self.bus.publish('vocalOrdre' , data)
