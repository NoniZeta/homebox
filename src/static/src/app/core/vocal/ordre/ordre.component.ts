import { Component, Input, OnInit } from '@angular/core';

import { VocalService }             from '../vocal.service';
import { Ordre }                    from '../Ordre';
import { Mapping }                  from '../Mapping';

@Component({
  selector: 'ordre',
  templateUrl:"./ordre.html",
  providers: [VocalService],
  styleUrls:['ordre.scss']
})
export class OrdreComponent implements OnInit {

    private errorMessage: string;
    private data:Array<Ordre>;
    private actions:Array<Ordre>;

    public ordreSelected:Ordre = new Ordre();
    public filterQuery = "";
    public rowsOnPage = 20;
    public sortBy = "key_ordre";
    public sortOrder = "asc";
    public newKeyVocal;
    public newActionKeyVocal;
    public newInputKeyVocal;
    public newRepeteKeyVocal;
    public newLocale = "fr";
    public newInputLocale = "fr";
    public newRepeteLocale = "fr";
    public isNewOrdre:boolean = false;
    _modal = null;


    constructor(private service: VocalService) {}

    ngOnInit() { 
      this.getOrdres();
    }

    getOrdres() {
      this.service.getOrdres().subscribe(
        items => {
          this.data = items;
          this.getActions();
        },
        error => this.errorMessage = <any>error);
    }

    getActions() {
        this.service.getActions().subscribe(
            actions => {
                this.actions = actions
            },
            error => this.errorMessage = <any>error);
    }


     bindModal(modal) {this._modal=modal;}

    public toInt(num: string) {
        return +num;
    }

    public edit(item:Ordre){
        this.isNewOrdre = false
        this.ordreSelected = item;
        this._modal.open();
    }

    public deleteOrdre(item:Ordre){
        this.service.deleteOrdre(item).subscribe(
                () => this.getOrdres(),
                error => this.errorMessage = <any>error 
            );
    }

    close() {
        this._modal.close();
    }

    delete(item) {
        let index:number = this.ordreSelected.mappings_messages.indexOf(item); 
        this.ordreSelected.mappings_messages.splice(index, 1);
    }

    deleteActions(item) {
        let index:number = this.ordreSelected.actions.indexOf(item); 
        this.ordreSelected.actions.splice(index, 1);
    }

    deleteInput(item) {
        let index:number = this.ordreSelected.mappings_inputs.indexOf(item); 
        this.ordreSelected.mappings_inputs.splice(index, 1);
    }

    deleteRepete(item) {
        let index:number = this.ordreSelected.mappings_repete.indexOf(item); 
        this.ordreSelected.mappings_repete.splice(index, 1);
    }

    addOrdre() {
        this.isNewOrdre = true
        this.ordreSelected = new Ordre();
        this.ordreSelected.module = 'core';
        this.ordreSelected.type = 'ordre';
        this._modal.open();
    }    

    add() {
        let mapping:Mapping = new Mapping();
        mapping.key_vocal = this.newKeyVocal;
        mapping.local = this.newLocale;
        mapping.type = "message";
        this.ordreSelected.mappings_messages.push(mapping);
        this.newKeyVocal = '';
        this.newLocale = 'Fr';
    }

    addAction() {
        let mapping:Mapping = new Mapping();
        mapping.key_vocal = this.newActionKeyVocal;
        mapping.local = "fr";
        mapping.type = "action";
        this.ordreSelected.actions.push(mapping);
        this.newActionKeyVocal = '';
    }

    addInput() {
        let mapping:Mapping = new Mapping();
        mapping.key_vocal = this.newInputKeyVocal;
        mapping.local = this.newInputLocale;
        mapping.type = "input";
        this.ordreSelected.mappings_inputs.push(mapping);
        this.newInputKeyVocal = '';
        this.newInputLocale = 'Fr';
    }

    addRepete() {
        let mapping:Mapping = new Mapping();
        mapping.key_vocal = this.newRepeteKeyVocal;
        mapping.local = this.newRepeteLocale;
        mapping.type = "repete";
        this.ordreSelected.mappings_repete.push(mapping);
        this.newRepeteKeyVocal = '';
        this.newRepeteLocale = 'Fr';
    }

    save() {
        this.ordreSelected.isModified = true;
        if (this.isNewOrdre){
            this.data.push(this.ordreSelected);
        }
        this.close();
    } 

    saveOrdres() {
        let itemsToSave = this.data.filter(item => item.isModified || !item.id);
/*                                    .map(item =>{
                                        item.mappings_messages.map( mapping => {
                                            mapping.id_ordre = item.key_ordre;
                                        });
                                        return item;
                                    });*/
        this.service.saveOrdres(itemsToSave).subscribe(
                () => this.getOrdres(),
                error => this.errorMessage = <any>error 
            );
    } 

 }