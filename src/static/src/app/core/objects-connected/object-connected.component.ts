import { Component, Input, OnInit } from '@angular/core';

import { ObjectConnectedService } from './objects-connected.service';

import { ObjectConnected }           from './ObjectConnected';


@Component({
  selector: 'object-connected',
  templateUrl:"./object-connected.html",
  providers: [ObjectConnectedService],
  styleUrls:[
    'object-connected.scss'
  ],
})
export class ObjectCOnnectedComponent implements OnInit {
  
  @Input() item: ObjectConnected;
 
  img_micro: string = "";
  img_enceinte: string = "";
  img_ecran: string = "";
  img_camera: string = "";
  img_kodi: string = "";
  img_mobil: string = "";
  img_is_vocal: string = "";

  ngOnInit() { this.manageImage(); }

  manageImage(){
    if (this.item.hasMicrofone){
      this.img_micro = 'assets/img/Microphone.svg'
    }
    if(this.item.microConnected){
      this.img_micro = 'assets/img/Microphone_red.svg'
    }
	  if(this.item.hasCamera){
	    this.img_camera = 'assets/img/camera.svg'
    }
    if(this.item.cameraConnected){
	    this.img_camera = 'assets/img/camera_red.svg'
    }
	  if(this.item.hasEcran){
	    this.img_ecran = 'assets/img/screen.svg'
    }
    if(this.item.screenConnected){
	    this.img_ecran = 'assets/img/screen_red.svg'
    }
	  if(this.item.hasHautParleur){
	    this.img_enceinte = 'assets/img/Speaker.svg'
	  }
    if(this.item.speakerConnected){
	    this.img_enceinte = 'assets/img/Speaker_red.svg'
    }
	  if(this.item.hasKodi){
	    this.img_kodi = 'assets/img/kodi.png'
    }
    if(this.item.isVocal){
	    this.img_is_vocal = 'assets/img/jarvis.jpg'
    }
  }

}