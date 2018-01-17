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
import os, re, sys, time, subprocess, platform, socket
import threading
import urllib.request
import netifaces  

from .Bus import Bus
from core.dao.DevicesDao import DevicesDAO, Device
from core import PORT_BASE, PORT_ADD, PORT_CONTROL_SAT_CONNECT, IP_MIN_SCAN,\
    IP_MAX_SCAN, PORT_MIN_SCAN, PORT_MAX_SCAN


osDetect = platform.system()
topiLogger = logging.getLogger('DevicesService')

class Module():
        
    def getIstance(self):
        print("Chargement du module DevicesService.....")
        return "devicesService", DevicesService()

class DevicesService():
    
    scanEnCours = False
    devices = []
    """
        devicesConected permet de garder en mémoire les connected et recharger leur resources suite a un scan 
    """
    devicesConnected = {}
    port_to_next = PORT_BASE

    def __init__(self):
        self.bus= Bus()
        self.devicesDao = DevicesDAO()
        self.loadDevives()
        self.d = ControlConnectedDevice(self)
        self.d.start()

    def ping(self, ip, macAddr, resources):
        if macAddr not in self.devicesConnected :
            self.devicesConnected[macAddr] = resources
        self.bus.subscribe('connectedDeviceDAO', self.connectedDeviceCallBack) 
        portToConnect = -1
        for device in self.devices :
            if device.mcAdress == macAddr :
                if device.port != -1 :
                    portToConnect = device.port
                break
        if portToConnect == -1 :        
            self.port_to_next += PORT_ADD
            portToConnect = self.port_to_next
        print("port to connect : " + ip + " => " + str(portToConnect))
        self.devicesDao.connectedDevice(macAddr, resources,  portToConnect, ip)
        return portToConnect

    def connectedDeviceCallBack(self, bus, key, devices):
        self.devices = devices
        obj = {'key':"loadDevices"   , 'devices' : devices}
        self.bus.publish('deviceService', obj)
        
    def loadDevives(self, args = None):
        self.bus.subscribe('loadDeviceDAO', self.loadDevicesCallBack) 
        self.devices = self.devicesDao.load()
        return self.devices

    def loadDevicesCallBack(self, bus, key, devices):
        self.devices = devices
        self.scan()
        obj = {'key':"loadDevices"   , 'devices' : devices}
        self.bus.publish('deviceService', obj)

    def scan(self):
        self.scanNetwork = ScanDevice(self)
        self.scanNetwork.start()
        return self.devices
 
    def saveDevives(self, args):      
        return self.devicesDao.updateOrSave(args)


class ControlConnectedDevice(threading.Thread) :
    def __init__(self, parent):
        super(ControlConnectedDevice, self).__init__()
        self.parent = parent

    def run(self):
        while 1 :
            for device in self.parent.devices :
                if device.isTopiConnected :
                    try :
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(5)
                        s.connect((device.ip, PORT_CONTROL_SAT_CONNECT))
                    except Exception as e:
                        print("ControlConnectedDevice error " + e.__str__())
                        print("Deconnexion du device : " + device.ip)
                        device.setIsTopiConnected(False)
                        del self.parent.devicesConnected[device.mcAdress]
                        obj = {'key':"scan", 'devices' : self.parent.devices}
                        self.parent.bus.publish('deviceService', obj)
                        data = {'ip': device.ip, 'macAddress' : device.mcAdress}
                        self.parent.bus.publish('deviceDeconnected', data)        

            time.sleep(5)         
            
            
class ScanDevice(threading.Thread) :
      
    def __init__(self, parent):
        super(ScanDevice, self).__init__()
        self.parent = parent
        self.scan_ports = Scan_ports()
    
    def run(self):
      
        if self.parent.scanEnCours == True:
            return
        self.parent.scanEnCours = True
        print("TopiBox Scan 1.0 sur " + osDetect)
        
        cn = CheckNetwork() 
        netinfo = cn.check_network()
        (ip, mask, mcAdress) = netinfo
        self.manageDevice(mcAdress, ip)

        if not ip :
            print("Error: No network range given.")
            print("Usage:\t" + sys.argv[0] + " 10.0.0.0/24")
            sys.exit(1)
       
        ping = Ping()
        pingScan = ping.ping(ip)
        pingScan.sort()
            
    #    response = ssdp.discover("upnp:rootdevice")
    #    print "ssdp : " + str(response)       
                 
        listmac = subprocess.Popen(['arp', '-a'] ,stdout = subprocess.PIPE,stderr = subprocess.PIPE,  universal_newlines=True)            
        out, error = listmac.communicate()
        if osDetect == "Linux":
            out = out.split('\n')
        else:   
            out = out.split('\r\n')
        
        for i in out:
            ip = re.search(r'[0-9]+(?:\.[0-9]+){3}', i)
            if ip and ip.group() in pingScan:
                mcadres = re.search(r'([0-9A-F]{2}[:-]){5}([0-9A-F]{2})', i, 0)
                if mcadres:
                    self.manageDevice(mcadres.group(), ip.group())

