import { Injectable }     from '@angular/core';
import { Http, Response, Headers, RequestOptions} from '@angular/http';
import { Observable }     from 'rxjs/Observable';

import { JsonPost }           from '../../common/model/JsonPost';

import { CustomHttpService } from '../../common/service/customHttp.service';

@Injectable()
export class KodiService extends CustomHttpService{

    constructor (http: Http) {
        super(http);
    }

    public detectKodi () {
        return this.post("kodi", "detectKodi");
    }

    public ordre (parameters:any[]) {
        return this.post("kodi", "kodiCommand", parameters);
    }

    public loadSeries () {
        return this.post("kodi", "loadSeries");
    }

    public loadFilms () {
        return this.post("kodi", "loadFilms");
    }
    
    public loadMusiques () {
        return this.post("kodi", "loadMusiques");
    }

    public scanVideo () {
        return this.post("kodi", "scanMoviesDatabase");
    }

    public scanMusic () {
        return this.post("kodi", "scanMusiquesDatabase");
    }

    public showNotification () {
        return this.post("kodi", "showNotification");
    }

}