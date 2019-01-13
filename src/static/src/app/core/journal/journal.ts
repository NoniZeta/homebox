import { Component, OnInit } from '@angular/core';
import { WebSocketService } from '../../common/service/websocket.service';
import { Ordre } from '../vocal/Ordre';
import { Mapping } from '../vocal/Mapping';
import { ToastsManager } from 'ng2-toastr/ng2-toastr';

export class VocalDetection {
    actions: Array<Ordre> = [];
    //ordres: Array<Ordre> = [];
    messages: Array<Mapping> = [];
    inputs: Array<Mapping> = [];
    variables: Array<Ordre> = [];
}

export class OrdreDetected {
    ordre: Ordre;
    input: string;
    variables: Array<string> = [];
}

export class DecodedWords {
    bestResult: string;
    others_words: Array<string> = [];
}


@Component({
    templateUrl: "./journal.html",
    providers: [],
    styleUrls: [
        'journal.scss'
    ],

})
export class JournalComponent implements OnInit {

    errorMessage: string;
    vocalDetection: VocalDetection;
    ordreDetected: OrdreDetected;
    decodedWords: DecodedWords = new DecodedWords();
    journal: Array<string> = []

    constructor(private wvService: WebSocketService, public toastr: ToastsManager) { 
        this.wvService.connect("ordreDetected").subscribe((item: OrdreDetected) => {
//            console.log(item);
            this.ordreDetected = item;
            if(this.ordreDetected && this.ordreDetected.ordre && this.ordreDetected.ordre.key_ordre){
                this.toastr.info(this.ordreDetected.ordre.key_ordre, 'OrdreDetected ordre');
            }
            if(this.ordreDetected && this.ordreDetected.input){
                 for (let element of Object.keys(this.ordreDetected.input)) {
                    this.toastr.info(element, 'OrdreDetected input');
                    
                    for (let item of this.ordreDetected.input[element]) {
                      //  let value = Object.keys(this.ordreDetected.input)[item]
                        this.toastr.info(item.key_ordre, 'OrdreDetected Variable');
                    }    
                 }     
            }
        });
        this.wvService.connect("vocalDetection").subscribe((item: VocalDetection) => {
            this.vocalDetection = item;
//            console.log(this.vocalDetection);
        });
        this.wvService.connect("decodedWords").subscribe((item: DecodedWords) => {
            this.decodedWords = item;
//            console.log(this.vocalDetection);
        });
//        this.wvService.connect("monitoringVocalService").subscribe((item: string) => {
 //           this.journal.unshift(item);
 //       });

    }

    ngOnInit() {
    };

}