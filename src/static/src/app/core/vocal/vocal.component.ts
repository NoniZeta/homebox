import { Component, OnInit, ViewEncapsulation } from '@angular/core';

import { VocalService } from './vocal.service';


import { Modal } from '../../common/modal/modal.component';

@Component({
  templateUrl:"./vocal.html",
  providers: [VocalService],
  styleUrls:[
    'vocal.scss'
  ],
 
})
export class VocalComponent implements OnInit { 
  
    emplacements: any[];
    errorMessage: string;
    _modal = null;

  constructor(private service: VocalService) { }

  ngOnInit() { this.getEmplacements(); }

  getEmplacements() {
   // this.emplacementService.getEmplacements().subscribe(
   //   emplacements => this.emplacements = emplacements,
   //   error => this.errorMessage = <any>error);
  }

}