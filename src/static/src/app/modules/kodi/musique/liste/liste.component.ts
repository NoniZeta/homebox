import { Component, Input, OnInit } from '@angular/core';
import { WebSocketService } from '../../../../common/service/websocket.service';
import {KodiService} from '../../kodi.service';
import {Artiste} from '../Artiste';
import {Album}  from '../Album';
import {Musique}   from '../Musique';

import { ObjectConnected }    from '../../../../core/objects-connected/ObjectConnected';

interface BreadcrumbObj {
  title: string;
  list: Array<any>;
  type:string;
}

@Component({
  selector: 'liste',
  templateUrl: "./liste.html",
  styleUrls: ['liste.scss'],
  providers: [WebSocketService, KodiService],
})
export class ListeMusiquesComponent implements OnInit {

  private errorMessage: string;
  private musiques;
  private itemsArtist: Array<Artiste>;
  private itemsAlbum: Array<Album>;
  private itemsMusic: Array<any>;
  private isDiplaying:string = "artiste";
  private breadcrumbList: BreadcrumbObj[] = [{title:"Artistes", list:this.itemsArtist, type:'artiste'}];
  private deviceConnected: ObjectConnected;

  constructor(private kodiService: KodiService, private wvService: WebSocketService) { }

  ngOnInit() {

    this.kodiService.detectKodi().subscribe(
      kodiDevices => this.deviceConnected = kodiDevices[0],
      error => this.errorMessage = <any>error);

    this.kodiService.loadMusiques().subscribe(
      items => {
        this.musiques = items;
        this.itemsArtist = this.transformArtistes(items);
      },
      error => this.errorMessage = <any>error);
    this.wvService.connect("kodiService").subscribe(obj => {
      if (obj.key === 'loadMusiques') {
        this.musiques = obj.musiques;
        this.itemsArtist = this.transformArtistes(obj.musiques);
      }
      if (obj.key === 'kodiDetected') {
        this.deviceConnected = obj.devices[0];
      }
    });
  }

  public open(artiste: Artiste) {
    this.breadcrumbList.push({title:artiste.name, list:this.itemsAlbum, type:'album'});
    let albums = this.musiques[artiste.name];
    this.isDiplaying ='album';
    //this.itemsSerie = undefined;
    this.itemsAlbum = this.transformAlbum(artiste.name, albums);
  }

  public openAlbum(album: Album) {
    this.breadcrumbList.push({title:album.name, list:this.itemsMusic, type:'music'});
    let musics = this.musiques[album.artist][album.name];
    //this.itemsSaison = undefined;
    this.isDiplaying ='music';
    this.itemsMusic = this.transformMusic(musics);
  }

  public openEpisode(music) {
    let data: any[] = [{ 'ip': this.deviceConnected.ip, 'ordre': 'openMusic', 'arguments': music.id }]
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

  private transformArtistes(artistesToTransform) {
    let items: Array<Artiste> = [];
    for (let element in artistesToTransform) {
      let item = new Artiste();
      item.name = element;
      items.push(item);
    }
    return items
  }

  private transformAlbum(nameArtiste, itemsToTransform) {
    let items: Array<Album> = [];
    for (let element in itemsToTransform) {
      let item = new Album();
      item.artist = nameArtiste;
      item.name = element;
      items.push(item);
    }
    return items
  }

  private transformMusic(itemsToTransform) {
    let items: Array<any> = [];
    for (let element in itemsToTransform) {
      items.push(itemsToTransform[element]);
    }
    return items;
  }

}