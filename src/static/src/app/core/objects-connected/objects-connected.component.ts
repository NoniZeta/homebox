import { Component, OnInit, ViewEncapsulation } from '@angular/core';

import { ObjectConnectedService } from './objects-connected.service';
import { WebSocketService } from '../../common/service/websocket.service';

import { ObjectConnected }           from './ObjectConnected';

import { Modal } from '../../common/modal/modal.component';



@Component({
  templateUrl:"./objects-connected.html",
  providers: [ObjectConnectedService, WebSocketService],
  styleUrls:[
    'objects-connected.scss'
  ],
 
})
export class ObjectsConnectedListComponent implements OnInit { 
  
    objectsConnected;
    errorMessage: string;
    _modal = null;
    item:ObjectConnected;
    name:string;
    hasMicrophone:number;
    hasEnceinte:number;
    hasEcran:number;
    hasCamera:number;

  constructor(private objectConnectedService: ObjectConnectedService, wvService:WebSocketService) {
          wvService.connect("deviceService").subscribe(obj => {
              if (obj.key === 'scan'){ 
                this.objectsConnected = obj.devices;
              }
              if (obj.key === 'loadDevices'){  
                this.objectsConnected = obj.devices;
              }
          });
   }

  ngOnInit() { this.getObjectsConnected(); }

  getObjectsConnected() {
    this.objectConnectedService.getObjectsConnected().subscribe(
      objectsConnected => {
          this.objectsConnected = objectsConnected
      },
      error => this.errorMessage = <any>error);
  }

  bindModal(modal) {this._modal=modal;}

    open(client) {
        this.item = client;
        this.name = this.item.name;
        this.hasMicrophone = this.item.hasMicrofone;    
        this.hasEnceinte = this.item.hasHautParleur;
        this.hasEcran = this.item.hasEcran;
        this.hasCamera = this.item.hasCamera;
        this._modal.open();
    }

    save(){
        this.item.name = this.name;
        this.item.hasMicrofone = this.hasMicrophone;    
        this.item.hasHautParleur = this.hasEnceinte;
        this.item.hasEcran = this.hasEcran;
        this.item.hasCamera = this.hasCamera;
        this.objectConnectedService.save(this.item).subscribe(
            objectsConnected => {
                this.objectsConnected = objectsConnected;
                this.close();
            },
            error => { 
                this.errorMessage = <any>error;   
                this.close();
            });
    }

    close() {
        this._modal.close();
    }

    onChangeM(flag){
         this.hasMicrophone = flag ? 1 : 0;
   }

    onChangeE(flag){
         this.hasEnceinte = flag ? 1 : 0;
   }
    
    onChangeEc(flag){
         this.hasEcran = flag ? 1 : 0;
   }

    onChangeC(flag){
         this.hasCamera = flag ? 1 : 0;
   }

}