import { Injectable }     from '@angular/core';
import { Http, Response, Headers, RequestOptions} from '@angular/http';
import { Observable }     from 'rxjs/Observable';

import { JsonPost }           from '../../common/model/JsonPost';
import { Emplacement }    from './Emplacement';

import { CustomHttpService } from '../../common/service/customHttp.service';

@Injectable()
export class EmplacementService extends CustomHttpService{

    constructor (http: Http) {
        super(http);
    }

    public getEmplacements (): Observable<Emplacement[]> {
        return this.post("emplacementsService", "loadEmplacements");
    }

    public save (obj:Emplacement): Observable<any> {
        return this.post("emplacementsService", "insertOrUpdateEmplacements", [obj]);
    }

    public delete (ids:Array<string>): Observable<any> {
        return this.post("emplacementsService", "deleteEmplacements", ids);
    }

    public saveDevicesByEmplacement (obj:Emplacement): Observable<any> {
        return this.post("emplacementsService", "saveDevicesByEmplacement", [obj]);
    }

}