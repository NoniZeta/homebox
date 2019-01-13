import { Injectable }     from '@angular/core';
import { Http, Response, Headers, RequestOptions} from '@angular/http';
import { Observable }     from 'rxjs/Observable';

import { JsonPost }           from '../common/model/JsonPost';

import { CustomHttpService } from '../common/service/customHttp.service';

@Injectable()
export class HomeService extends CustomHttpService {

    constructor (http: Http) {
        super(http);
    }

    public isVocalActive (): Observable<boolean> {
        return this.post('vocal', 'isVocalActive');
    }

    public stopVocal (): Observable<boolean> {
        return this.post('vocal', 'stopVocal');
    }

    public startVocal (): Observable<boolean> {
        return this.post('vocal', 'startVocal');
    }

}