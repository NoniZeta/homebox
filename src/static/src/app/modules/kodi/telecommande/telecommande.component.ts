import { Component, Input, OnInit } from '@angular/core';

import { KodiService }              from '../kodi.service';

import { ObjectConnected }              from '../../../core/objects-connected/ObjectConnected';

@Component({
  selector: 'telecommande',
  templateUrl:"./telecommande.html",
  providers: [KodiService],
  styleUrls:['telecommande.scss']
})
export class Telecommande implements OnInit {

    private deviceConnected:ObjectConnected;
    private player: string = "1";
    private errorMessage: string;


    constructor(private kodiService: KodiService) {}

    ngOnInit() { 
        this.kodiService.detectKodi().subscribe(
            kodiDevices => this.deviceConnected = kodiDevices[0],
            error => this.errorMessage = <any>error);
    }

    public play(){
        let data: any[] = [{'ip':this.deviceConnected.ip, 'ordre':'PlayPause', 'arguments':this.player}]
        this.kodiService.ordre(data).subscribe(
            data => console.log(data),
            error => this.errorMessage = <any>error);
    }

    public stop(){
         let data: any[] = [{'ip':this.deviceConnected.ip, 'ordre':'Stop', 'arguments':this.player}]
        this.kodiService.ordre(data).subscribe(
            data => console.log(data),
            error => this.errorMessage = <any>error);
    }

    public scanVideo(){
         this.kodiService.scanVideo().subscribe(
            data => console.log(data),
            error => this.errorMessage = <any>error);
    }
    
    public scanMusic(){
        this.kodiService.scanMusic().subscribe(
            data => console.log(data),
            error => this.errorMessage = <any>error);
    }

    public showNotification(){
        this.kodiService.showNotification().subscribe(
            data => console.log(data),
            error => this.errorMessage = <any>error);
    }

    
}