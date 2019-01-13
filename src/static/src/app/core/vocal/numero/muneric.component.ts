import { Component, Input, OnInit } from '@angular/core';

import { VocalService } from '../vocal.service';
import { Ordre } from '../Ordre';
import { Mapping } from '../Mapping';

@Component({
    selector: 'numeric',
    templateUrl: "./numeric.html",
    providers: [VocalService],
    styleUrls: ['numeric.scss']
})
export class NumericComponent implements OnInit {

    private errorMessage: string;
    private data: Array<Ordre>;

    public ordreSelected: Ordre = new Ordre();
    public filterQuery = "";
    public rowsOnPage = 20;
    public sortBy = "key_ordre";
    public sortOrder = "asc";
    public newKeyVocal;
    public newLocale = "fr";
    public isNewOrdre: boolean = false;
    _modal = null;


    constructor(private service: VocalService) { }

    ngOnInit() {
        this.getNumeric();
    }

    getNumeric() {
        this.service.getNumeric().subscribe(
            actions => {
                this.data = actions
            },
            error => this.errorMessage = <any>error);
    }

    bindModal(modal) { this._modal = modal; }

    public toInt(num: string) {
        return +num;
    }

    public edit(item: Ordre) {
        this.isNewOrdre = false
        this.ordreSelected = item;
        this._modal.open();
    }

    close() {
        this._modal.close();
    }

    delete(item) {
        let index: number = this.ordreSelected.mappings_messages.indexOf(item);
        this.ordreSelected.mappings_messages.splice(index, 1);
    }

    addOrdre() {
        this.isNewOrdre = true
        this.ordreSelected = new Ordre();
        this.ordreSelected.module = 'core';
        this.ordreSelected.type = 'numeric';
        this._modal.open();
    }

    add() {
        let mapping: Mapping = new Mapping();
        mapping.key_vocal = this.newKeyVocal;
        mapping.local = this.newLocale;
        mapping.type = "numeric";
        this.ordreSelected.mappings_messages.push(mapping);
        this.newKeyVocal = '';
        this.newLocale = 'Fr';
    }

    save() {
        this.ordreSelected.isModified = true;
        if (this.isNewOrdre) {
            this.data.push(this.ordreSelected);
        }
        this.close();
    }

    saveOrdres() {
        let itemsToSave = this.data.filter(item => item.isModified || !item.id);
            /*.map(item => {
                item.mappings_messages.map(mapping => {
                    //mapping.id_ordre = item.key_ordre;
                });
                return item;
            });*/
        this.service.saveOrdres(itemsToSave).subscribe(
            () => this.getNumeric(),
            error => this.errorMessage = <any>error
        );
    }

}