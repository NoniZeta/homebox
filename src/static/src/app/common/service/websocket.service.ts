import { Subject, Observable, Observer }from 'rxjs/Rx';
import { Injectable } from '@angular/core';

@Injectable()
export class WebSocketService {

    
    
    private subject = {}//Subject<MessageEvent>;
    private protocol = "ws:";
	private host = this.protocol.concat("//").concat(window.location.hostname).concat(":7002");
	private url = this.host.concat('/').concat("ws?service=");    

    constructor() {}

    public connect(service:string): Subject<any> {
        let result: Subject<any>;
        if(!this.subject[service]) {
            this.subject[service] = this.create(this.url.concat(service));
            result = this.subject[service].map( (response: MessageEvent) => {
                return JSON.parse(response.data);
            });
        } else {
            result = this.subject[service].map( (response: MessageEvent) => {
                return JSON.parse(response.data);
            });
        }

        return result;
    }

    private create(url): Subject<MessageEvent> {
        let ws = new WebSocket(url);

        let observable = Observable.create((obs: Observer<MessageEvent>) => {
            ws.onmessage = obs.next.bind(obs);
            ws.onerror = obs.error.bind(obs);
            ws.onclose = obs.complete.bind(obs);

            return ws.close.bind(ws);
        });

        let observer = {
            next: (data: Object) => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify(data));
                }
            },
        };

        return Subject.create(observer, observable);
    }
}