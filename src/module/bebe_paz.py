#!/usr/bin/env python2
# -*- coding: utf-8 -*-
'''
Created on 18/06/2017

@author: Arnaud
'''

from __future__ import print_function
from __future__ import unicode_literals

from Bus import Bus
import threading, time
from Queue import Queue

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

GObject.threads_init()
Gst.init(None)


class Module():
          
    def getIstance(self):
        print ("Chargement du module Bebe Paz.....")
        return "bebepaz", BebePaz()
    
class BebePaz():

    VARIABLES = {}

    ORDRES = {
            "display_bebepaz"   : { 
                                    "action"        : ["display", "show"],
                                    "message_fr"    : ["bébé"]
                                  }
              }
    
    def __init__(self):
        self.bus= Bus()
        
        self.isActive = True
        self.bus.subscribe('vocalOrdre', self.lanceVocalOrdre) 

        global queues
        queues = []
        gst_thread = MainPipeline()
        gst_thread.start()
        
    def stream(self):
        q = Queue(10)
        queues.append(q)
        while True:
            try:
                #print q.qsize()
                yield q.get(timeout=1)
            except Exception as e:
                if q in queues:
                    queues.remove(q)
                return

    def lanceVocalOrdre(self, bus, key, obj):
        """
         Point d'entré du module pour gérer les ordres associés par la reconnaissance vocale
        """    
        groupe = obj['groupe']
        if groupe != 'bebepaz' :
            return     
        
        ordre = self.ORDRES[obj['ordre']]
        
        print ("Ordre lancé : " + obj['ordre'])
        #print ("appel de la function : " + ordre["function"])
        print ("origine  : " + obj["origine"])
        # print ("recognised  : " + str(obj["recognised"]))
        print ("input  : " + str(obj["input"]))


    def isCameraActive(self, args = None):
        """
            return un objet JSON de cameraActive
        """
        obj = {}
        obj['cameraActive'] = self.isCamera()
        return obj

    def isCamera(self):
        return self.isActive
    
    def startCamera(self, args = None):    
        """
            Activer par l'IHM
        """
        print ("bebe_paz.py : Start vocal")
        self.isActive = True
        
        
    def stopCamera(self, args = None):   
        """
            Activer par l'IHM
        """
        print ("bebe_paz.py : Stop vocal")
        self.isActive = False

class MainPipeline(threading.Thread):
    
    videosink = None
    served_image_timestamp = 0
    
    def __init__(self):
        super(MainPipeline, self).__init__()
        self.current_buffer = None
        self.served_image_timestamp = time.time()
        self.interval = 0.1
        print("Initializing GST Elements")
    
        self.pipeline = Gst.Pipeline.new("server")

        self.videosrc = Gst.ElementFactory.make("udpsrc")
        self.videosrc.set_property("port", 50003)
        self.depay = Gst.ElementFactory.make("rtpjpegdepay")
        self.videosink = Gst.ElementFactory.make("appsink")
        self.videosink.set_property("emit-signals", True)

        self.videosink.connect("new-sample", self.pull_frame)

        caps = Gst.caps_from_string(" application/x-rtp, encoding-name=JPEG, payload=26")
        self.videosrc.set_property("caps", caps)

        # Build the pipeline
        self.pipeline.add(self.videosrc)
        self.pipeline.add(self.depay)
        # self.pipeline.add(self.decoder)
        self.pipeline.add(self.videosink)

        
        if not Gst.Element.link(self.videosrc, self.depay):
            print("Elements could not be linked.")
            exit(-1)
        #if not Gst.Element.link(self.depay, self.decoder):
        #    print("Elements could not be linked.")
        #    exit(-1)
        if not Gst.Element.link(self.depay, self.videosink):
            print("Elements could not be linked.")
            exit(-1)
        
        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
 
        self.bus.connect('message', self.on_message)
        
    def on_message(self, bus, message):
        t = message.type
        print (str(message.type))
        #if t == Gst.MessageType.EOS:
        #    self.on_next()
        #elif t == Gst.MessageType.ERROR:
        #    self.on_next()    
    
        

    def pull_frame(self, sink):
        # second param appears to be the sink itself
        sample = sink.emit("pull-sample")
        if sample is not None:
            self.current_buffer = sample.get_buffer()
            data = self.current_buffer.extract_dup(0, self.current_buffer.get_size())
            if data:
                if self.served_image_timestamp + self.interval < time.time():
                    for q in queues:
                        if not q.full() :
                            q.put(data)
                        else :
                            queues.remove(q)    
                    self.served_image_timestamp = time.time()
        return False

    def run(self):
        self.pipeline.set_state(Gst.State.PLAYING)
        loop = GObject.MainLoop()
        loop.run()   

