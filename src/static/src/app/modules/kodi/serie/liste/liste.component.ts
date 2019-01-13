import { Component, Input, OnInit } from '@angular/core';
import { WebSocketService } from '../../../../common/service/websocket.service';
import {KodiService} from '../../kodi.service';
import {Episode} from '../Episode';
import {Saison}  from '../Saison';
import {Serie}   from '../Serie';

import { ObjectConnected }    from '../../../../core/objects-connected/ObjectConnected';

interface BreadcrumbObj {
  title: string;
  list: Array<any>;
  type:string;
  active?:boolean;
}

@Component({
  selector: 'liste',
  templateUrl: "./liste.html",
  styleUrls: ['liste.scss'],
  providers: [WebSocketService, KodiService],
})
export class ListeComponent implements OnInit {

  private errorMessage: string;
  private series;
  private itemsSerie: Array<Serie>;
  private itemsSaison: Array<Saison>;
  private itemsEpisode: Array<any>;
  private isDiplaying:string = "serie";
  private breadcrumbList: BreadcrumbObj[] = [{title:"Séries", list:this.itemsSerie, type:'serie'}];
  private deviceConnected: ObjectConnected;

  constructor(private kodiService: KodiService, private wvService: WebSocketService) { }

  ngOnInit() {

    this.kodiService.detectKodi().subscribe(
      kodiDevices => this.deviceConnected = kodiDevices[0],
      error => this.errorMessage = <any>error);

    this.kodiService.loadSeries().subscribe(
      items => {
        this.series = items;
        this.itemsSerie = this.transformSerie(items);
      },
      error => this.errorMessage = <any>error);
    this.wvService.connect("kodiService").subscribe(obj => {
      if (obj.key === 'loadSeries') {
        this.series = obj.series;
        this.itemsSerie = this.transformSerie(obj.series);
      }
      if (obj.key === 'kodiDetected') {
        this.deviceConnected = obj.devices[0];
      }
    });
  }

  public open(nameSerie: Serie) {
    this.breadcrumbList.push({title:nameSerie.title, list:this.itemsSaison, type:'saison'});
    let serie = this.series[nameSerie.title];
    this.isDiplaying ='saison';
    //this.itemsSerie = undefined;
    this.itemsSaison = this.transformSaison(nameSerie.title, serie);
  }

  public openSaison(saison: Saison) {
    this.breadcrumbList.push({title:saison.saison, list:this.itemsEpisode, type:'episode'});
    let episodes = this.series[saison.serie][saison.saison];
    //this.itemsSaison = undefined;
    this.isDiplaying ='episode';
    this.itemsEpisode = this.transformEpisode(episodes);
  }

  public openEpisode(episode) {
    let data: any[] = [{ 'ip': this.deviceConnected.ip, 'ordre': 'openSerie', 'arguments': episode.id }]
    this.kodiService.ordre(data).subscribe(
      data => console.log(data),
      error => this.errorMessage = <any>error);
  }

  public openBreadCrumb(item:BreadcrumbObj){
      this.isDiplaying = item.type;
      let index = this.breadcrumbList.indexOf(item) + 1;
      let nbToDelete =  this.breadcrumbList.length - index;
      this.breadcrumbList.splice(index, nbToDelete);
  }

  private transformSerie(seriesToTransform) {
    let series: Array<Serie> = [];
    for (let element in seriesToTransform) {
      let serie = new Serie();
      serie.title = element;
      series.push(serie);
    }
    return series
  }

  private transformSaison(nameSerie, itemsToTransform) {
    let items: Array<Saison> = [];
    for (let element in itemsToTransform) {
      let item = new Saison();
      item.serie = nameSerie;
      item.saison = element;
      items.push(item);
    }
    return items
  }

  private transformEpisode(itemsToTransform) {
    let items: Array<any> = [];
    for (let element in itemsToTransform) {
      items.push(itemsToTransform[element]);
    }
    return items;
  }

}