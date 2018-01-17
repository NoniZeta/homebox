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
import glob, sys
import json
import logging
from os.path import dirname, basename, isfile
import os.path
import threading

from core import PORT_SERVER
from core.DownloadFilesService import DownloadFiles
from core.WebSocketFacade import WebSocketFacade
from tornado import gen
from tornado.options import define, options
import tornado.web
import tornado.websocket


define("port", default=PORT_SERVER, help="run on the given port", type=int)

def main():
    global webSocketFacade
    global topiLogger
    global modules
    global downloadFiles 

    logging.basicConfig(filename='/tmp/out.log',level=logging.DEBUG, format='%(asctime)s : %(levelname)s : %(name)s => %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    topiLogger = logging.getLogger('TopiServer')
    topiLogger.info('Start server')
    webSocketFacade = WebSocketFacade()
    downloadFiles = DownloadFiles()
    
    modules = {}
    loadModules("core")
    loadModules("module")
    
    getattr(modules["modelVocalService"], "activate")()

    ordres = getattr(modules["modelVocalService"], "getOrdres")()
    actions = getattr(modules["modelVocalService"], "getActions")()
    variables = getattr(modules["modelVocalService"], "getVariables")()
    numeric = getattr(modules["modelVocalService"], "getNumeric")()
    
    getattr(modules["vocal"], "loadActions")(actions)
    getattr(modules["vocal"], "loadOrdres")(ordres)
    getattr(modules["vocal"], "loadVariables")(variables)
    getattr(modules["vocal"], "loadNumeric")(numeric)
    
    getattr(modules["vocal"], "activate")()
    
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

def loadModules(packageName):
    modules_path = glob.glob(dirname(__file__)+ "/" + packageName + "/*.py")
    __all__ = [ basename(f)[:-3] for f in modules_path if isfile(f)]

    for m_ in __all__:
        if m_ != "__init__"  and m_ != "facade" and m_ != "DecodeThread":
            try:
                module_name = packageName + "." + str(m_)
                __import__(module_name, globals={}, locals={}, fromlist=[], level=0)
                modul = sys.modules[module_name]
                inst = getattr(modul, 'Module')()    
                name, instMod = getattr(inst, "getIstance")()
                modules[name] = instMod 
                if hasattr(instMod, "ORDRES") :
                    getattr(modules["modelVocalService"], "setOrdresbyModules")(instMod.ORDRES, instMod.VARIABLES, name)
                    #modelVocalService.setOrdresbyModules(instMod.ORDRES, instMod.VARIABLES, name)   
            except Exception as e :
                print (e.__str__())

class Application(tornado.web.Application):
    def __init__(self):
         
        settings = dict(
         #   cookie_secret="_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            template_path=os.path.join(os.path.dirname(__file__), "static/dist"),
            static_path=os.path.join(os.path.dirname(__file__), "static/dist"),
            
          #   compress_response=True,
        #    xsrf_cookies=True,
        )
        
        handlers = [
            (r"/", MainHandler),
            (r"/jsonMessage", JsonMessageHandler),
            (r"/ping", PingHandler),
            (r"/ws", WSMessageHandler),
            (r"/mjpeg_stream", MJPEGHandler),
        ]
       
        tornado.web.Application.__init__(self, handlers, **settings)
        

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class JsonMessageHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.modules = modules
        
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET,PUT,POST,OPTIONS,DELETE")
        self.set_header("Access-Control-Allow-Headers", "Content-Type, Depth, User-Agent, X-File-Size, X-Requested-With, X-Requested-By, If-Modified-Since, X-File-Name, Cache-Control")

    @gen.coroutine
    @tornado.web.asynchronous
    def post(self):
        try :
            data = json2obj(self.request.body)
            args = data.parameters
            module = data.module
            func =  getattr(self.modules[module], data.method)
        except Exception as e :
            print (e.__str__())
            #raise e
        t = Worker(self.worker_done, args, func)
        t.start()
        #self.finish()
        
    def get(self):
        self.write('some get')

    def options(self):
        # no body
        self.set_status(204)
        self.finish()
    
    def worker_done(self, obj):
        if hasattr(obj, "__dict__"):
            jsonObj = json.dumps(obj.__dict__, default=lambda o: o.__dict__)
        else:
            jsonObj = json.dumps(obj, default=lambda o: o.__dict__)

        topiLogger.debug("JSONMessage : message received %r", jsonObj)             
        self.write(jsonObj)
        self.finish()
        
class Worker(threading.Thread):
    def __init__(self, callback=None, arguments=None, func=None, *args, **kwargs):
        super(Worker, self).__init__(*args, **kwargs)
        self.func = func
        self.arguments = arguments
        self.callback = callback

    def run(self):
        obj = self.func(self.arguments)
        self.callback(obj)


class PingHandler(tornado.web.RequestHandler):
    
    def initialize(self):
        self.modules = modules
        self.downloadFiles = downloadFiles

    def post(self):
        print ('Topiserver => Ping ')
        try :
            arguments = json2obj(self.request.body)
            ip_obj = arguments.ip
            macAddr = arguments.macAddr
            resources = arguments.resources
       
            self.obj = {}
            if getattr(modules["modelVocalService"], "vocalReady") :
            #  if modelVocalService.vocalReady :
                self.obj['port'] =  getattr(self.modules["devicesService"], "ping")(ip_obj, macAddr, resources)
                self.obj['vocalActive'] =  getattr(self.modules["vocal"], "isVocal")()
                self.obj['sumsOfFiles'] = self.downloadFiles.getFilesVocal()

                
            if hasattr(self.obj, "__dict__"):
                jsonObj = json.dumps(self.obj.__dict__, default=lambda o: o.__dict__)
            else:
                jsonObj = json.dumps(self.obj, default=lambda o: o.__dict__)
            topiLogger.debug("Ping : message received %r", jsonObj)
    
            self.add_header('Content-Type', 'application/x-www-form-urlencoded')    
            self.write(jsonObj)
            self.finish()
            #print str(time.time() - t_1)
        except Exception as e:
            print (str(e))

class WSMessageHandler(tornado.websocket.WebSocketHandler):
    
    def check_origin(self, origin):
        return True

    def open(self):
        arguments = self.request.arguments
        service = arguments['service']
        self.service = str(service[0])
        webSocketFacade.addWaiters(self)

    def on_close(self):
        webSocketFacade.removeWaiters(self)

    def on_message(self, message):
        parsed = tornado.escape.json_decode(message)
        topiLogger.info("got message %r", parsed)


class MJPEGHandler(tornado.web.RequestHandler):
    
    def initialize(self):
        self.stream = getattr(modules["bebepaz"], "stream")
    
    
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):

        self.set_header( 'Content-Type', 'multipart/x-mixed-replace;boundary=--boundarydonotcross')
        try :    
            for img in self.stream() :
                
                self.write("--boundarydonotcross\n")
                self.write("Content-type: image/jpeg\r\n")
                self.write("Content-length: %s\r\n\r\n" % len(img))
                self.write(str(img))
                yield tornado.gen.Task(self.flush)
        except Exception as e :
            print ("Topiserver : ThreadMJPEG envoi" + e.__str__())
            
                    
def _json_object_hook(d): 
    return namedtuple('X', d.keys())(*d.values())

def json2obj(data): 
    return json.loads(data, object_hook=_json_object_hook)
    
if __name__ == "__main__":
    main()
    
