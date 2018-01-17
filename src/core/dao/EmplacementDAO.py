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
import uuid

from core.Bus import Bus
from core import HOST_DB, PORT_DB, USER_DB, PASSWD_DB, DB_DB
import mysql.connector


logger = logging.getLogger('EmplacementsDAO')

class EmplacementsDAO():
    
    emplacements = []
    
    def __init__(self):
        self.bus= Bus()

    def load(self):
        items = []
        try:
            logger.debug('Load emplacements BDD')
            _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
            cr = _db.cursor()
            cr.execute("SELECT * FROM emplacement")
            results = cr.fetchall()
            cr.close()    
            _db.close()
            for (idEmpl, name) in results:
                item = Emplacement(name)
                item.setId(idEmpl)
                items.append(item)
                
        except Exception as e:
            print("Erreur emplacementDao run ..." +  e.__str__())
            # logger.error("BDD loadDevives" + e.__str__())

        items.sort(key=attrgetter('name'))
        self.emplacements= items
        return self.emplacements
    
    def updateOrSave(self, args):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToInsert = """
                        INSERT INTO emplacement (id, name) 
                        VALUES (%s, %s)
                     """
        sqlToUpdate = """
                        UPDATE emplacement SET  name = %s
                        where id = %s
                      """   

        for arg in args: 
            if hasattr(arg, 'id'):
                data= (arg.name, arg.id)
                cr.execute(sqlToUpdate, data)
            else:    
                idEmplacement = str(uuid.uuid4())
                data= (idEmplacement, arg.name)
                cr.execute(sqlToInsert, data)             
    
        _db.commit()       
        return True
    
    def delete(self, idEmplacement):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlDelete = "delete from emplacement where id = '%s' ;"   %idEmplacement
        cr.execute(sqlDelete)     
        _db.commit()

class DevicesByEmplacementsDAO():
    
    def __init__(self):
        self.bus= Bus()

    def load(self):
        results = []
        try:
            logger.debug('Load devicesByemplacement BDD')
            _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
            cr = _db.cursor()
            cr.execute("SELECT * FROM devicesByEmplacement")
            results = cr.fetchall()
            cr.close()    
            _db.close()
             
        except Exception as e:
            print("Erreur DevicesByEmplacementDao run ..." +  e.__str__())
            # logger.error("BDD loadDevives" + e.__str__())
        return results
    
    def updateOrSave(self, args):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToInsert = """
                        INSERT INTO devicesByEmplacement (idEmplacement, idDevice) 
                        VALUES (%s, %s);
                     """

        for (idEmplacement, idDevice) in args:              
            data= (idEmplacement, idDevice)
            cr.execute(sqlToInsert, data)     
    
        _db.commit()       
    
    def delete(self, idEmplacement):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlDelete = "delete from devicesByEmplacement where idEmplacement = '%s';" %idEmplacement
        cr.execute(sqlDelete)     
        _db.commit()

class Emplacement():
        
    def __init__(self, name):
        self.name = name
        self.devices = []    
        
    def setId(self, id):
        self.id = id   
        
    def setName(self, name):
        self.name = name
        
    def setListDevices(self, devices):
        self.devices = devices
        
    def addDevice(self,idDevice):
        self.devices.append(idDevice)    

if __name__ == "__main__":
    emplDAO = EmplacementsDAO()  
    empls = []

    empl = Emplacement('test')
    empls.append(empl)  
    
    emplDAO.updateOrSave(empls)
    
    emplLoaded = emplDAO.load()
    
    for item in emplLoaded :
        if item.name == 'test' :
            emplDAO.delete(item.id)
    
    
    deviceByEmplDAO = DevicesByEmplacementsDAO()  
    args = [('1','901f883d-2e51-4b6e-b7ae-baf592eb9d22'),('1', 'c0521d08-095e-4f3b-b828-9214c925d0ca' ),('1', 'd4e5871a-0f11-4d42-94bb-0b8991fc42e6')]
    deviceByEmplDAO.updateOrSave(args)
    
    devicesByEmpl = deviceByEmplDAO.load()
    
    deviceByEmplDAO.delete('1')
    