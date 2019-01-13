import { Injectable }     from '@angular/core';
import { Http, Response, Headers, RequestOptions} from '@angular/http';
import { Observable }     from 'rxjs/Observable';

import { JsonPost }           from '../../common/model/JsonPost';
import { ObjectConnected }    from './ObjectConnected';

import { CustomHttpService } from '../../common/service/customHttp.service';

@Injectable()
export class ObjectConnectedService extends CustomHttpService{

    constructor (http: Http) {
        super(http);
    }

    public getObjectsConnected (): Observable<ObjectConnected[]> {
        return this.post("devicesService", "loadDevives");
    }


    public save (obj:ObjectConnected): Observable<any> {
        return this.post("devicesService", "saveDevives", [obj]);
    }

    public scanNetwork(): Observable<any> {
        return this.post("devicesService", "scan");
    }

}