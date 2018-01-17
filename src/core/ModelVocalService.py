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

#from modelVocal.modelVocalBuildThread import ModelVocalBuildThread
from core.dao.ModelVocalDAO import Word, Ordre, Mapping, WordDao, Prononciation, OrdreDao
from core.utils.ToolsUtils import Tools

from .Bus import Bus
from core import PATH_VOCAL, PATH_RESOURCES, LANG


class Module():
        
    def getIstance(self):
        print("Chargement du module modelVocalService.....")
        return "modelVocalService", ModelVocalService()

class ModelVocalService(): 

    #liste des actions
    actions = []
    #listes des ordre reçu des modules
    ordres_module = []
    #liste des ordres a envoyer aux satellites
    ordres_json = {}
    vocalReady = True
    #Liste des variables
    variables = {}
    
    numeros_mapping = {}
    
    #list_phrase_sans_variable = []
    #list_phrase_avec_variable = []
    #list_phrase_transformer = []
    
    #REST API
    map_words = {}

    ACTION = {
        "add"     : ["peux tu ajouter", "ajoute", "est ce que tu peux ajouter" ],
        "active"  : ["peux tu activer", "active", "est ce que tu peux activer" ],
        "cancel"  : ["peux tu annuler", "annule", "est ce que tu peux annuler" ],
        "change"  : ["peux tu changer", "change", "est ce que tu peux changer" ],
        "create"  : ["peux tu créer", "crée", "est ce que tu peux créer" ],
        "cut"     : ["peux tu couper", "coupe", "est ce que tu peux couper"],
        "delete"  : ["peux tu supprimer", "supprime", "est ce que tu peux supprimer", "peux tu retirer", "retire", "est ce que tu peux retirer"],
       "desactive": ["peux tu désactiver", "désactive", "est ce que tu peux désactiver" ],
        "display" : ["peux tu afficher", "affiche moi", "affiche", "est ce que tu peux afficher"], 
        "launch"  : ["peux tu lancer", "lance", "est ce que tu peux lancer"],
        "modify"  : ["peux tu modifier",  "modifie", "est ce que tu peux modifier"],
        "put"     : ["peux tu mettre", "met", "met moi", "est ce que tu peux mettre"],
        "put_down": ["peux tu baisser", "baisse", "est ce que tu peux baisser"],
        "reboot"  : ["peux tu redémarrer", "redémarre", "est ce que tu peux redémarrer"],
        "remove"  : ["peux tu effacer", "efface", "est ce que tu peux effacer"],
        "resume"  : ["peux tu reprendre", "reprend", "est ce que tu peux reprendre"],
        "send"    : ["peux tu envoyer", "envoie", "est ce que tu peux envoyer"],
        "show"    : ["peux tu montrer", "montre", "montre moi", "est ce que tu peux montrer"],
        "stop"    : ["peux tu arrêter", "arrête", "est ce que tu peux arrêter", "peux tu stopper", "stop", "est ce que tu peux stopper"],
        "turn_up" : ["peux tu monter", "monte", "est ce que tu peux monter"],  
    }
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ModelVocalService, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.bus= Bus()
        self.tools = Tools()
        self.wordDao = WordDao()
        self.ordreDao = OrdreDao()
        #self.findAllWords()
        #self.findOrdres()
        #self.is_first = True
        
        for action_key in self.ACTION:
            action = self.ACTION[action_key]
            action_obj = Ordre( action_key, "core", "action", True)
            for m in action :
                action_obj.addMappingMessage(key = m, local = 'fr')
            self.actions.append(action_obj)
        

        newDirection = os.path.join(PATH_VOCAL, 'numeros_mapping.json')

        with open(newDirection) as data_file:    
            self.numeros_mapping = json.load(data_file)

        
        #self.vocal_thread = ModelVocalBuildThread([])
        #self.bus.subscribe('loadVocalVariable', self.loadVariable)
       
    def activate(self) :
        self.findAllWords()
        self.findOrdres()
    
    def getOrdres(self) :
        return self.ordreDao.list_ordres    

    def getActions(self) :
        return self.ordreDao.list_actions    
    
    def  getVariables(self) :
        return self.ordreDao.list_variables    
   
    def  getNumeric(self) :
        return self.ordreDao.list_numeric    
   
    def setOrdresbyModules(self, moduleOrdres, moduleVariables, moduleName):
        self.variables[moduleName] = moduleVariables
        for ordre in moduleOrdres:
            if ordre not in self.ordres_module : 
                ordre_ = moduleOrdres[ordre]
                key_ordre = ordre
                module  = moduleName
                type_ = "ordre"
                active = True
                #text_to_speech = ordre_['message_fr'][0]
                ordre_module = Ordre(key_ordre, module, type_, active)
                for m in ordre_['action']:
                    ordre_module.addAction(id_ordre=key_ordre ,key=m, local='fr') 
                #print ordre_['action']
                
                for m in ordre_['message_fr']:
                    ordre_module.addMappingMessage(id_ordre=key_ordre ,key=m, local='fr', )

                if 'input' in ordre_:
                    for m in ordre_['input']:
                        ordre_module.addMappingInput(id_ordre=key_ordre ,key=m, local='fr')
                    ordre_module.input_time = ordre_["input_time"] if "input_time" in ordre_ else "3"

                if 'repete' in ordre_:
                    for m in ordre_['repete']:
                        ordre_module.addMappingRepete(id_ordre=key_ordre ,key=m, local='fr')
                    ordre_module.repete_time = ordre_["repete_time"] if "repete_time" in ordre_ else "3"
                    
                self.ordres_module.append(ordre_module)
            else :
                print(ordre + " existe déja !!!") 

    def createMapping(self, key, value): 
        return Mapping(key, value)          

