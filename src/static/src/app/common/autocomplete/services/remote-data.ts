import { Http, Response, Headers, RequestOptions } from '@angular/http';
import { Subscription } from "rxjs/Subscription";
import "rxjs/add/operator/map";
import "rxjs/add/operator/catch";


import { CompleterBaseData } from "./completer-base-data";
import { Observable } from 'rxjs/Observable';
import { JsonPost } from '../../model/JsonPost';
import { Item } from './Item';

export class RemoteData extends CompleterBaseData {
    private _remoteUrl: string;
    private _module: string;
    private _method: string;
    private remoteSearch: Subscription;
    private _urlFormater: (term: string) => string = null;
    private _dataField: string = null;
    private _headers: Headers;


    constructor(private http: Http) {
        super();
    }

    public remoteUrl(remoteUrl: string) {
        this._remoteUrl = remoteUrl;
        return this;
    }

    public module(module: string) {
        this._module = module;
        return this;
    }

    public method(method: string) {
        this._method = method;
        return this;
    }

    public urlFormater(urlFormater: (term: string) => string) {
        this._urlFormater = urlFormater;
    }

    public dataField(dataField: string) {
        this._dataField = dataField;
    }

    public headers(headers: Headers) {
        this._headers = headers;
    }

    public search(term: string): void {
        this.cancel();
        // let params = {};
        let url = "";
        if (this._urlFormater) {
            url = this._urlFormater(term);
        } else {
            url = this._remoteUrl + encodeURIComponent(term);
        }

        this.remoteSearch = this.post(this._module, this._method)
            .map((res: Response) => res.json())
            .map((data: any) => {
               /* let items: Array<Item> = [];
                for (let element in data) {
                    let item = new Item();
                    item.title = element;
                    items.push(item);
                }*/

                let matchaes = this.extractValue(data, this._dataField);
                return this.extractMatches(matchaes, term);
            })
            .map(
            (matches: any[]) => {
                let results = this.processResults(matches);
                this.next(results);
                return results;
            })
            .catch((err) => {
                this.error(err);
                return null;
            })
            .subscribe();
    }

    public cancel() {
        if (this.remoteSearch) {
            this.remoteSearch.unsubscribe();
        }
    }
    
    protected post (module:string, method:string, parameters?:Array<any>): Observable<any> {
        let headers = new Headers({ 'Content-Type': 'application/json' });
        let options = new RequestOptions({ headers: headers });
        let data = new JsonPost(module, method);
        data.parameters = parameters || [];
        return this.http.post('http://'+ window.location.hostname + ':7002/jsonMessage', JSON.stringify(data), options)
    }

}