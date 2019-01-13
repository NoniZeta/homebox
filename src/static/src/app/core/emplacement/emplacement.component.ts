import { Component, OnInit, ViewEncapsulation } from '@angular/core';

import { EmplacementService } from './emplacement.service';

import { Emplacement }           from './Emplacement';

import { Modal } from '../../common/modal/modal.component';

@Component({
  templateUrl:"./emplacement.html",
  providers: [EmplacementService],
  styleUrls:[
    'emplacement.scss'
  ],
 
})
export class EmplacementComponent implements OnInit { 
  
    emplacements: Emplacement[];
    errorMessage: string;
    _modal = null;
    item:Emplacement;
    name:string;

  constructor(private emplacementService: EmplacementService) { }

  ngOnInit() { this.getEmplacements(); }

  getEmplacements() {
    this.emplacementService.getEmplacements().subscribe(
      emplacements => this.emplacements = emplacements,
      error => this.errorMessage = <any>error);
  }

  bindModal(modal) {this._modal=modal;}

    add(client) {
         this.item = new Emplacement();
         this._modal.open();
    }

    delete(){
        var ids:Array<string> = []; 
        for (let item_ of this.emplacements){
            if (item_.toDelete === true)  {
                ids.push(item_.id);
            }
        }
        this.emplacementService.delete(ids).subscribe(
            () => this.getEmplacements(),
            error => this.errorMessage = <any>error
        );
  }


    edit(client){
        this.item = client;
        this.name = this.item.name;
        this._modal.open();
    }

    detail(client){
        this.item = client;
    }


    save(){
        this.item.name = this.name;
        this.emplacementService.save(this.item).subscribe(
            emplacements => {
                this.getEmplacements();
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
}