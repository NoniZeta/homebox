import { Injectable }     from '@angular/core';
import { Http, Response, Headers, RequestOptions} from '@angular/http';
import { Observable }     from 'rxjs/Observable';

import { JsonPost }          from '../../common/model/JsonPost';
import { CustomHttpService } from '../../common/service/customHttp.service';

import { Word } from './dictionnaire/Word';
import { Ordre } from './Ordre';

@Injectable()
export class VocalService extends CustomHttpService{

    constructor (http: Http) {
        super(http);
    }

    public getWords (): Observable<Word[]> {
        return this.post("modelVocalService", "findAllWords");
    }

    public save (words:Array<Word>): Observable<any> {
        return this.post("modelVocalService", "saveWords", words);
    }

    public delete (id:string): Observable<any> {
        return this.post("modelVocalService", "deleteWords", [id]);
    }

    public createDic (): Observable<any> {
        return this.post("modelVocalService", "createDic");
    }

    public suggestion (word:string): Observable<any> {
        return this.post("modelVocalService", "suggestionWords", [word]);
    }

    public getActions (): Observable<Ordre[]> {
        return this.post("modelVocalService", "findActions");
    }

    public getOrdres (): Observable<Ordre[]> {
        return this.post("modelVocalService", "findOrdres");
    }

    public getNumeric (): Observable<Ordre[]> {
        return this.post("modelVocalService", "findNumeric");
    }

    /*mappingNane = @nameserie, @nameflim */
    public getMapping (mappingName:string): Observable<Ordre[]> {
        return this.post("modelVocalService", "findMapping", [mappingName]);
    }

    public saveOrdres (items:Array<Ordre>): Observable<any> {
        return this.post("modelVocalService", "saveOrdres", items);
    }

    public deleteOrdre (item:Ordre): Observable<any> {
        return this.post("modelVocalService", "deleteOrdre", [item]);
    }

}