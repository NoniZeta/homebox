#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Created on 23/07/2015

@author: Arnaud
'''

from datetime import datetime, timedelta

from Bus import Bus
from xbmcjson import XBMC
import threading, os, conf
import logging

class KodiDAO():
    listKodis = []
    listFilms = []
    listSeries = []
    listSeriesEnCours = []
    listMusiques = []
    ListWordsToRecognize = []
    ListTitlesToRecognize = []
    
    def __init__(self):
        self.bus= Bus()
        self.ft = LoadFilms(self)
        self.fs = LoadSeries(self)
        self.fm = LoadMusiques(self)
        
    def connectFirstKodi(self):
        if not hasattr(self, 'currentKodiIp') and len(self.listKodis) > 0 :
            self.currentKodiIp = self.listKodis[0].ip
        
        result = None    
        if hasattr(self, 'currentKodiIp') :
            result = self.connectKodi(self.currentKodiIp)    
        return  result
    
    def connectKodi(self, kodiIp):
        return XBMC("http://" + kodiIp + ":" + str(conf.PORT_HTTP_KODI) + "/jsonrpc")  
        
    def loadFilms(self):
        if not self.ft.isAlive():
            self.xbmc = self.connectFirstKodi()
            self.ft = LoadFilms(self)
            self.ft.start()
        return self.listFilms
    
    def loadFilmsCallback(self):
        self.bus.publish('loadFilmsDao', self.listFilms)

    def loadSeries(self):
        if not self.fs.isAlive():
            self.xbmc = self.connectFirstKodi()
            self.fs = LoadSeries(self)
            self.fs.start()
        return self.listSeries
    
    def loadSeriesCallback(self):
        self.bus.publish('loadSeriesDao', self.listSeries)
        self.bus.publish('loadSeriesEnCoursDao', self.listSeriesEnCours)
    
    def loadSeriesEnCours(self):
        if not self.fs.isAlive():
            self.xbmc = self.connectFirstKodi()
            self.fs = LoadSeries(self)
            self.fs.start()
        return self.listSeriesEnCours

    def loadMusiques(self):
        if not self.fm.isAlive():
            self.fm = LoadMusiques(self)
            self.fm.start()
        return self.listMusiques
    
    def loadMusiquesCallback(self):
        self.bus.publish('loadMusiquesDao', self.listMusiques)

    def loadEpisodeDetails(self, episodeid):
        if len(self.listSeries) > 0 :
            return 
         
        episode = None
        properties = ["title", "plot", "votes", "rating", "writer", "firstaired", "playcount", "runtime", 
                      "director", "productioncode", "season", "episode", "originaltitle", "showtitle", "cast", 
                      "streamdetails", "lastplayed", "fanart", "thumbnail", "file", "resume", "tvshowid", 
                      "dateadded", "uniqueid", "art"]

        for item in self.listSeries:
            if episodeid == item.id :
                episode = item
                detailsJson = self.xbmc.VideoLibrary.GetEpisodeDetails(episodeid=episodeid, properties=properties)
                details = detailsJson.get('result', {}).get('episodedetails', {})
                episode['art'] = details.get('art', {})
#                logger.debug(details)   
         
        return episode       
    
    
    def loadFilmDetails(self, movieid):
        if len(self.loadFilms()) > 0 :
            return 
        ### Media properties ###
        movie_properties = ['title', 'genre', 'year', 'rating', 'director', 'trailer', 'tagline', 'plot',  
                            'plotoutline', 'originaltitle', 'lastplayed', 'playcount', 'writer', 'studio', 
                            'mpaa', 'cast', 'country', 'imdbnumber', 'runtime', 'set', 'showlink', 'streamdetails',
                            'top250', 'votes', 'fanart', 'thumbnail', 'file', 'sorttitle' , 'resume', 'setid', 
                            'dateadded', 'tag', 'art' ]
        film = None
        for item in self.listFilms:
            if movieid == item.id :
                film = item
                detailsJson = self.xbmc.VideoLibrary.GetMovieDetails(movieid=movieid, properties=movie_properties)
                details = detailsJson.get('result', {}).get('moviedetails', {})
                film['art'] = details.get('art', {})
        return film


class LoadFilms(threading.Thread) :
    
    def __init__(self, parent):
        super(LoadFilms, self).__init__()
        self.parent = parent
    
    def run(self):
        listFilms = []
    
        if not self.parent.xbmc:
            return
        films = self.parent.xbmc.VideoLibrary.GetMovies()
        if films : 
            for film in films.get('result', {}).get('movies', []):
                item = Film(film['label'], film['movieid'])
                listFilms.append(item)      
        
        self.parent.listFilms = listFilms
        print "Films loaded : %s films", len(self.parent.listFilms)   
        self.parent.loadFilmsCallback()
            
class LoadSeries(threading.Thread) :
    
    def __init__(self, parent):
        super(LoadSeries, self).__init__()
        self.parent = parent
    
    def run(self):
        if not self.parent.xbmc:
            return
        
        properties = ["title", "season", "episode", "originaltitle", "showtitle", "lastplayed", "file", "dateadded", "playcount", "resume"]
        series = self.parent.xbmc.VideoLibrary.GetEpisodes({"properties": properties, "sort": {"order":"ascending", "method":"tvshowtitle"} })
        if not series :
            return
        
        listSeries = {}       
        for serie in series.get('result', {}).get('episodes', []):
            serieTitle = serie['showtitle']
            string_date = serie['lastplayed']
            title = serie['title']
            saison = serie['season']
            numEpisode = serie['episode']
            playcount = serie['playcount']
            episodeid = serie['episodeid']
            resume = serie['resume']
            position = resume["position"]
            total = resume["total"]
            if position > 0 or total > 0 :
                print str(serieTitle.encode("utf-8")) +" saison "+str(saison)+" episode "+ str(numEpisode)+" en cours : "+ str(position) +"/"+str(total)
            episode = Episode(serieTitle, title, episodeid, numEpisode, saison, playcount)
            lastPlayed = ''
            if string_date != '':
                lastPlayed = datetime.strptime(string_date, "%Y-%m-%d %H:%M:%S").isoformat()
            episode.setLastPlayed(lastPlayed)
            if serieTitle not in listSeries.keys() :
                listSeries[serieTitle] = {} 
            if saison not in listSeries[serieTitle].keys() :
                listSeries[serieTitle][saison] = {} 
            listSeries[serieTitle][saison][numEpisode] = episode    
        
        listSeriesEnCours = []
        for serie in listSeries.keys():
            current = (datetime.now() - timedelta(days=100)).isoformat()
            lastEpisodePlayed = None
            for saison in listSeries[serie].keys():
                lastEpisode = max(listSeries[serie][saison].keys())
                for numEpisode in listSeries[serie][saison].keys():
                    episode = listSeries[serie][saison][numEpisode]
                    nextNum = episode.episode + 1 
                    if nextNum in listSeries[serie][saison].keys(): 
                        nextEp = listSeries[serie][saison][nextNum]
                        episode.setNextEpisodeid(nextEp.id)
                    else :
                        if lastEpisode == episode.episode:
                            nextSaison = saison + 1 
                            if nextSaison in listSeries[serie].keys() and 1 in listSeries[serie][nextSaison].keys():
                                    nextEp = listSeries[serie][saison+1][1]
                                    episode.setNextEpisodeid(nextEp.id)
                            else :
                                episode.setNextEpisodeid(-9)       
                        else :
                            episode.setNextEpisodeid(-1)
                 
                    if  episode.lastPlayed != '' and episode.playcount > 0 and episode.lastPlayed  > current:
                        current = episode.lastPlayed       
                        lastEpisodePlayed = episode

                        
            if lastEpisodePlayed != None  and lastEpisodePlayed.nextEpisodeid > -1 :
                listSeriesEnCours.append(lastEpisodePlayed)
    
        self.parent.listSeries = listSeries
        self.parent.listSeriesEnCours = listSeriesEnCours
        print "Serie loaded : %s series", len(self.parent.listSeries) 
        print "Serie en cours loaded : %s series", len(self.parent.listSeriesEnCours) 

        self.parent.loadSeriesCallback()        

class LoadMusiques(threading.Thread) :
    
    def __init__(self, parent):
        super(LoadMusiques, self).__init__()
        self.parent = parent
    
    def run(self):
        
        listMusiques = {}

        #properties = ["title", "artist", "albumartist", "genre", "year", "rating", "album", "track", "duration", "comment", "lyrics", "musicbrainztrackid", "musicbrainzartistid", "musicbrainzalbumid", "musicbrainzalbumartistid", "playcount", "fanart", "thumbnail", "file", "albumid", "lastplayed", "disc", "genreid", "artistid", "displayartist", "albumartistid" ]
        properties = ["title", "artist", "album", "file" ]

        #for kodi in self.parent.listKodis :
        xbmc = self.parent.connectKodi("192.168.1.100")
        musiques = xbmc.AudioLibrary.GetSongs({"properties":properties})
        if len(musiques.get('result', {}).get('songs', {})) > 0 : 
            listM = musiques.get('result', {}).get('songs', {})
            for m in listM :
                music = Musique()
                music.setAlbum(str(m.get('album', {}).encode('utf8')).strip())
                artists = m.get('artist', [])
                if len(artists) > 0 :
                    #TODO : On ne prend que le premier artiste de la liste !!!
                    artist = str(artists[0].encode('utf8')).strip() if str(artists[0].encode('utf8')).strip() != "" else "Inconnu"
                    music.setArtist(artist)
                else :    
                    music.setArtist("Inconnu")
                music.setTitle(str(m.get('title', {}).encode('utf8')).strip())
                music.setFile(str(m.get('file', {}).encode('utf8')).strip())
                music.setIp("192.168.1.100")
                                    
                if music.artist not in listMusiques.keys() :
                    listMusiques[music.artist] = {} 
                if music.album not in listMusiques[music.artist].keys() :
                    listMusiques[music.artist][music.album] = {} 
                listMusiques[music.artist][music.album][music.title] = music   
                    
        self.parent.listMusiques = listMusiques        
        print "Musics loaded : %s songs", len(listMusiques)   
        self.parent.loadMusiquesCallback()
        #TODO


class Musique():
        
    def __init__(self):
        self.ip = ''
        self.file = ''
        self.artist = ''
        self.album = ''
        self.title = ''
        self.ordre = 0

    def setIp(self, ip):
        self.ip = ip
    
    def setArtist(self, artist):
        self.artist= artist    

    def setAlbum(self, album):
        self.album= album    

    def setTitle(self, title):
        self.title= title    
                
    def setFile(self, file):
        self.file= file    
    
    def setOrdre(self, ordre):
        self.ordre = ordre    

    def getPath(self):
        host = "http://" + self.ip + ":" + str(conf.PORT_HTTP_KODI) + "/" 
        return os.path.join(host, self.file)


class Film():
        
    def __init__(self, title, movieid):
        self.title = title
        self.id = movieid

class Serie():
        
    def __init__(self, title):
        self.title = title


class Episode():
        
    def __init__(self, serieTitle, title, episodeid, episode, saison, playcount):
        self.serieTitle = serieTitle
        self.title = title
        self.id = episodeid
        self.episode = episode
        self.saison = saison
        self.playcount = playcount
        
    def setLastPlayed(self,lastPlayed):
        self.lastPlayed = lastPlayed
        
    def setNextEpisodeid(self,nextEpisodeid):
        self.nextEpisodeid = nextEpisodeid

    def setDetails(self,details):
        self.details= details

