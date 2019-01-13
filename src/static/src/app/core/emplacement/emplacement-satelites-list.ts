import { Component, OnInit, Input, ViewEncapsulation } from '@angular/core';

import { EmplacementService }     from './emplacement.service';
import { ObjectConnectedService } from '../objects-connected/objects-connected.service';

import { Emplacement }            from './Emplacement';
import { ObjectConnected }        from '../objects-connected/ObjectConnected';

import { Modal } from '../../common/modal/modal.component';

@Component({
  selector: 'emplacement-satelites-list',
  templateUrl:"./emplacement-satelites-list.html",
  providers: [EmplacementService, ObjectConnectedService],
  styleUrls:[
    'emplacement-satelites-list.scss'
  ],
 
})
export class EmplacementSatelitesListComponent implements OnInit { 
  
    @Input() item:Emplacement;
    devices: ObjectConnected[];
    errorMessage: string;
    _modal = null;
    name:string;

  constructor(private emplacementService: EmplacementService, private objectConnectedService:ObjectConnectedService) { }

  ngOnInit() { this.getDevices(); }

  getDevices() {
    this.objectConnectedService.getObjectsConnected().subscribe(
      devices => this.devices = devices,
      error => this.errorMessage = <any>error);
  }

    bindModal(modal) {this._modal=modal;}

    save(){
        this.item.devices = [];
        this.devices.map(device => {
                if ( device.isAssociated) {
                    this.item.devices.push(device);
                } });
        this.emplacementService.saveDevicesByEmplacement(this.item).subscribe(
            () => this.close(),
            error => { 
                this.errorMessage = <any>error;   
                this.close();
            });
    }

    edit(){
        this.devices.map(device => device.isAssociated = false);

        for (let devicesAssociated of this.item.devices){
            this.devices.map(device => {
                if (devicesAssociated.id === device.id ){
                    device.isAssociated = true;
                }
            });
        }
        this._modal.open();
    }

    close() {
        this._modal.close();
    }
}