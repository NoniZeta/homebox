import { Injectable }     from '@angular/core';
import { Http, Response, Headers, RequestOptions} from '@angular/http';
import { Observable }     from 'rxjs/Observable';
import { JsonPost }       from '../model/JsonPost';

@Injectable()
export class CustomHttpService {

    protected http: Http;

    constructor (http: Http) {
        this.http = http;
    }

    protected post (module:string, method:string, parameters?:Array<any>): Observable<any> {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ headers: headers });
        let data = new JsonPost(module, method);
        data.parameters = parameters || [];
        return this.http.post('http://'+ window.location.hostname + ':7002/jsonMessage', JSON.stringify(data), options)
                        .map(this.extractData)
                        .catch(this.handleError);
    }

    private extractData(res: Response) {
        let body = res.json();
        return body || { };
    }

    private handleError (error: Response | any) {
        // In a real world app, we might use a remote logging infrastructure
        let errMsg: string;
        if (error instanceof Response) {
            const body = error.json() || '';
            const err = body.error || JSON.stringify(body);
            errMsg = `${error.status}  => ${err}`;
        } else {
            errMsg = error.message ? error.message : error.toString();
        }
        console.log(errMsg);
        return Observable.throw(errMsg);
    }

}