#        self.scan_ports.ports_scan(self.parent.devices)

        self.parent.devices.sort(key=attrgetter('ip'))                
        
        for macAddr in self.parent.devicesConnected :
            for device in self.parent.devices :
                if device.mcAdress == macAddr :
                    self.parent.devicesDao.connectedDevice(macAddr, self.parent.devicesConnected[macAddr], device.port)
        
        obj = {'key':"scan", 'devices' : self.parent.devices}
        self.parent.bus.publish('deviceService', obj)
        self.parent.scanEnCours = False
        print("TopiBox Fin Scan sur " + osDetect)
            
    
    def manageDevice(self, mcadress, ip):
        result = None
        try:
            url = "http://api.macvendors.com/"
            mcVendor = urllib.request.urlopen(url + mcadress).read()
            isNotExist = True
            mcAddress = mcadress.replace("-", ":")
            for device in self.parent.devices :
                if device.mcAdress == mcAddress :
                    device.setIp(ip)
                    device.setIsConnected(True)
                    isNotExist = False
                    result =  device
                    break
                                    
            if isNotExist :
                result = Device(ip, mcAddress, mcVendor)
                result.setIsConnected(True)
                self.parent.devices.append(result)
                
        except Exception as e:
            print("erreur DevicesService scan : " + e.__str__())    
            
        return result        
            
class CheckNetwork():
            
    def check_network(self):
        
        interfaces = netifaces.interfaces()
        
        ipDefault = ""
        maskDefault = ""
        macAddrDefault = ""

        for i in interfaces:
            addrs = netifaces.ifaddresses(i)
            try:
                ip = addrs[netifaces.AF_INET][0]['addr']
                mask = addrs[netifaces.AF_INET][0]['netmask']
                bcast = addrs[netifaces.AF_INET][0]['broadcast']
                macAddr = addrs[netifaces.AF_LINK][0]['addr']
                if ip != '127.0.0.1':
                    ipDefault = ip
                    maskDefault = mask
                    macAddrDefault = macAddr
            except Exception as e: 
                pass        
        return (ipDefault, maskDefault, macAddrDefault)
    
class Ping():
    
    def ping(self, ipHost):    

        utils =Utils()
        ipPingList = []
        iprange = utils.find('(\w+\.\w+\.\w+)', ipHost)
        
        p = [] # ip -> process
        act = 0
        nrp = 0
        err = 0
        
        for n in range(IP_MIN_SCAN, IP_MAX_SCAN): # start ping processes
            ip = iprange +".%d" % n
            arg = ["ping"]
            if osDetect == "Linux":
                arg.append("-c3")
                arg.append("-w5")
            else:   
                arg.append("-n")
                arg.append("3")
            arg.append(ip)
            p.append((ip, subprocess.Popen(arg ,stdout = subprocess.PIPE,stderr = subprocess.PIPE)))
        
        while p:
            for i, (ip, proc) in enumerate(p[:]):
                if proc.poll() is not None: # ping finished
                    p.remove((ip, proc)) # this makes it O(n**2)
        
                    if osDetect == "Windows":    
                        out, error = proc.communicate()
                        out = out.split('\n')
                        isCorrect = False
                        for line in out:
                            if (ip in line) & ("TTL" in line):
                                isCorrect = True
                                
                        if isCorrect:
                            ipPingList.append(ip)
                            act = act + 1
                        else:
                            err=err+1
                    elif osDetect == "Linux":
                        if proc.returncode == 0:
                            out, error = proc.communicate()
                            out = out.strip()
                            act = act + 1
                            ipPingList.append(ip)
                        elif proc.returncode == 2:
                            nrp=nrp+1
                        else:
                            err=err+1
            time.sleep(.04)
        
        return ipPingList


class connect_to_host(threading.Thread):
    def __init__(self, host, ports):
        super(connect_to_host, self).__init__()
        self.host=host
        self.ports=ports
        self.portsOpen=[]

    def run(self):
        try:
            for port in self.ports:  
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex((self.host, port))
                if result == 0:
                    self.portsOpen.append(port)
                sock.close()

        except KeyboardInterrupt:
            print("You pressed Ctrl+C")
        
        except socket.gaierror:
            print('Hostname could not be resolved. Exiting')
        
        except socket.error:
            print("Couldn't connect to server")

class Scan_ports():

    def ports_scan(self, hosts):
        
        ports = list(range(PORT_MIN_SCAN, PORT_MAX_SCAN))
        threadTmp = []
        
        for host in hosts:
            if hasattr(socket, 'setdefaulttimeout'):   
                socket.setdefaulttimeout(5)

            t= connect_to_host(host.ip, ports)
            threadTmp.append(t)
            t.start()
       
        while threadTmp:
            for i, t in enumerate(threadTmp[:]):
                if not t.is_alive():
                    threadTmp.remove(t)
                    print(t.host + " " + str(t.portsOpen))  
            time.sleep(.4) 


class Utils():
    
    def find(self, needle, haystack):
        match = re.search(needle, haystack)
        if match:   
            if len(match.groups()) > 1:
                return match.groups()
            elif len(match.groups()) == 1:
                return match.groups()[0]
            else:
                return "None"
        
    def cmd_exists(self, cmd):
        if self.invoke("which " + cmd + " 2>&1").find("no " + cmd) == -1:
            return True
        return False
    
    def invoke(self, cmd):
        (sin, sout) = os.popen2(cmd)
        return sout.read()
    

    
#    def __str__(self):
#        return self.ip + " ---> " + self.mcAdress + " ---> " + self.mcVendor+ " ---> " + str(self.isXbmc)
    

if __name__ == "__main__":
    app = DevicesService()
    devices = app.loadDevives()
    print(devices.__str__())
    