#    def loadVariable(self, bus, key, obj):
#        module = obj['module']
#        key = obj['key']
#        values  = obj['values']
#        v_obj = self.variables[module]
#        print key + " is loaded !!!!" 
#        list_phrase = []
#        
#        for phrase_avec_variable in self.list_phrase_avec_variable :
#            phrase = "@"
#            if key in phrase_avec_variable :
#                for value in values:
#                    phrase = phrase_avec_variable.replace(key, value)
#                    for var in v_obj :
#                        if var in phrase :
#                            v_o = v_obj[var]
#                            if v_o == 'Int' :
#                                phrase = phrase.replace(var, "deux")
#                    #print phrase
#                    list_phrase.append(phrase)   
#            if "@" not in  phrase and phrase_avec_variable not in  self.list_phrase_transformer:
#                self.list_phrase_transformer.append(phrase_avec_variable)             
#        
#        self.list_phrase_sans_variable.extend(list_phrase)
#
#        print str(len(self.list_phrase_transformer)) + " / " + str(len(self.list_phrase_avec_variable))
#
#        if len(self.list_phrase_avec_variable) == len(self.list_phrase_transformer) :
#            if not self.vocal_thread.isAlive():
#                self.vocal_thread = ModelVocalBuildThread(self.list_phrase_sans_variable)
#                self.vocal_thread.start()

