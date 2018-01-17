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

import platform

from .Bus import Bus
from core.dao.EmplacementDAO import  EmplacementsDAO, DevicesByEmplacementsDAO


osDetect = platform.system()

class Module():
        
    def getIstance(self):
        print("Chargement du module EmplacementService.....")
        return "emplacementsService", EmplacementService()


class EmplacementService():
    
    devices = []
    emplacements = [] 
    devicesByEmplacement = []
    
    def __init__(self):
        self.bus = Bus()
        self.bus.subscribe('deviceService', self.changeListDevices)
        self.emplacementDAO = EmplacementsDAO()
        self.devicesByEmplacementDAO = DevicesByEmplacementsDAO()
        
    def changeListDevices(self, bus, key, obj):
        f = obj["key"]
        listDevices = obj["devices"] 
        if f == "loadDevices" :
            self.devices = listDevices
            self.mergeDevicesEmplacements()
        
    def loadEmplacements(self, args = None):
        self.emplacements = self.emplacementDAO.load()
        self.devicesByEmplacement = self.devicesByEmplacementDAO.load()
        self.mergeDevicesEmplacements()
        return self.emplacements

    def mergeDevicesEmplacements(self):
        if len(self.devices) == 0 and len(self.devicesByEmplacement) == 0 and len(self.emplacements) == 0 : 
            return
        for emplacement in self.emplacements: 
            emplacement.setListDevices([])
        for (idEmplacement, idDevice) in self.devicesByEmplacement:
            for emplacement in self.emplacements: 
                if emplacement.id == idEmplacement:
                    for device in self.devices: 
                        if hasattr(device, 'id') and device.id == idDevice :
                            emplacement.addDevice(device)
                    break
        
        obj = {'key':"loadEmplacements", 'emplacements' : self.emplacements}
        self.bus.publish('emplacementService', obj)


    def insertOrUpdateEmplacements(self, args):
        return self.emplacementDAO.updateOrSave(args)
    
    def deleteEmplacements(self, ids):
        for id in ids:
            self.deleteEmplacement(id)
        return True
                
    def deleteEmplacement(self, id):
        self.devicesByEmplacementDAO.delete(id)
        self.emplacementDAO.delete(id)
        return True

    def saveDevicesByEmplacement(self, emp):
        self.devicesByEmplacementDAO.delete(emp[0].id)
        result = []
        for device in emp[0].devices:
            result.append((emp[0].id, device.id))
            
        return self.devicesByEmplacementDAO.updateOrSave(result)

if __name__ == "__main__":
    emplService = EmplacementService()
    test = emplService.loadEmplacements()
    