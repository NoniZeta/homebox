import { Component, Input, OnInit } from '@angular/core';
import { WebSocketService }         from '../../../../common/service/websocket.service';
import { KodiService}               from '../../kodi.service';

import { ObjectConnected }    from '../../../../core/objects-connected/ObjectConnected';


@Component({
  selector: 'liste',
  templateUrl:"./liste.html",
  styleUrls:['liste.scss'],
  providers: [WebSocketService, KodiService],
})
export class ListeFilmsComponent implements OnInit {

    private deviceConnected: ObjectConnected;
    private films;
    private errorMessage: string;

    constructor(private kodiService: KodiService, private wvService: WebSocketService) {}

    ngOnInit() {
        this.kodiService.detectKodi().subscribe(
            kodiDevices => this.deviceConnected = kodiDevices[0],
            error => this.errorMessage = <any>error);

        this.kodiService.loadFilms().subscribe(
            items => {
                this.films = items;
                //this.itemsSerie = this.transformSerie(items);
            },
            error => this.errorMessage = <any>error);
        this.wvService.connect("kodiService").subscribe(obj => {
            if (obj.key === 'loadFilms') {
                this.films = obj.films;
                //this.itemsSerie = this.transformSerie(obj.series);
            }
            if (obj.key === 'kodiDetected') {
                this.deviceConnected = obj.devices[0];
            }
        });
   }

 public open(item) {
    let data: any[] = [{ 'ip': this.deviceConnected.ip, 'ordre': 'openFilm', 'arguments': item.id }]
    this.kodiService.ordre(data).subscribe(
      data => console.log(data),
      error => this.errorMessage = <any>error);
  }


}