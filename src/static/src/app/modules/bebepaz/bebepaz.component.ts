import { Component, OnInit } from '@angular/core';
import { BebepazService } from './bebepaz.service';

@Component({
  selector: 'bebe-paz',
  templateUrl:"./bebepaz.html",
  styleUrls:['bebepaz.scss'],
   providers: [BebepazService],
})
export class BebepazComponent implements OnInit {

  isActive: boolean = false;
  isMusicActive: boolean = false;
  errorMessage: string;
  stream:any;

  constructor(private service: BebepazService) { }

  ngOnInit() { 
    this.isActived(); 
    this.stream = 'http://'+ window.location.hostname + ':7002/mjpeg_stream'
  }

  isActived() {
    this.service.isCameraActive().subscribe(
      isActive => {
        this.isActive = isActive
      },
      error => this.errorMessage = <any>error);
  }

  onChange() {
    if (this.isActive) {
      this.service.startCamera().subscribe(
        isActive => console.log(),
        error => this.errorMessage = <any>error);
    } else {
      this.service.stopCamera().subscribe(
        isActive => console.log(),
        error => this.errorMessage = <any>error);
    }
  }

  onChangeMusique() {
    if (this.isMusicActive) {
      this.service.startMusic().subscribe(
        isActive => console.log(),
        error => this.errorMessage = <any>error);
    } else {
      this.service.stopMusic().subscribe(
        isActive => console.log(),
        error => this.errorMessage = <any>error);
    }
  }


  


}