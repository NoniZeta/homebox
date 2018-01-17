#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Created on 18/06/2016

@author: Arnaud
'''

import logging
import uuid

from core import HOST_DB, PORT_DB, USER_DB, PASSWD_DB, DB_DB
import mysql.connector


logger = logging.getLogger('ModelVocalDAO')

class ModelVocalDAO():
                
    def __init__(self):
        self.wordDao = WordDao()
        self.ordreDao = OrdreDao()

class Word():
    
    def __init__(self, word, local, active):
        self.word = word
        self.local = local
        self.active = active
        self.isPresent = False
        self.vocal = [] 
    
    def setId(self, id_):
        self.id = id_     
        
    def addPrononciation(self, grapheme, local):
        self.vocal.append(Prononciation(grapheme, local))

    def setIsPresent(self, isPresent):
        self.isPresent = isPresent     
        
class Prononciation():
    
    def __init__(self, grapheme, local):
        self.grapheme = grapheme
        self.local = local

    def setId(self, id_):
        self.id = id_       

class Ordre():
    
    def __init__(self, key_ordre, module, type_, active):
        self.key_ordre = key_ordre
        self.module = module
        self.type = type_
        self.active = active
        self.actions = []
        self.mappings_messages = []
        self.mappings_inputs = []
        self.mappings_repete = []
        self.textToSpeech = []
        self.input_time = "0"
        self.repete_time = "0"

    def setId(self, id_):
        self.id = id_       
    
    def addMapping(self, mapping):
   
        if mapping.type == "input":
            self.mappings_inputs.append(mapping)    
        elif mapping.type == "repete":
            self.mappings_repete.append(mapping)    
        elif mapping.type == "action":
            self.actions.append(mapping)    
        else :
            self.mappings_messages.append(mapping) 

    def addMappingMessage(self, key = None, id_ordre=None, local = None, type_ = None):
        self.mappings_messages.append(Mapping(id_ordre, key, local, "message"))    
    def addMappingInput(self,  key = None,id_ordre=None, local = None, type_ = None):
        self.mappings_inputs.append(Mapping(id_ordre, key, local, "input"))    

    def addMappingRepete(self,  key = None, id_ordre=None, local = None, type_ = None):
        self.mappings_repete.append(Mapping(id_ordre, key, local, "repete"))    

    def addAction(self, key = None, id_ordre=None, local = None, type_ = None):
        self.actions.append(Mapping(id_ordre, key, local, "action"))    

    def addTexToSpeech(self, local, text):
        self.textToSpeech.append(TextToSpeech(local, text))    

class Mapping():
    
    def __init__(self, id_ordre = None,  key = None, local = None, type_ = None ):
        self.id_ordre = id_ordre
        self.key_vocal = key
        self.local = local
        self.type = type_

    def setId(self, id_):
        self.id = id_       
        
        
class TextToSpeech():

    def __init__(self, local, text, id_ordre = None ):
        self.id_ordre = id_ordre
        self.local = local
        self.text_to_speech = text

    def setId(self, id_):
        self.id = id_       


class WordDao():  
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WordDao, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    list_words = {}
    
    def __init__(self):
        pass
    
    def load(self):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        cr.execute("SELECT * FROM word_prononciation")
        results = cr.fetchall()
        cr.close()    
        _db.close()
        self.list_words = {}
        for (id_b, word_b, local_b, active, grapheme, local_graheme) in results:
            try:
                word = word_b.decode("utf-8")
                id_ = id_b.decode("utf-8")
                local = local_b.decode("utf-8")
                if word not in self.list_words :
                    self.list_words[word] = Word(word, local, active)
                mot =  self.list_words[word]
                mot.setId(id_)
                mot.addPrononciation(grapheme, local_graheme)
            except Exception as e :
                print(("load " + e.__str__()))    
        return self.list_words  
          
          
    def saveOrUpdateWord(self, words):  
        
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToInsert = """
                        INSERT INTO word (id, word, local) 
                        VALUES (%s, %s, %s)
                     """
                     
        sqlToUpdate = """
                        UPDATE word SET  word = %s, 
                                         local = %s
                        where id = %s
                      """   
        
        for word in words:
            
            if hasattr(word, 'id'):
                id_ = word.id
                data= (word.word, word.local, word.id)
                cr.execute(sqlToUpdate, data)
            else:    
                id_ = str(uuid.uuid4())
                data= (id_, word.word, word.local)
                try:
                    cr.execute(sqlToInsert, data)
                except Exception as e:
                    print(("saveOrUpdateWord " + e.__str__()))
            self.saveOrUpdatePrononciation(id_, word.vocal)
            
        _db.commit()      
        cr.close()    
        _db.close()     
        
        
    def deleteAll(self):  
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToDeleteWord = """
                        delete from word
                     """
        sqlToDeletePrononciation = """
                        delete from prononciation
                     """
        cr.execute(sqlToDeleteWord)
        cr.execute(sqlToDeletePrononciation)
        _db.commit()      
        cr.close()    
        _db.close()    
        
    def delete(self, ids):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()

        for id_ in ids :
            self.deletePrononciationByWord(id_)
            sqlToDeleteWord = "delete from word where id = '%s' ;"   %id_
            cr.execute(sqlToDeleteWord)
            _db.commit()      
        cr.close()    
        _db.close()    
        

        
    def deletePrononciationByWord(self, idWord):  
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlDelete = "delete from prononciation where id_word = '%s' ;"   %idWord
        cr.execute(sqlDelete)     
        _db.commit()
    
            
    def saveOrUpdatePrononciation(self, word, prononciations):
        self.deletePrononciationByWord(word)
              
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToInsert = """
                        INSERT INTO prononciation (id, id_word, local, vocal) 
                        VALUES (%s, %s, %s, %s)
                     """
                     
        for item in prononciations:
            id_ = str(uuid.uuid4())
            
            data= (id_, word, item.local, item.grapheme.strip().lower().rstrip('\n'))
            cr.execute(sqlToInsert, data)
           
        _db.commit()   
        cr.close()    
        _db.close()          
                      

class MappingDao():  
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(MappingDao, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    
    
    def __init__(self):
        pass
    
    
    def findAll(self):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        cr.execute("SELECT * FROM mapping" )
 
        list_mappings = []
        for (id_, id_ordre, key_vocal, local, type_) in cr:
            mapping = Mapping( id_ordre, key_vocal, local, type_)
            mapping.setId(id_)
            list_mappings.append(mapping)
        
        cr.close()    
        _db.close()
        return list_mappings 
    
    def load(self, id_ordre):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        cr.execute("SELECT * FROM mapping where id_ordre = '%s'" %id_ordre )
 
        list_mappings = []
        for (id_, id_ordre, key_vocal, local, type_) in cr:
            mapping = Mapping( id_ordre, key_vocal, local, type_)
            mapping.setId(id_)
            list_mappings.append(mapping)
        
        cr.close()    
        _db.close()
        return list_mappings 

    def deleteAll(self):  
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToDelete = """
                        delete from mapping
                     """
        cr.execute(sqlToDelete)
        _db.commit()      
        cr.close()    
        _db.close()    
     
    def deleteMappingByOrdre(self, idOrdre):  
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlDelete = "delete from mapping where id_ordre = '%s' ;"   %idOrdre
        cr.execute(sqlDelete)     
        _db.commit()   
        
    def saveOrUpdate(self, id_ordre, mappings):      
        if len(mappings) == 0 :
            return
        
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToInsert = """
                        INSERT INTO mapping (id, id_ordre, key_vocal, local, type) 
                        VALUES (%s, %s, %s, %s, %s)
                     """
                     
        sqlToUpdate = """
                        UPDATE mapping SET  id_ordre = %s, 
                                            key_vocal = %s,
                                            local = %s,
                                            type = %s
                        where id = %s
                  """   
        for item in mappings:
        
        #    if hasattr(item, 'id'):
        #        data= (item.id_ordre, item.key_vocal, item.local, item.type, item.id)
        #        cr.execute(sqlToUpdate, data)
        #        _db.commit()   
        #    else:    
            id_ = str(uuid.uuid4())
            data= (id_, id_ordre, item.key_vocal, item.local, item.type)
            cr.execute(sqlToInsert, data)
            _db.commit()   
   
        cr.close()    
        _db.close()          


class OrdreDao():  
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(OrdreDao, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance
    
    list_ordres = {}
    list_actions = {}
    list_variables = {}
    list_vocal = {}
    
    def __init__(self):
        self.mappingDao = MappingDao()
    
    def load(self):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        cr.execute("SELECT * FROM ordres")
        results = cr.fetchall()
        cr.close()    
        _db.close()
    
        self.list_ordres = {}
        self.list_actions = {}
        self.list_variables = {}
        self.list_numeric = {}
        self.list_vocal = {}
    
        for (id_, key_ordre, module, type_ordre, active) in results:
            ordre = Ordre(key_ordre, module, type_ordre, active)
            ordre.setId(id_)
            list_mapping = self.mappingDao.load(id_)
            for item in list_mapping : 
                ordre.addMapping(item)
            if type_ordre == "ordre":
                if key_ordre not in self.list_ordres :
                    self.list_ordres[key_ordre] = ordre
            elif type_ordre == "action":
                if key_ordre not in self.list_actions :
                    self.list_actions[key_ordre] = ordre
            elif type_ordre == "vocal":
                if key_ordre not in self.list_vocal :
                    self.list_vocal[key_ordre] = ordre
            elif type_ordre == "numeric":
                if key_ordre not in self.list_numeric :
                    self.list_numeric[key_ordre] = ordre

            else :
                if key_ordre not in self.list_variables :
                    self.list_variables[key_ordre] = ordre
        return self.list_ordres 

    def deleteAll(self):  
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToDelete = """
                        delete from ordres
                     """
        cr.execute(sqlToDelete)
        _db.commit()      
        cr.close()    
        _db.close()    

    def deleteOrdreById(self, idOrdre):  
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlDelete = "delete from ordres where id = '%s' ;"   %idOrdre
        sqlDelete_mapping = "delete from mapping where id_ordre = '%s' ;"   %idOrdre
        cr.execute(sqlDelete)
        cr.execute(sqlDelete_mapping)
        _db.commit()      
        cr.close()    
        _db.close()    

        
        
    def saveOrUpdate(self, ordres):      
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToInsert = """
                        INSERT INTO ordres (id, key_ordre, module, type, active) 
                        VALUES (%s, %s, %s, %s, %s)
                     """
                     
        sqlToUpdate = """
                        UPDATE ordres SET  key_ordre = %s, 
                                           module = %s,
                                           type = %s,
                                           active = %s
                        where id = %s
                  """   
        for item in ordres:
        
            id_ = str(uuid.uuid4()) 
        
            if hasattr(item, 'id'):
                id_ = item.id
                data= (item.key_ordre, item.module, item.type, item.active, item.id)
                cr.execute(sqlToUpdate, data)
            else:    
                data= (id_, item.key_ordre, item.module, item.type, item.active)
                cr.execute(sqlToInsert, data)
        
            self.mappingDao.deleteMappingByOrdre(id_)   
            self.mappingDao.saveOrUpdate(id_, item.mappings_messages)
            self.mappingDao.saveOrUpdate(id_, item.mappings_inputs)
            self.mappingDao.saveOrUpdate(id_, item.mappings_repete)
            self.mappingDao.saveOrUpdate(id_, item.actions)
                
        _db.commit()   
        cr.close()    
        _db.close()          

def testWordDao():
    dao = OrdreDao()
    #items = []
    #word = Word("test", "fr_FR")
    #word.addPrononciation("tt ee zz tt", "fr_FR")
    #word.addPrononciation("tt ee ss tt", "fr_FR")
    #words.append(word)
    
    #dao.saveOrUpdateWord(words)
    items = dao.load()
    
    for m in items :
        print(m)
    
    #dao.deleteAll()

if __name__ == "__main__":
    testWordDao()
    
                      
            
    