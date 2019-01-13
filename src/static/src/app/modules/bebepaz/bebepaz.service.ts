import { Injectable } from '@angular/core';
import { CustomHttpService } from '../../common/service/customHttp.service';
import { Http } from '@angular/http';
import { Observable } from 'rxjs/Observable';

@Injectable()
export class BebepazService extends CustomHttpService {

    constructor (http: Http) {
        super(http);
    }

//    public getVideoStream(): Observable<any>{
//        return this.http.get("http://127.0.0.1:7002/mjpeg_stream");
//    }

    public isCameraActive (): Observable<boolean> {
        return this.post('bebepaz', 'isCameraActive');
    }

    public stopCamera (): Observable<boolean> {
        return this.post('bebepaz', 'stopCamera');
    }

    public startCamera (): Observable<boolean> {
        return this.post('bebepaz', 'startCamera');
    }

    public stopMusic (): Observable<boolean> {
        return this.post('musicplayer', 'stopMusic');
    }

    public startMusic (): Observable<boolean> {
        return this.post('musicplayer', 'startMusic', ['bebeList']);
    }

}