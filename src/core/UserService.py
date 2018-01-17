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
import uuid

from core import HOST_DB, PORT_DB, USER_DB, PASSWD_DB, DB_DB
import mysql.connector


osDetect = platform.system()

class Module():
        
    def getIstance(self):
        print("Chargement du module UsersService.....")
        return "usersService", UsersService()


class UsersService():
    
    def __init__(self):
        # self._db = TopiDB()
        pass
    
    def loadUsers(self, args = None):
        users = []
        try: 
            _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
            cr = _db.cursor()
            cr.execute("SELECT * FROM users")
            results = cr.fetchall()
            cr.close()
            for (id, alias, nom, prenom, mcAdress, code_langue, voice_id) in results:      
                user = User(alias, nom, prenom, mcAdress, code_langue)
                user.setId(id)
                user.setVoiceId(voice_id.__str__())
                users.append(user)  
        except Exception as e:
                print("erreur userService loadUsers : " + e.__str__())        
        return users

    def insertOrUpdateUsers(self, args):
        items = []
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()  
        sqlToInsert = "INSERT INTO users (id, alias, nom, prenom, mcAdress, code_langue, voice_id) VALUES (%s, %s, %s, %s, %s, %s, %s )"
        sqlToUpdate = "update users set  alias= %s, nom = %s, prenom= %s, mcAdress= %s, code_langue= %s, voice_id = %s where id = %s"
        try: 
            for arg in args:
                item = User(arg.alias, arg.nom, arg.prenom, arg.mcAdress, arg.code_langue)
                if hasattr(arg, 'voice_id') :
                    item.setVoiceId(arg.voice_id)
                else   : 
                    item.setVoiceId('null') 
                    arg.voice_id = 'null'
                
                if hasattr(arg, 'id'):
                    item.setId(arg.id)
                    data= (arg.alias, arg.nom, arg.prenom, arg.mcAdress, arg.code_langue, arg.voice_id, arg.id)
                    cr.execute(sqlToUpdate, data)
                else:    
                    id = str(uuid.uuid4())
                    item.setId(id)
                    data= ( id, arg.alias, arg.nom, arg.prenom, arg.mcAdress, arg.code_langue, arg.voice_id)
                    cr.execute(sqlToInsert, data)
                items.append(item)
                _db.commit() 
        except Exception as e:
                print("erreur userService insertOrUpdateUsers : " + e.__str__())        
        finally:
            cr.close()

        return items
    
    def deleteUsers(self, ids):
        for id in ids:
            self.deleteUser(id)
        
        return True
                
    def deleteUser(self, id):
        _db = mysql.connector.connect(host=HOST_DB,port=PORT_DB,user=USER_DB,passwd=PASSWD_DB,db=DB_DB)
        cr = _db.cursor()
        sqlToDelete = "DELETE FROM users where id = '%s' ;" %id
        try:
            cr.execute(sqlToDelete)
            print('User delete : ' + id)
        except Exception as e:
                print("erreur userService deleteUser : " + e.__str__())   
        finally:
            _db.commit()   
            cr.close()
        
        return True


class User():
        
    def __init__(self, alias = '', nom = '', prenom = '', mcAdress = '',code_langue = ''):
        self.alias = alias
        self.nom = nom
        self.prenom = prenom
        self.mcAdress = mcAdress.replace("-", ":")
        self.code_langue = code_langue
    
    def setVoiceId(self, voice_id):
        self.voice_id = voice_id
        
    def setId(self, id):
        self.id = id


if __name__ == "__main__":
    us = UsersService()
    
    users = []
    users = us.loadUsers()
    print(users.__str__())
    
    ids = []
    for user in users :
        ids.append(user.id)
     
    if len(ids) > 0 :   
        us.deleteUsers(ids)
    
    user = User('test')
    users.append(user)
    us.insertOrUpdateUsers(users)

    