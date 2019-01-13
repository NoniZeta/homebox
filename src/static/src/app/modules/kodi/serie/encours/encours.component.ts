import { Component, Input, OnInit } from '@angular/core';
import { WebSocketService }         from '../../../../common/service/websocket.service';
import { KodiService}               from '../../kodi.service';
import { ObjectConnected }          from '../../../../core/objects-connected/ObjectConnected';


@Component({
  selector: 'encours',
  templateUrl:"./encours.html",
  styleUrls:['encours.scss'],
  providers: [WebSocketService, KodiService],
})
export class EnCoursComponent implements OnInit {

    private errorMessage: string;
    private itemsLastPlayed: Array<any>;
    private series;
    private deviceConnected: ObjectConnected;

    constructor(private kodiService: KodiService, private wvService: WebSocketService) {}

    ngOnInit() {
      this.kodiService.detectKodi().subscribe(
        kodiDevices => this.deviceConnected = kodiDevices[0],
        error => this.errorMessage = <any>error);
      this.kodiService.loadSeries().subscribe(
        items => this.series = items,
        error => this.errorMessage = <any>error);
      this.wvService.connect("kodiService").subscribe(obj => {
        if (obj.key === 'loadSeriesEnCours') {
          this.itemsLastPlayed = obj.series;
        }
        if (obj.key === 'kodiDetected') {
          this.deviceConnected = obj.devices[0];
        }
      });
   }

  public openEpisode(episode) {
    let data: any[] = [{ 'ip': this.deviceConnected.ip, 'ordre': 'openSerie', 'arguments': episode.nextEpisodeid }]
    this.kodiService.ordre(data).subscribe(
      data => console.log(data),
      error => this.errorMessage = <any>error);
  }
}