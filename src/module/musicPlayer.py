#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Created on 16/09/2017

@author: Arnaud
'''

from __future__ import print_function
from __future__ import unicode_literals

from Bus import Bus
import threading, os 
import conf
from operator import attrgetter
import xbmcjson, urllib2, shutil

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init(None)


class Module():
          
    def getIstance(self):
        print ("Chargement du module music player.....")
        return "musicplayer", MusicPlayer()
    
class MusicPlayer():

    VARIABLES = {}

    ORDRES = {   
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
                              }}
    
    list_players = {}
    counter = 0
    
    def __init__(self):
        self.bus= Bus()
        
        self.bus.subscribe('vocalOrdre', self.lanceVocalOrdre) 
        # Liste des musiques venant de Kodi
        self.bus.subscribe('loadMusiquesDao', self.loadMusiques) 

        current_dir = os.path.dirname(__file__)
        script = '../tmp'
        directory_tmp = os.path.join(current_dir, script)
        if not os.path.exists(directory_tmp):
            os.makedirs(directory_tmp)
        script = '../tmp/music'
        directory_tmp = os.path.join(current_dir, script)
        if not os.path.exists(directory_tmp):
            os.makedirs(directory_tmp)

    def lanceVocalOrdre(self, bus, key, obj):
        groupe = obj['groupe']
        if groupe != 'musicplayer' :
            return 
        
        ordre_name = obj['ordre']
        origineIp  = obj["origine"]
        input_     = obj["input"]

        try :
            getattr(self, ordre_name)(input_, origineIp)
        except Exception as e :
            print ("musicplayer => lanceVocalOrdre : " + e.__str__())


    def launchMusic(self, input_, ipDestination):
        self.manageMusic(ipDestination, "lance_music" , "bureau")
        
    def startMusic(self, args):
        self.manageMusic('192.168.1.108', "lance_music" , args[0])
        
    def stopMusic(self, args):
        self.manageMusic('192.168.1.108', "stop")
        
    def pause(self, input_, ipDestination):
        self.manageMusic(ipDestination, "pause")
    
    def lecture(self, input_, ipDestination):
        self.manageMusic(ipDestination, "lecture")
    
    def stop(self, input_, ipDestination):
        self.manageMusic(ipDestination, "stop")

    def launchMute(self, input_, ipDestination):
        pass   

    def baisser_son(self, input_, ipDestination):
        pass


    def loadMusiques(self, bus, key, obj):
        # Chargement en liste de toutes les musiques 
        listMusiqueKodi = []
        for artist in obj :
            for album in obj[artist]:
                for music in obj[artist][album]:
                    listMusiqueKodi.append(obj[artist][album][music])
        self.listMusicKodi = listMusiqueKodi       


    def manageMusic(self, ipDestination, ordre, play_list="bureau"):
        
        print ("IP musique  => " + str(ipDestination)) 
                
        player = None
        
        if ipDestination not in self.list_players: 
            listMusicToPlay = self.getMusicOfPlaylist(play_list) 
            nameThread = "music_tmp" + str(self.counter)
            self.counter += 1 
            self.list_players[ipDestination]  = player = PlayerMp3_seeking(ipDestination, nameThread, listMusicToPlay)
            player.setDaemon(True)
            player.start()
        else :
            player =  self.list_players[ipDestination]   
        
        if ordre == 'lance_musique' :
            player.on_play()

        if ordre == 'stop' :
            player.on_stop()
            del self.list_players[ipDestination]
    
        if ordre == 'next' :
            player.on_next()

        if ordre == 'previous' :
            player.on_foward()

        if ordre == 'pause' :
            player.on_pause()
            
        if ordre == 'lecture' :
            player.on_play()


    def getMusicOfPlaylist(self, playlistName):        
        current_dir = os.path.dirname(__file__)
        script = '../../resources/playlist_' + playlistName
        playlistFile = os.path.join(current_dir, script)
        f = open(playlistFile, 'r')
        list_song = []
        for line in f:
            if '\n' in line:
                line = line[:-1]
            list_song.append(str(line))
            
        # Match de ce qui vient de la playlist avec music kodi
        listMusicPlayList = []
        for music in self.listMusicKodi :
            list_ =  [ext in music.file for ext in list_song]
            if any(list_) :    
                index = list_.index(True)
                music.setOrdre(index)
                listMusicPlayList.append(music)     
        listMusicPlayList.sort(key=attrgetter('ordre'))    
        
        return listMusicPlayList  

    def coupeSon(self):
        for player in self.list_players :
            self.list_players[player].on_pause()       

    def repriseSon(self):
        for player in self.list_players :
            self.list_players[player].on_play()       

class EndException(Exception):
    pass

class PlayerMp3_seeking(threading.Thread):
    
    counter = 0
    ip = "127.0.0.1"
    musicLocationToPlay = []
    
    def __init__(self, ip, threadName, listMusic):
        GObject.threads_init()
        Gst.init(None)
        threading.Thread.__init__(self)
        
        self.ip = ip
        self.threadName = threadName
        
        current_dir = os.path.dirname(__file__)
        script = '../tmp/music/' + threadName +'/'
        directory_tmp = os.path.join(current_dir, script)
        if not os.path.exists(directory_tmp):
            os.makedirs(directory_tmp)

        for music in listMusic :
            self.downloadMusicFromKodi(music)    
            print (str(sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))))
        
        self.pipeline = Gst.Pipeline.new('pipeline')
        self.src = Gst.ElementFactory.make("filesrc")
        self.src.set_property("location", self.musicLocationToPlay[0])
        
        self.decodebin = Gst.ElementFactory.make("decodebin")
        self.audioconvert = Gst.ElementFactory.make("audioconvert")
        self.rtpL16pay = Gst.ElementFactory.make("rtpL16pay")
                
        self.client = Gst.ElementFactory.make("udpsink")
        self.client.set_property("host", self.ip)
        self.client.set_property("port", conf.PORT_STREAM_MUSIC)
        
        self.pipeline.add(self.src)
        self.pipeline.add(self.decodebin)
        self.pipeline.add(self.audioconvert)
        self.pipeline.add(self.rtpL16pay)
        self.pipeline.add(self.client)
              
        self.src.link(self.decodebin)
        self.decodebin.link(self.audioconvert)
        self.audioconvert.link(self.rtpL16pay)
        self.rtpL16pay.link(self.client)

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
 
        self.bus.connect('message', self.on_message)

        self.is_playing = True
        self.pipeline.set_state(Gst.State.PLAYING)
        
    def run(self):    
        #constructing the window and setting up its size, and the destroy signal
        self.loop = GObject.MainLoop()
        self.loop.run() 
        
    
    def mp3_to_play(self, sens = "NEXT"):
        list_size = len(self.musicLocationToPlay) -1 
        if sens == "NEXT" :
            self.counter = self.counter + 1
        else :
            self.counter = self.counter - 1
        
        if self.counter > list_size or self.counter < 0 :
            self.counter = 0

        return self.musicLocationToPlay[self.counter]
    
    def downloadMusicFromKodi(self, music):
        #Téléchargement de la        
        #host = "http://"+ music.ip.ip +":8080/"
        host = "http://192.168.1.100:8080/"
        xbmc = xbmcjson.XBMC(host + "jsonrpc")
        musicPath = xbmc.Files.PrepareDownload(path=music.file)
        print (str(musicPath.get('result', {})))
        vfs = musicPath.get('result', {}).get('details', {}).get('path', {})
        
        pathMusic = music.file.split('/')
        title = pathMusic 
        if len(pathMusic) > 0:
            indexEnd =  len(pathMusic) - 1
            title = pathMusic[indexEnd]

        current_dir = os.path.dirname(__file__)
        script = '../tmp/music/' + self.threadName +'/' 
        directory_tmp = os.path.join(current_dir, script)
        
        if not os.path.isfile(directory_tmp + title): 
            url = os.path.join(host, vfs)
            mp3file = urllib2.urlopen(url)
    
            file_name = open( directory_tmp + title , 'wb')
            file_name.write(mp3file.read())
            file_name.close()

        self.musicLocationToPlay.append(directory_tmp + title )
    
    def on_message(self, bus, message):
        t = message.type
#        print str(message.type)
        if t == Gst.MessageType.EOS:
            self.on_next()
        elif t == Gst.MessageType.ERROR:
            self.on_next()
        
    def on_play(self):
        self.is_playing = True
        self.pipeline.set_state(Gst.State.PLAYING)
      
    def on_pause(self): 
        self.is_playing = False
        self.pipeline.set_state(Gst.State.PAUSED)

    def on_stop(self): 
        self.is_playing = False
        self.pipeline.set_state(Gst.State.NULL)
        current_dir = os.path.dirname(__file__)
        script = '../tmp/music/' + self.threadName +'/'
        directory_tmp = os.path.join(current_dir, script)
        shutil.rmtree(directory_tmp)
        self.loop.quit()
        #raise EndException("An error in thread '{}'.".format(self.threadName))
        
    def on_next(self): 
        self.pipeline.set_state(Gst.State.NULL)
        self.src.set_property("location", self.mp3_to_play())
        self.pipeline.set_state(Gst.State.PLAYING)

    def on_foward(self): 
        self.pipeline.set_state(Gst.State.NULL)
        self.src.set_property("location", self.mp3_to_play("ARR"))
        self.pipeline.set_state(Gst.State.PLAYING)
    
if __name__ == "__main__":
    player = MusicPlayer()
    player.manageMusic("192.168.1.108", "lance_music", "bureau")

