import { Prononciation } from './Prononciation';

export class Word {

    public id: string;
    public word: string;
    public local: string;
    public vocal:Array<Prononciation>  = new Array();
    public active:boolean;
    public toDelete:boolean = false;
    public isModified:boolean = false;
    public isPresent:boolean;
    
    constructor() { }
}