#    def replaceVariable(self, s, key, value):            
#        return s.replace(key, value)           


    list_word_dic_obj = {} 
    list_phrase_fixe = []
    #API REST
    def findAllWords(self, args = None):
        
        print("Chargement des mots...") 

        if len(self.list_word_dic_obj) == 0 :
            print("Chargement de dictionnaires") 
            self.list_word_dic_obj = self.loadDicFrToWords()
            print("Dictionnaire Fr chargé!") 
            list_word_dic_en_obj = self.loadDicEnToWords()
            print("Dictionnaire En chargé!")
            list_word_dic_es_obj = self.loadDicEsToWords()
            print("Dictionnaire es chargé!")
            for word in list_word_dic_en_obj:
                if word in self.list_word_dic_obj:
                    self.list_word_dic_obj[word].vocal.extend(list_word_dic_en_obj[word].vocal)
                else :    
                    self.list_word_dic_obj[word] =list_word_dic_en_obj[word]
            
            for word in list_word_dic_es_obj:
                if word in self.list_word_dic_obj:
                    self.list_word_dic_obj[word].vocal.extend(list_word_dic_es_obj[word].vocal)
                else :    
                    self.list_word_dic_obj[word] =list_word_dic_es_obj[word]
                    
            keyphrase_location = os.path.join(PATH_VOCAL, "keyphrase.list")
            content_keyphrase = self.tools.read_file(keyphrase_location)
            
            for l in content_keyphrase :
                self.list_phrase_fixe.append(self.tools.cleanString(l))
            
            numero_location = os.path.join(PATH_VOCAL, 'numero.json')
            with open(numero_location) as data_file:    
                content_numero = json.load(data_file)
        
            for index in content_numero :
                self.list_phrase_fixe.append(index['label'])
                
            print("Dictionnaires chargé!")
               
        self.map_words = self.wordDao.load()
        self.db_mapping = self.findAllMapping() 
        list_mapping = []
        for mapping in self.db_mapping:
            if mapping.type != "action" and not "@" in mapping.key_vocal:
                list_mapping.append(mapping.key_vocal)    
            
        list_word_app = self.tools.buildVocab(list_mapping)
        list_word_app.extend(self.tools.buildVocab(self.list_phrase_fixe))
        
        for word in list_word_app:
            if word in self.map_words:
                self.map_words[word].setIsPresent(True)
            else :
                newWord = Word(word, 'fr', True)    
                newWord.setIsPresent(False)
                self.map_words[word] = newWord
                if word in self.list_word_dic_obj:
                    self.map_words[word].vocal = self.list_word_dic_obj[word].vocal
        
        list_words_array = []
        for line in self.map_words :
            list_words_array.append(self.map_words[line])
        
        print("Mots chargés") 

        return list_words_array    

        
    #API REST
    def saveWords(self, args):
        self.wordDao.saveOrUpdateWord(args)

    #API REST
    def deleteWords(self, args):
        self.wordDao.delete(args)
    
    #API REST
    def suggestionWords(self, args):
        suggestions = []
        

        if args[0] in self.list_word_dic_obj :
            word = self.list_word_dic_obj[args[0]]
            suggestions.extend(word.vocal)
        else :    
            suggestionG2P = self.tools.launchG2PTools(args)
            for line in suggestionG2P:
                list_ = line.split(' ', 1)
                suggestions.append(Prononciation(list_[1], 'fr'))
        return suggestions

    #API REST
    def createDic(self, args):
        lines = []
        path = os.path.join(PATH_VOCAL, 'custom.dic')
        for index in self.map_words :
            word = self.map_words[index]
            listVocal = []
            for vocal in word.vocal:
                if vocal.local == LANG :
                    listVocal.append(vocal)
            if len(listVocal) > 0:
                lines.extend(self.tools.formatWordToDIC(word.word, listVocal))
        lines.sort() 
        self.tools.write_file(path, lines)
        print("Fichier dic créé !!!")
        
        self.createLM()
        
        self.bus.publish('loadDic')

    def loadDicFrToWords(self):
        list_words = {}
        list_words_dic = self.tools.read_file(os.path.join(PATH_RESOURCES, 'fr', "model_vocal", "frenchWords62K.dic"))
        for line in list_words_dic :
            list_ = line.split(' ', 1)
            mot_general = list_[0].split('(')[0] if '(' in list_[0] else list_[0]
            mot_general_clean = self.tools.cleanString(mot_general)
            if mot_general_clean in list_words:
                list_words[mot_general_clean].addPrononciation(list_[1], 'fr')
            else:     
                w = Word(mot_general_clean, 'fr', False)
                if len(list_) > 1  :
                    w.addPrononciation(list_[1], 'fr')
                list_words[mot_general_clean] = w     
            
        return list_words    


    def loadDicEnToWords(self):
        list_words = {}
        list_words_dic = self.tools.read_file(os.path.join(PATH_RESOURCES, 'en', "model_vocal", "cmudict.hub4.06d.dic"))
        for line in list_words_dic :
            list_ = line.split(' ', 1)
            mot_general = list_[0].split('(')[0] if '(' in list_[0] else list_[0]
            mot_general_clean = self.tools.cleanString(mot_general)
            if mot_general_clean in list_words:
                list_words[mot_general_clean].addPrononciation(list_[1], 'en')
                
            else:     
                w = Word(mot_general_clean, 'en', False)
                if len(list_) > 1  :
                    w.addPrononciation(list_[1], 'en')
                list_words[mot_general_clean] = w     
            
        return list_words    

    def loadDicEsToWords(self):
        list_words = {}
        list_words_dic = self.tools.read_file(os.path.join(PATH_RESOURCES, 'es', "model_vocal", "voxforge_es_sphinx.dic"))
        for line in list_words_dic :
            list_ = line.split(' ', 1)
            mot_general = list_[0].split('(')[0] if '(' in list_[0] else list_[0]
            mot_general_clean = self.tools.cleanString(mot_general)
            if mot_general_clean in list_words:
                list_words[mot_general_clean].addPrononciation(list_[1], 'es')
            else:     
                w = Word(mot_general_clean, 'es', False)
                if len(list_) > 1  :
                    w.addPrononciation(list_[1], 'es')
                list_words[mot_general_clean] = w     
            
        return list_words    
    
    #API REST
    def findActions(self, args):
        self.ordreDao.load()
        action_db = self.ordreDao.list_actions;
        for a in self.actions:
            if a.key_ordre not in action_db :
                action_db[a.key_ordre] = a
            
        list_array = []
        for line in action_db :
            list_array.append(action_db[line])
                
        return list_array
    
    #API REST
    def findNumeric(self, args):
        self.ordreDao.load()
        numeric_db = self.ordreDao.list_numeric;
        for mapping in self.numeros_mapping:
            key_ordre = str(self.numeros_mapping[mapping])
            if key_ordre not in numeric_db :
                ordre =  Ordre(key_ordre, "core", "numeric", True)
                ordre.addMappingMessage(id_ordre=key_ordre ,key=mapping, local='fr', )
                numeric_db[key_ordre] = ordre
            
        list_array = []
        for line in numeric_db :
            list_array.append(numeric_db[line])
                
        return list_array

    
    #API REST
    def findOrdres(self, args=None):
        self.ordreDao.load()
        ordres_db = self.ordreDao.list_ordres;
        for a in self.ordres_module:
            if a.key_ordre not in ordres_db :
                ordres_db[a.key_ordre] = a
            else:
                if hasattr(a, "input_time") :
                    ordres_db[a.key_ordre].input_time = a.input_time     
            
        list_array = []
        for line in ordres_db :
            list_array.append(ordres_db[line])
                
        return list_array

    #API REST
    def saveOrdres(self, ordres):
        self.ordreDao.saveOrUpdate(ordres)

    #API REST
    def deleteOrdre(self, ordre):
        self.ordreDao.deleteOrdreById(ordre[0].id)

    
    #API REST
    """
        Retourne le mapping d'une variable 
            NameVar peut name_serie, name_film etc
    """
    def findMapping(self, nameVar=None):
        self.ordreDao.load()
        ordres_db = self.ordreDao.list_variables;
            
        list_array = []
        for line in ordres_db :
            if ordres_db[line].type == nameVar[0]:
                list_array.append(ordres_db[line])
                
        return list_array
    


    #API REST
    """
        Retourne tous les mapping 
    """
    def findAllMapping(self):
        return self.ordreDao.mappingDao.findAll()
    
    
    def createLM(self):
        print("Creation du fichier LM...")
        list_variabe  = {}

        list_phrase = []
        
        for index in self.ordreDao.list_variables:
            ordre_var = self.ordreDao.list_variables[index]
            if ordre_var.type not in list_variabe:
                list_variabe[ordre_var.type] = []
            for map_var in ordre_var.mappings_messages:
                list_variabe[map_var.type].append(map_var.key_vocal)
        
        keyphrase_path = os.path.join(PATH_VOCAL, 'keyphrase.list')
        content_keyphrase = self.tools.read_file(keyphrase_path)
        
        for l in content_keyphrase :
            list_phrase.append(self.tools.cleanString(l))
        
        numero_path = os.path.join(PATH_VOCAL,'numero.json')
        with open(numero_path) as data_file:    
            content_numero = json.load(data_file)
        
        for index in content_numero :
            list_phrase.append(index['label'])

        for index in self.ordreDao.list_ordres :
            ordre = self.ordreDao.list_ordres[index]
            list_action_message = []
            for a in ordre.actions :
                actions = self.ordreDao.list_actions[a.key_vocal]
                for action in actions.mappings_messages :
                    for m in ordre.mappings_messages :
                        phrase = action.key_vocal + " " + m.key_vocal
                        list_action_message.append(phrase)

            if  len(ordre.mappings_repete) > 0 :
                for r in ordre.mappings_repete :
                    list_phrase.append(r.key_vocal)
             
            if len(ordre.mappings_inputs) == 0 :
                list_phrase.extend(list_action_message)
                continue
                
            for a_m in list_action_message :
                if len(ordre.mappings_inputs) > 0 :
                    for i in ordre.mappings_inputs :
                        if "@" in i.key_vocal:
                            variables = [x[1:] for x in i.key_vocal.split(' ') if '@'  in x]
                            first_time = True
                            phrases_var = []
                            for var in variables:
                                phrases_var_temp = []
                                if var in list_variabe :
                                    if first_time :
                                        first_time = False
                                        for mapping in list_variabe[var]:
                                            p = a_m + " " + i.key_vocal.replace("@" + var, mapping)
                                            phrases_var_temp.append(p)
                                    else :
                                        for mapping in list_variabe[var]:
                                            for phrase in phrases_var:
                                                p = phrase.replace("@" + var, mapping)
                                                phrases_var_temp.append(p)
                                else:
                                    if first_time :
                                        first_time = False
                                        for mapping in ["un", "dix"]:
                                            p = a_m + " " + i.key_vocal.replace("@" + var, mapping)
                                            phrases_var_temp.append(p)
                                    else :
                                        for mapping in ["un", "dix"]:
                                            for phrase in phrases_var:
                                                p = phrase.replace("@" + var, mapping)
                                                phrases_var_temp.append(p)
                                phrases_var = phrases_var_temp
                            list_phrase.extend(phrases_var)                       
                        else:
                            p = a_m + " " + i.key_vocal
                            list_phrase.append(p)
                else :
                    list_phrase.append(a_m)   
            
        
        self.tools.buildStatisticLanguageModel(list_phrase)
        print("Fichier LM créé !!!")
            
if __name__ == "__main__":
    modelVocalService = ModelVocalService()   
    #list_word = ["maïté", "topi"]
    #modelVocalService.buildGraphemeToPhoneme(list_word)
    modelVocalService.ordreDao.deleteAll()
    items = modelVocalService.findOrdres()
    modelVocalService.saveOrdres(items)
    #modelVocalService.buildFileToSLM()
