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


import logging
from operator import attrgetter
import threading
import time
import uuid

from core import HOST_DB, PORT_DB, USER_DB, PASSWD_DB, DB_DB
from core.Bus import Bus
import mysql.connector


logger = logging.getLogger('DevicesDAO')

class DevicesDAO():
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DevicesDAO, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance

    
    devices = []
            
    def __init__(self):
        self.t = LoadDevice(self)
        self.bus= Bus()
        
    
    def load(self):
        if not self.t.isAlive():
            self.t = LoadDevice(self)
            self.t.start()
        return self.devices
    
    def loadCallback(self):
        self.bus.publish('loadDeviceDAO', self.devices)

    def connectedDevice(self, macAddress, ressources, port, ip = None):
        c = ConnectedDevice(self, macAddress, ressources, port, ip)
        c.start()

    def connectedDeviseCallback(self):
        self.bus.publish('connectedDeviceDAO', self.devices)

    def updateOrSave(self, args):
        logger.debug('updateOrSave devices BDD')

        devices = []
        #try:
        fecha = time.strftime('%Y-%m-%d %H:%M:%S')
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToInsert = """
                        INSERT INTO devices (id, mcAdress, mcVendor, name, ip, lastDateDetect, hautParleur, microfone, ecran, camera, kodi, mobile) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )
                     """
                     
        sqlToUpdate = """
                        UPDATE devices SET  mcAdress = %s, 
                                            mcVendor = %s, 
                                            name = %s, 
                                            ip = %s, 
                                            lastDateDetect = %s,
                                            hautParleur = %s,
                                            microfone = %s,
                                            ecran = %s,
                                            camera = %s,
                                            kodi = %s,
                                            mobile = %s
                        where id = %s
                      """   
        for arg in args:
            device = Device(arg.ip,  arg.mcAdress, arg.mcVendor)
            device.setName(arg.name)
            device.setLastDateDetect(fecha)
            device.setHasCamera(arg.hasCamera)
            device.setHasEcran(arg.hasEcran)
            device.setHasHautParleur(arg.hasHautParleur)
            device.setHasKodi(arg.hasKodi)
            device.setHasMicrofone(arg.hasMicrofone)
            device.setIsMobile(arg.isMobile)
            
            if hasattr(arg, 'id'):
                device.setId(arg.id)
                data= (arg.mcAdress, arg.mcVendor, arg.name, arg.ip, fecha, arg.hasHautParleur, arg.hasMicrofone, arg.hasEcran, arg.hasCamera, arg.hasKodi, arg.isMobile, arg.id)
                cr.execute(sqlToUpdate, data)
            else:    
                idDevice = str(uuid.uuid4())
                device.setId(idDevice)
                data= (idDevice, arg.mcAdress, arg.mcVendor, arg.name, arg.ip, fecha, arg.hasHautParleur, arg.hasEcran, arg.hasMicrofone, arg.hasCamera, arg.hasKodi,arg.isMobile)
                cr.execute(sqlToInsert, data)
            devices.append(device)
                
        _db.commit()           
        return self.load()
    
    def delete(self):
        logger.debug('Delete device BDD')

class ConnectedDevice(threading.Thread) :
    
    def __init__(self, parent, macAddress = None, resources = None, port = None, ip = None):
        super(ConnectedDevice, self).__init__()
        self.parent = parent
        self.macAddress = macAddress
        self.resources = resources
        self.port = port
        self.ip = ip
        self.isVocal = True if self.resources.vocal == "True" else False

    
    def run(self):
        for device in self.parent.devices :
            if device.mcAdress == self.macAddress :
                if self.ip != None and self.ip != device.ip:
                    device.ip = self.ip
                device.setIsTopiConnected(True)
                device.setIsVocal(self.isVocal)
                for resource in self.resources.resources :
                    if resource == 'micro' :    
                        device.setMicroConnected(True)
                    if resource == 'speaker' :    
                        device.setSpeakerConnected(True)
                    if resource == 'camera' :    
                        device.setCameraConnected(True)
                    if resource == 'screen' :    
                        device.setScreenConnected(True)
                if self.port != None :
                    device.setPort(self.port)
                    if self.isVocal :
                        data = {'ip': device.ip, 'macAddress' : device.mcAdress, 'port' : self.port}
                        self.parent.bus.publish('newDeviceConnected', data)        
        self.parent.connectedDeviseCallback()               
   
