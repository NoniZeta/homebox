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

import logging, json

from core.Bus import Bus


logger = logging.getLogger('WebSocketFacade')

class WebSocketFacade():
    
    def __init__(self):
        self.waiters = []
        self.bus= Bus()
        
    def addWaiters(self, waiter):  
        self.bus.subscribe(waiter.service, self.write_message) 
        self.waiters.append(waiter) 
            
    def write_message(self, bus, key, obj):  
        for waiter in self.waiters:
            try:
                if waiter.service == key:
                    if hasattr(obj, "__dict__"):
                        jsonObj = json.dumps(obj.__dict__, default=lambda o: o.__dict__)
                    else:
                        jsonObj = json.dumps(obj, default=lambda o: o.__dict__)
                    waiter.write_message(jsonObj)
                    
            except Exception as e:
                logger.error("erreur WS : %s",  e.__str__())
        
    def removeWaiters(self, waiter):
        self.waiters.remove(waiter)
        
        

