#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Created on 22/02/2015

@author: Arnaud
'''

from __future__ import print_function
from __future__ import unicode_literals

import json
from io import StringIO

import collections, os
import urllib2
import websocket, conf
import threading
from Bus import Bus
from module.dao.kodiDao import KodiDAO, Episode, Film, Serie
from convertInNumeric import Convert
from xbmcjson import XBMC, PLAYER_VIDEO, PLAYER_DEFAULT
#from py import playerMusic
from modelVocal.toolsUtils import Tools

class Module():
          
    def getIstance(self):
        print ("Chargement du module Kodi.....")
        return "kodi", Kodi()
    
class Kodi():
    
    VARIABLES = {'@name_serie'      : {},
                 '@name_film'       : {},
                 '@name_music'      : {},
                 '@name_playlist'   : {},
                 '@episode'         : 'Int',
                 '@saison'          : 'Int',
                 '@episod_id'       : 'Int',
                 '@film_id'         : 'Int'
                } 

    ORDRES = {
        "liste_film"        : { 
                                "action"        : ["display", "show"],
                                "message_fr"    : ["liste film"],
                                "input"         : ["récent", "ordre alpha", "note", "date ajout"]
                              },
        "liste_serie"       : { 
                                "action"        : ["display", "show"],
                                "message_fr"    : ["liste série"],
                                "input"         : ["récent", "ordre alpha", "note", "date ajout"]
                              },
        "liste_music"       : { 
                                "action"        : ["display", "show"],
                                "message_fr"    : ["liste musique"],
                                "input"         : ["récent", "ordre alpha", "note", "date ajout"]
                              },
        "lance_episode"     : { 
                                "action"        : ["launch", "put"], 
                                "message_fr"    : ["épisode"],
                                "input"         : ["suivant de @name_serie", 
                                                   "@episode de la saison @saison de @name_serie", 
                                                   "de @name_serie saison @saison épisode @episode", 
                                                   "de @name_serie numéro @episod_id", 
                                                   "numéro @episod_id de @name_serie"]
                              },
        "lance_episode_2"   : { 
                                "action"        : ["resume"], 
                                "message_fr"    : ["la série", "épisode", "la suite", "la suite de la série"],
                                "input"         : ["de @name_serie"]
                              },
        "lance_film"        : {  
                                "action"        : ["launch", "put"], 
                                "message_fr"    : ["film"],
                                "input"         : ["@name_film"]
                              },  
        "resume_film"       : {  
                                "action"        : ["resume"], 
                                "message_fr"    : ["film"],
                                "input"         : ["@name_film"],
                              }, 
        "lance_music"        : { 
                                "action"        : ["launch", "put"], 
                                "message_fr"    : ["musique"],
                                "input"         : ["@name_music", "@name_playlist", "suivante"],
                              },      
        "lecture"           : { 
                                "action"        : ["put"],
                                "message_fr"    : ["lecture"],
                              },
        "pause"             : { 
                                "action"        : ["put"],
                                "message_fr"    : ["pause"],
                              },
        "stop"               : { 
                                "action"        : ["stop"],
                                "message_fr"    : ["musique", "vidéo", "épisode", "film", "stop", "arrête"],
                              },     
        "baisser_son"       : { 
                                "action"        : ["put_down"],
                                "message_fr"    : ["le son", "le volume"],
                                "repete"        : ["encore", "plus"],
                              },
        "monter_son"       : { 
                                "action"        : ["turn_up"],
                                "message_fr"    : ["le son", "le volume"],
                                "repete"        : ["encore", "plus"],
                              },    
        "mute"              : { 
                                "action"        : ["cut", "stop"],
                                "message_fr"    : ["le son", "le volume"],
                              },
        "scan"              : { 
                                "action"        : ["put", "launch"],
                                "message_fr"    : ["scan"],
                              }
    }
    
    devices = []
    emplacements = []
    satelitesConnected = {}

    listeMotsSerie = []
    listeMotsNumero = []
    
    def __init__(self,devicesService = None):
        self.bus= Bus()
        self.kodiDao = KodiDAO()
        self.convert = Convert()
    #   self.playerMusic = playerMusic()
        self.tools = Tools()
        self.bus.subscribe('vocalOrdre', self.lanceVocalOrdre) 
        self.bus.subscribe('loadSeriesDao', self.loadSeriesCallBack) 
        self.bus.subscribe('loadSeriesEnCoursDao', self.loadSeriesEnCoursCallBack) 
        self.bus.subscribe('loadFilmsDao', self.loadFilmsCallBack) 
        self.bus.subscribe('loadMusiquesDao', self.loadMusiquesCallBack) 
        self.bus.subscribe('deviceService', self.deviceChange) 
        self.bus.subscribe('emplacementService', self.emplacementChange) 
        
        current_dir = os.path.dirname(__file__)
      #  jsonfile = '../../resources/fr/serieMapping.json'
      #  mappingfile = os.path.join(current_dir, jsonfile)
      #  with open(mappingfile) as data_file:    
      #      serieMapping = json.load(data_file)

      #  self.listeMotsSerie = self.mappingToWords(serieMapping)

        numeroMapping_path = '../../resources/fr/numeroMapping.json'
        numeroMapping_file = os.path.join(current_dir, numeroMapping_path)
        with open(numeroMapping_file) as data_file:    
            numeroMapping = json.load(data_file)                    

        self.listeMotsNumero = self.mappingToWords(numeroMapping)
                        
        for var in self.VARIABLES:
            v = self.VARIABLES[var]
            if v == "Int":
                self.VARIABLES[var] = numeroMapping
       #     if var == "@name_serie" :
       #         self.VARIABLES[var] = serieMapping
            
    def mappingToWords(self, mapping): 
        listOfWord = [] 
        for item in mapping :  
            l_m = mapping[item]
            for m in l_m :
                m_clean = self.tools.cleanString(m)
                l_w = m_clean.split(" ") 
                for w in l_w:
                    if w not in   listOfWord :
                        listOfWord.append(w)
        return listOfWord 

    def listToWords(self, list_): 
        listOfWord = [] 
        for item in list_ :  
            m_clean = self.tools.cleanString(item)
            l_w = m_clean.split(" ") 
            for w in l_w:
                if w not in   listOfWord :
                    listOfWord.append(w)
        return listOfWord 


    def synchronize(self, data):
        self.bus.publish('kodiService' , data)
    
    def lanceVocalOrdre(self, bus, key, obj):
        groupe = obj['groupe']
        if groupe != 'kodi' :
            return 
        
        ordre_name = obj['ordre']
        origineIp  = obj["origine"]
        #recognised = obj["recognised"]
        input_     = obj["input"]
        


        #ordre = self.ORDRES[ordre_name]
#        function = ordre["function"]

        try :
            getattr(self, ordre_name)(input_, origineIp)
        except Exception as e :
            print ("Kodi => lanceVocalOrdre : " + e.__str__())

    def findKodiBySecteur(self,origineIp):
        for secteur in self.emplacements:
            for device in secteur.devices:
                if str(device.ip) == origineIp :
                    self.secteurTouche = secteur
                    
        if hasattr(self, 'secteurTouche') :           
            for device in self.secteurTouche.devices:
                if device.hasKodi == True :
                    self.kodiDao.currentKodiIp = device.ip
            del self.secteurTouche   
                    

    def liste_film(self, input_, ipDestination):
        self.loadFilms()

    def liste_serie(self, input_, ipDestination):
        self.loadSeries()
    
    def liste_music(self, input_, ipDestination):
        self.loadMusiques()
    
    def lance_episode_2(self, input_, ipDestination):
        self.lance_episode( input_, ipDestination, True)
        
    def lance_episode(self, input_, ipDestination, suite = False):
        """
        1/ Liste des séries   : self.kodiDao.listSeriesEnCours
        2/ Input              : input_   
        """
        
        self.findKodiBySecteur(ipDestination)

        name_var = None
        episode_num = 0
        saison_num = 0
         
        
        for i in input_ :
            print(i)
            if "suivant" in i:
                suite = True
            if "@name_serie" in i :
                if len(input_[i]) > 1 :
                    name_var = input_[i][1]    
                if len(input_[i]) == 1 :
                    name_var = input_[i][0]
            if "@umeric" in i :
                if "épisode" in i :
                    if len(input_[i]) > 1 :
                        episode_num = input_[i][1]    
                    if len(input_[i]) == 1 :
                        episode_num = input_[i][0]
                if "saison" in i :        
                    if len(input_[i]) > 1 :
                        saison_num = input_[i][1]    
                    if len(input_[i]) == 1 :
                        saison_num = input_[i][0]
            if "premier" in i :
                saison_num = 1
                episode_num = 1
            if "dernier" in i :
                saison_num = "last"
                episode_num = "last"                 

        
        numeros =[]               
        if name_var :
            if suite :                 
                for serieEnCours in self.kodiDao.listSeriesEnCours :
                    if serieEnCours.serieTitle == name_var.key_ordre :
                        numeros.append(serieEnCours.nextEpisodeid)
            else :
                saison = 0
                episode = None
                serie = None
                if  name_var.key_ordre in self.kodiDao.listSeries :
                    serie = self.kodiDao.listSeries[name_var.key_ordre]
                if serie :
                    if saison_num == "last" :
                        saison = serie[-1]
                    elif saison_num > 0 :
                        saison = serie[saison_num]
                    else :
                        saison = serie[1]
                    
                    if saison > 0 :    
                        if episode_num == "last" :
                            episode = saison[-1]
                        elif episode_num > 0 :
                            episode = saison[episode_num]
                        else : 
                            episode = saison[1]
                    if episode :
                        numeros.append(episode.id)       
                    

        if len(numeros) > 0:     
            counter = collections.Counter(numeros)
            listePossible = counter.most_common()
            if len(listePossible) > 0 :
                episod_id, nombre = listePossible[0]
                if episod_id > -1 :
                    self.openSerie(episod_id) 
    

    def lance_film(self, input_, ipDestination):

        print(input_)
        self.findKodiBySecteur(ipDestination)

        name_var = None
        
        for i in input_ :
            print(i)
            if "@name_film" in i :
                if len(input_[i]) > 1 :
                    name_var = input_[i][1]    
                if len(input_[i]) == 1 :
                    name_var = input_[i][0]

        numeros =[]               
        if name_var :
            for film in self.kodiDao.listFilms :
                if film.title == name_var.key_ordre :
                    numeros.append(film.id)

        if len(numeros) > 0:     
            counter = collections.Counter(numeros)
            listePossible = counter.most_common()
            if len(listePossible) > 0 :
                movieid, nombre = listePossible[0]
                if movieid > -1 :
                    self.openFilm(movieid) 
                    
        #movieid = -1
        #movieid = self.convert.convert(arguments[0])
#        numeros = self.convert.convertListChaine(input_, self.kodiDao.listFilms)
        #      print 'lance_film : ' + str(movieid)
 #       print ('numeros : ' + str(numeros))
#        counter = collections.Counter(numeros)
#        print ('numeros : ' + str(counter.most_common(4)))
 #       listePossible = counter.most_common(4)
 #       movieid, nombre = listePossible[0]
        

    #def lance_episode(self, input_, ipDestination):
        #episod_id = -1
    #    print(input_)
    #    numeros = self.convert.convertListChaine(input_, self.kodiDao.listSeries, self.kodiDao.listSeriesEnCours)
#            print 'lance_episode : ' + str(episod_id)
    #    print ('numeros : ' + str(numeros))
    #    counter = collections.Counter(numeros)
    #    print ('numeros : ' + str(counter.most_common(4)))
    #    listePossible = counter.most_common(4)
    #    episod_id, nombre = listePossible[0]
    #    if episod_id > -1 :
    #        self.openSerie(episod_id) 
    
    #def launchMusic(self, input_, ipDestination):
    #    self.playerMusic.manageMusic(ipDestination, "lance_music" , "bureau")
    
    def pause(self, input_, ipDestination):
        #pass
        self.playPause(False)
        #self.playerMusic.manageMusic(ipDestination, "pause")
    
    def lecture(self, input_, ipDestination):
        #pass
        self.playPause(True)
        #self.playerMusic.manageMusic(ipDestination, "lecture")
    
    def stop(self, input_, ipDestination):
        #pass
        self.stopFilm()
        #self.playerMusic.manageMusic(ipDestination, "stop")

    def launchMute(self, input_, ipDestination):
        self.xbmc.Application.SetMute({"mute":True})   

    def baisser_son(self, input_, ipDestination):
        self.xbmc = self.kodiDao.connectFirstKodi()
        volume = self.xbmc.Application.GetProperties({"properties" : ["volume"]})    
        n_v = volume["result"]["volume"] - 2
        volume = self.xbmc.Application.SetVolume({"volume":n_v} )    


    def scan(self, input_, ipDestination):
        self.scanMoviesDatabase()
        
    def deviceChange(self, bus, key, obj):
        self.devices = obj["devices"]
        self.detectKodi()
        if len(self.kodiDao.listKodis) > 0 and not hasattr(self, 'WSthread'):
            self.WSthread = []
            for kodi in self.kodiDao.listKodis :
                t = WSThread(self, kodi.ip)
                self.WSthread.append(t)
                t.start()
            self.loadMusiques()
            self.loadFilms()
            self.loadSeries()
    
    def emplacementChange(self, bus, key, obj):
        if hash(frozenset(self.emplacements)) != hash(frozenset(obj["emplacements"])):
            self.emplacements = obj["emplacements"]
            emplacement_name = []
            emplacement_mapping = {}
            for e in self.emplacements :
                name_clean = self.tools.cleanString(e.name)    
                emplacement_name.append(name_clean) 
                if e.name not in emplacement_mapping :
                    emplacement_mapping[e.name] = []
                if name_clean not in emplacement_mapping[e.name] :
                    emplacement_mapping[e.name].append(name_clean)
                
            self.VARIABLES["@name_playlist"] = emplacement_mapping   
            self.bus.publish('loadVocalVariable' , {'module': 'kodi', 'key':'@name_playlist' , 'values' : emplacement_name})
               
        
    def detectKodi(self, args = None):
        listKodis = []
        if len(self.devices) > 0 :
            for device in self.devices:
                if self.deviceDetectKodi(device.ip):
                    device.setHasKodi(True)
                    listKodis.append(device)
                    print ('Kodi detect  : ' + device.ip)
            obj = {'key':"kodiDetected"   , 'devices': listKodis}
            self.synchronize(obj)
            
            self.kodiDao.listKodis = listKodis
        return self.kodiDao.listKodis
    
    def deviceDetectKodi(self, ip):   
        params = {}
        params['jsonrpc'] = '2.0'
        params['id'] = 0
        params['method'] = 'JSONRPC.Ping'
        params['params'] = ''
        data = json.dumps(params).encode('utf-8')
        header = {'Content-Type': 'application/json', 'User-Agent': 'python-xbmc'}
        url = "http://" + ip + ":" + str(conf.PORT_HTTP_KODI) +"/jsonrpc"
        isKodi = True
        try:
            req = urllib2.Request(url, data, header)
            urllib2.urlopen(req, timeout = 0.3)
            # xbmc = xbmcjson.XBMC(url)
            # xbmc.JSONRPC.Ping()
        except:
            isKodi = False
        return isKodi
    
    def scanMoviesDatabase(self, args = None):
        self.xbmc = self.kodiDao.connectFirstKodi()
        self.xbmc.VideoLibrary.Scan()
        
    def scanMusiquesDatabase(self, args = None):
        self.xbmc = self.kodiDao.connectFirstKodi()
        self.xbmc.AudioLibrary.Scan()
            
    def showNotification(self, args):
        self.xbmc = self.kodiDao.connectFirstKodi()
        self.xbmc.GUI.ShowNotification({"title":"Topi de amor", "message":"Bonjour je m'appelle Noni y te quiero"})
    
    def loadFilms(self, forcage = False ):
        if len(self.kodiDao.listFilms) == 0 or forcage: 
            self.kodiDao.loadFilms()
        obj = {'key':"loadFilms"   , 'films' : self.kodiDao.listFilms}
        self.synchronize(obj)
        return self.kodiDao.listFilms

    def loadFilmsCallBack(self, bus, key, films):
        obj = {'key':"loadFilms"   , 'films' : films}
        self.synchronize(obj)
        films_name = []
        for f in films:
            films_name.append(f.title)
        self.bus.publish('loadVocalVariable' , {'module': 'kodi', 'key':'@name_film' , 'values' : films_name})

    def loadMusiques(self, forcage = False ):
        self.kodiDao.loadMusiques()
        obj = {'key':"loadMusiques", 'musiques' : self.kodiDao.listMusiques}
        self.synchronize(obj)
        return self.kodiDao.listMusiques

    def loadMusiquesCallBack(self, bus, key, musiques):
        obj = {'key':"loadMusiques", 'musiques' : self.kodiDao.listMusiques}
        self.synchronize(obj)
        listArtiste = ["pink floyd"]
        self.bus.publish('loadVocalVariable' , {'module': 'kodi', 'key':'@name_music' , 'values' : listArtiste})

    def loadSeries(self, forcage = False):
        if len(self.kodiDao.listSeries) == 0 or forcage: 
            self.kodiDao.loadSeries()
        self.synchronize({'key':"loadSeries", 'series' : self.kodiDao.listSeries})
        self.synchronize({'key':"loadSeriesEnCours"   , 'series' : self.kodiDao.listSeriesEnCours})
        return self.kodiDao.listSeries   
    
    def loadSeriesTab(self, forcage = False):
        if len(self.kodiDao.listSeries) == 0 or forcage: 
            self.kodiDao.loadSeries()
        listSeriesTab = []
        for serie in self.kodiDao.listSeries:
            listSeriesTab.append(Serie(serie))
        return listSeriesTab

    def loadSeriesCallBack(self, bus, key, series):
        self.kodiDao.listSeries = series
        self.synchronize({'key':"loadSeries"   , 'series' : series})
        
        #serieMapping = self.VARIABLES["@name_serie"]
        #for s in self.kodiDao.listSeries:
        #    s_clean = self.tools.cleanString(s)    
        #    if s not in serieMapping :
        #        serieMapping[s] = []
        #    if s_clean not in serieMapping[s] :   
        #        serieMapping[s].append(s_clean)
                    
        ##self.listeMotsSerie = self.mappingToWords(serieMapping)
        #self.VARIABLES["@name_serie"] = serieMapping
        
        #vocal_serie = []
        #for item in serieMapping :
        #    l = serieMapping[item]
        #    for m in l :
        #        if m not in vocal_serie :
        #            vocal_serie.append(m)
                    
        #self.bus.publish('loadVocalVariable' , {'module': 'kodi', 'key':'@name_serie' , 'values' : vocal_serie})
        
    def loadSeriesEnCoursCallBack(self, bus, key, seriesEnCours):
        self.kodiDao.listSeriesEnCours = seriesEnCours
        self.synchronize({'key':"loadSeriesEnCours"   , 'series' : self.kodiDao.listSeriesEnCours})

    def kodiCommand(self, kodiArgs):

        command = kodiArgs[0].ordre
        if hasattr(kodiArgs[0], 'arguments'):
            args = kodiArgs[0].arguments

        self.xbmc = self.kodiDao.connectFirstKodi()

        player = {}

        activePlayer = self.xbmc.Player.GetActivePlayers()
        print ('Active player : ' + str(activePlayer))  
        if command == 'PlayPause' :
            player = self.playPause(args)

        if command == 'openFilm' :
            player = self.openFilm(args)
            
        if command == 'openSerie' :
            player = self.openSerie(args)
            
        if command == 'Stop' :
            player = self.stopFilm()

        if command == 'activeItem' :
            try:
                player = self.activeItem()
            except :
                pass   
        return player

    def openFilm(self, args):
        self.xbmc = self.kodiDao.connectFirstKodi()
        self.xbmc.Player.Open({"item": {"movieid" : int(args)}})
    
    def openSerie(self, episod_id):
        self.xbmc= self.kodiDao.connectFirstKodi()
        #   print episod_id
        result = self.xbmc.Player.Open({"item": {"episodeid" : int(episod_id)}, "options" : {"resume": True}})
        print (result)
        
    def playPause(self, args):
        self.xbmc = self.kodiDao.connectFirstKodi()
        return self.xbmc.Player.PlayPause([PLAYER_VIDEO])
    
    def stopFilm(self):
        self.xbmc = self.kodiDao.connectFirstKodi()
        return self.xbmc.Player.Stop([PLAYER_VIDEO])

    def activeItem(self):
        self.kodiDao.connectFirstKodi()
        activeItem = {}
        activeKodi = self.xbmc.Player.GetItem([PLAYER_VIDEO])   
        if not activeKodi:
            return
        listActiveItem = activeKodi.get('result', {}).get('item', [])
#        print str(listActiveItem)        
        if len(listActiveItem) > 0 :
            type = listActiveItem['type']
            
        if  type != 'unknown':
            title = listActiveItem['label']
            id = listActiveItem['id']
            speedJson = self.xbmc.Player.GetProperties({"properties": ["speed"], "playerid": PLAYER_VIDEO})    
            speed = speedJson.get('result', {}).get('speed') 
            print ('onPlay' if speed > 0 else 'onPause')
            if type == 'movie' :
                activeItem = self.kodiDao.loadFilmDetails(id)
            else :     
                activeItem = self.kodiDao.loadEpisodeDetails(id)
            print (title)
            obj = {'key':"activeItem" , 'items' : {'item' : activeItem, 'speed' : speed}}
            self.synchronize(obj)
        else :
            print ("nada en curso")

        return activeItem    
    
            
    def test(self):
#        self.xbmc.GUI.ActivateWindow({"window":"mediasource"})
        
        sources = self.xbmc.Files.GetSources(media="video")
        print (sources)
        directoryFilms = self.xbmc.Files.GetDirectory({"directory":'/media/HP Desktop Drive/Film/', "sort": {"order":"ascending", "method":"label"}})
        filmsTitle = []
        for film in directoryFilms.get('result', {}).get('files', []):
            item = film['label']
            if item not in filmsTitle :
                filmsTitle.append(item) 

        print (filmsTitle) 
        
        directorySeries = self.xbmc.Files.GetDirectory({"directory":'/media/Seagate Expansion Dr/série/', "sort": {"order":"ascending", "method":"label"}})
        seriesTitle = []
        for serie in directorySeries.get('result', {}).get('files', []):
            item = serie['label']
            if item not in seriesTitle :
                seriesTitle.append(item) 
        print (seriesTitle)
        print (len(seriesTitle))



    def test1(self):
        xbmc = XBMC("http://192.168.1.100:8080/jsonrpc")
        audio = xbmc.AudioLibrary.GetSongs()
        print (audio)

class WSThread(threading.Thread):
        
    def __init__(self, parent, ip):
        super(WSThread, self).__init__()
        host = "ws://" + ip + ":" + str(conf.PORT_WS_KODI) + "/jsonrpc/"
        self.parent = parent
        self.ws = websocket.WebSocketApp(host,
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close)

    def run(self):
        self.ws.run_forever()

    def on_message(self, ws, message):
        response = json.load(StringIO(message.decode('utf-8')))
        print(str(response))
#        {u'params': {u'data': {u'shuttingdown': False}, u'sender': u'xbmc'}, u'jsonrpc': u'2.0', u'method': u'GUI.OnScreensaverDeactivated'}
#        {u'params': {u'data': None, u'sender': u'xbmc'}, u'jsonrpc': u'2.0', u'method': u'System.OnRestart'}
#        {u'params': {u'data': {u'exitcode': 66}, u'sender': u'xbmc'}, u'jsonrpc': u'2.0', u'method': u'System.OnQuit'}
#        {"jsonrpc":"2.0","method":"Player.OnPlay","params":{"data":{"item":{"id":2,"type":"movie"},"player":{"playerid":1,"speed":1}},"sender":"xbmc"}}
#        {"jsonrpc":"2.0","method":"Player.OnStop","params":{"data":{"end":false,"item":{"id":2,"type":"movie"}},"sender":"xbmc"}}
#        {"jsonrpc":"2.0","method":"VideoLibrary.OnScanFinished","params":{"data":null,"sender":"xbmc"}}
#        {"jsonrpc":"2.0","method":"VideoLibrary.OnUpdate","params":{"data":{"item":{"id":2557,"type":"episode"},"transaction":true},"sender":"xbmc"}}

        method = response['method']
        param = response.get('param', {})
#        sender = message['sender']

        scanEnCours = False
        if method == 'VideoLibrary.OnScanStarted' :
            scanEnCours = True

        if method == 'VideoLibrary.OnScanFinished' :
            self.parent.loadFilms(True)
            self.parent.loadSeries(True)
            scanEnCours = False 

        if method == 'Player.OnPlay' :
            item = param.get('data', {}).get('item', {})
            if hasattr(item, 'id') :
                id = item['id']
            type = item['type']
            if type == 'movie' :
                activeItem = Film('title', id )
            else :     
                activeItem = Episode('', 'title', id, 0, '', 0)
            obj = {'key':"activeItem" , 'items' : {'item' : activeItem, 'speed' : 1}}
            self.parent.synchronize(obj)

        if method == 'Player.OnPause' :
            item = param.get('data', {}).get('item', {})
            if hasattr(item, 'id') :
                id = item['id']
            type = item['type']
            if type == 'movie' :
                activeItem = Film('title', id )
            else :     
                activeItem = Episode('', 'title', id, 0, '', 0)
            obj = {'key':"activeItem" , 'items' : {'item' : activeItem, 'speed' : 1}}
            self.parent.synchronize(obj)


        if method == 'Player.OnStop' :
            item = param.get('data', {}).get('item', {})
            if hasattr(item, 'id') :
                id = item['id']
            type = item['type']
        
        if method == 'VideoLibrary.OnUpdate' :
            if scanEnCours == False :
                item = param.get('data', {}).get('item', {})
                self.parent.loadSeries(True)
                self.parent.loadFilms(True)

    
    def on_error(self, ws, error):
        print(error)
    
    def on_close(self, ws):
        print("KODI : ### closed ###")

if __name__ == "__main__":
    kodi = Kodi()   
    kodi.test1()