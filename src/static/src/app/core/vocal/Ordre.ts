import { Mapping } from './Mapping'
import { TextToSpeech } from './TextToSpeech'

export class Ordre {

    public id: string;
    public key_ordre: string;
    public module: string;
    public type:string;
    public active:boolean = true;
    public actions:Array<Mapping> =[];
    public mappings_messages:Array<Mapping>=[];
    public mappings_inputs:Array<Mapping>=[];
    public mappings_repete:Array<Mapping>=[];
    public textToSpeech:Array<TextToSpeech>=[];
    public input_time:number = 0;
    public repete_time:number = 0;
    
    public isModified:boolean = false;
    public toDelete:boolean = false;
    
    constructor() { }
}