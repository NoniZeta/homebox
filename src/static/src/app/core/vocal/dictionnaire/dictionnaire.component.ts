import { Component, Input, OnInit } from '@angular/core';

import { VocalService }              from '../vocal.service';

import {Word}  from "./Word";
import {Prononciation}  from "./Prononciation";
import { uniqueId } from '../../../common/modal/modal.component';

@Component({
  selector: 'dictionnaire',
  templateUrl:"./dictionnaire.html",
  providers: [VocalService],
  styleUrls:['dictionnaire.scss']
})
export class DictionnaireComponent implements OnInit {

    private errorMessage: string;
    public data:Array<Word>;
    public wordSelected:Word = new Word();
    public filterQuery = "";
    public rowsOnPage = 100;
    public sortBy = "word";
    public sortOrder = "asc";
    public newGrapheme;
    public newLocale = "fr";
    public isNewWord:boolean = false;
    public isModifiedFilter:boolean = false;
    _modal = null;


    constructor(private service: VocalService) {}

    ngOnInit(): void { this.getWords() }

    public getWords(){
       this.service.getWords()
            .subscribe( 
                data => { 
                        this.data = data;
                } 
            );
    }        

    bindModal(modal) {this._modal=modal;}

    public toInt(num: string) {
        return +num;
    }

    public edit(item:Word){
        this.isNewWord = false
        this.wordSelected = item;
        this._modal.open();
    }

    close() {
        this._modal.close();
    }

    delete(item) {
        let index:number = this.wordSelected.vocal.indexOf(item); 
        this.wordSelected.vocal.splice(index, 1);
    }

    addWord() {
        this.isNewWord = true
        this.wordSelected = new Word();
        this._modal.open();
    }    

    add() {
        let prononciation:Prononciation = new Prononciation();
        prononciation.grapheme = this.newGrapheme;
        prononciation.local = this.newLocale;
        this.wordSelected.vocal.push(prononciation);
        this.newGrapheme = '';
        this.newLocale = 'Fr';
    }

    save() {
        this.wordSelected.isModified = true;
        if (this.isNewWord){
            this.data.push(this.wordSelected);
        }
        this.close();
    } 

    saveWords() {
        let wordsToSave = this.data.filter(word => word.isModified || !word.id);
        this.service.save(wordsToSave).subscribe(
                () => {
                this.getWords();
                this.isModifiedFilter = false;
            },
                error => this.errorMessage = <any>error 
            );
    } 

    deleteWord(item){
        this.service.delete(item.id).subscribe(
                () => {
                this.getWords();
                this.isModifiedFilter = false;
            },
                error => this.errorMessage = <any>error 
            );
    }

    createDic() {
        this.service.createDic().subscribe(
                () => this.getWords(),
                error => this.errorMessage = <any>error 
            );
    } 

    suggestion(){
        this.service.suggestion(this.wordSelected.word).subscribe(
                data => {
                  this.wordSelected.vocal = data
                }, 
                error => this.errorMessage = <any>error 
            );
    }


 }