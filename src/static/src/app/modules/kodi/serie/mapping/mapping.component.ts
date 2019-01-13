import { Component, Input, OnInit } from '@angular/core';
import { WebSocketService } from '../../../../common/service/websocket.service';
import { Ordre } from '../../../../core/vocal/Ordre';
import { Mapping } from '../../../../core/vocal/Mapping';
import { VocalService } from '../../../../core/vocal/vocal.service';
import { KodiService } from '../../kodi.service';
import { Serie } from '../Serie';
import { CompleterService, CompleterData } from '../../../../common/autocomplete';


@Component({
  selector: 'mapping',
  templateUrl: "./mapping.html",
  styleUrls: ['mapping.scss'],
  providers: [WebSocketService, VocalService, KodiService],
})
export class MappingComponent implements OnInit {

  private errorMessage: string;
  private searchStr: string;
  private dataService: CompleterData;
  private seriesName = [];
  private data: Array<Ordre>;
  private _modal = null;

  public ordreSelected: Ordre = new Ordre();
  public filterQuery = "";
  public rowsOnPage = 20;
  public sortBy = "key_ordre";
  public sortOrder = "asc";
  public newKeyVocal;
  public newLocale = "fr";
  public isNewOrdre: boolean = false;

  constructor(private service: VocalService,private completerService: CompleterService, private kodiService:KodiService) {
    this.dataService = completerService.remote("http://localhost:7002/jsonMessage",  "kodi" ,"loadSeriesTab", 'title', 'title');
  }

  public ngOnInit() {
    this.getSeriesMapping();
  }

/*  public getSeries() {
    this.kodiService.loadSeries().subscribe(
      items => {
        this.seriesName = this.transformSerie(items);
      },
      error => this.errorMessage = <any>error);
  }
*/
/*  private transformSerie(seriesToTransform) {
    let series: Array<Serie> = [];
    for (let element in seriesToTransform) {
      let serie = new Serie();
      serie.title = element;
      series.push(serie);
    }
    return series
  }
*/
 getSeriesMapping() {
    this.service.getMapping('name_serie').subscribe(
      items => {
        this.data = items
      },
      error => this.errorMessage = <any>error);
  }

  bindModal(modal) { this._modal = modal; }

  public toInt(num: string) {
    return +num;
  }

  public edit(item: Ordre) {
    this.isNewOrdre = false
    this.ordreSelected = item;
    this._modal.open();
  }

  close() {
    this._modal.close();
  }

  delete(item) {
    let index: number = this.ordreSelected.mappings_messages.indexOf(item);
    this.ordreSelected.mappings_messages.splice(index, 1);
  }

  addOrdre() {
    this.isNewOrdre = true
    this.ordreSelected = new Ordre();
    this._modal.open();
  }

  add() {
    let mapping: Mapping = new Mapping();
    mapping.key_vocal = this.newKeyVocal;
    mapping.local = this.newLocale;
    this.ordreSelected.mappings_messages.push(mapping);
    this.newKeyVocal = '';
    this.newLocale = 'Fr';
  }

  save() {
    this.ordreSelected.isModified = true;
    if (this.isNewOrdre) {
      this.data.push(this.ordreSelected);
    }
    this.close();
  }

  saveOrdres() {
    let itemsToSave = this.data.filter(item => item.isModified || !item.id)
      .map(item => {
        item.module = "kodi";
        item.type = "name_serie";
        item.active = true;
        item.mappings_messages.map(mapping => {
         // mapping.id_ordre = item.key_ordre;
          mapping.type = "name_serie";
        });
        return item;
      });
    this.service.saveOrdres(itemsToSave).subscribe(
      () => this.getSeriesMapping(),
      error => this.errorMessage = <any>error
    );
  }

}