class LoadDevice(threading.Thread) :
    
    def __init__(self, parent):
        super(LoadDevice, self).__init__()
        self.parent = parent
    
    def run(self):
        devices = []
        try:
            logger.debug('Load devices BDD')
            _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
            cr = _db.cursor()
            cr.execute("SELECT * FROM devices")
            results = cr.fetchall()
            cr.close()
            _db.close()
            for (idDevice, mcAdress, mcVendor, name, ip, last_detect_date, hasHautParleur, hasMicrofone, hasEcran, hasCamera, hasKodi, isMobile) in results:
                device = Device(ip, mcAdress, mcVendor)
                device.setId(idDevice)
                device.setName(name)
                device.setHasCamera(hasCamera)
                device.setHasEcran(hasEcran)
                device.setHasHautParleur(hasHautParleur)
                device.setHasMicrofone(hasMicrofone)
                device.setLastDateDetect(last_detect_date.isoformat())
                device.setHasKodi(hasKodi)
                device.setIsMobile(isMobile)
                devices.append(device)
                
        except Exception as e:
            print("Erreur deviceDao load run ..." +  e.__str__())
            # logger.error("BDD loadDevives" + e.__str__())

        devices.sort(key=attrgetter('ip'))

        self.parent.devices = devices
        self.parent.loadCallback()
    
class Device():
        
    def __init__(self, ip, mcAdress, mcVendor):
        self.ip = ip
        self.port = -1
        self.mcAdress = mcAdress.replace("-", ":")
        self.mcVendor = mcVendor
        self.setHasCamera(False)
        self.setHasEcran(False)
        self.setHasHautParleur(False)
        self.setHasKodi(False)
        self.setHasMicrofone(False)
        self.setIsMobile(True)
        self.setIsConnected(False)
        self.setIsTopiConnected(False)
        self.setMicroConnected(False)
        self.setSpeakerConnected(False)
        self.setCameraConnected(False)
        self.setScreenConnected(False)
        self.setIsVocal(False)

    def setIp(self, ip):
        self.ip = ip   

    def setPort(self, port):
        self.port = port   
    
    def setHasKodi(self, hasKodi):
        self.hasKodi = hasKodi
        
    def setName(self, name):
        self.name = name
    
    def setId(self, id):
        self.id = id   
        
    def setLastDateDetect(self, date):
        self.lastDateDetect = date

    def setHasHautParleur(self, isPresent):
        self.hasHautParleur = isPresent
 
    def setHasMicrofone(self, isPresent):
        self.hasMicrofone = isPresent

    def setHasEcran(self, isPresent):
        self.hasEcran = isPresent

    def setHasCamera(self, isPresent):
        self.hasCamera = isPresent

    def setIsMobile(self, isMobile):
        self.isMobile = isMobile

    def setIsConnected(self, isConnected):
        self.isConnected = isConnected
        
    def setIsTopiConnected(self, isConnected):
        self.isTopiConnected = isConnected  
        if not self.isTopiConnected :
            self.setMicroConnected(False)
            self.setSpeakerConnected(False)
            self.setScreenConnected(False)
            self.setCameraConnected(False)
    
    def setMicroConnected(self, microConnected):
        self.microConnected = microConnected
        
    def setSpeakerConnected(self, speaker):
        self.speakerConnected = speaker

    def setCameraConnected(self, cameraConnected):
        self.cameraConnected = cameraConnected
    
    def setScreenConnected(self, screenConnected):
        self.screenConnected = screenConnected

    def setIsVocal(self, isVocal):
        self.isVocal = isVocal
