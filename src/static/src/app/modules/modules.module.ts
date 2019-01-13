import { NgModule }       from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';

import { ModulesRoutingModule } from './modules-routing.module';

import { KodiComponent }  from './kodi/kodi.component';
import { Telecommande }  from './kodi/telecommande/telecommande.component';
import { SerieComponent }  from './kodi/serie/serie.component';
import { FilmComponent }  from './kodi/film/film.component';
import { EnCoursComponent }  from './kodi/serie/encours/encours.component';
import { ListeComponent }  from './kodi/serie/liste/liste.component';
import { ListeFilmsComponent }  from './kodi/film/liste/liste.component';
import { MappingComponent }  from './kodi/serie/mapping/mapping.component';
import { MusiqueKodiComponent } from './kodi/musique/musique.component';
import { ListeMusiquesComponent }  from './kodi/musique/liste/liste.component';

import { CourseComponent }     from './courses/courses.component';
import { Ng2CompleterModule } from '../common/autocomplete/ng2-completer.module';
import { FormsModule } from '@angular/forms';
import { DataTableModule } from '../common/datatable/datatable.module';
import { ModalModule } from '../common/modal/modal.module';
import { SerieFilterPipe } from './kodi/serie/mapping/serie-filter.pipe';
import { FilmFilterPipe } from './kodi/film/mapping/film-filter.pipe';
import { FilmMappingComponent } from './kodi/film/mapping/mapping.component';
import { BebepazComponent } from './bebepaz/bebepaz.component';
import { MusiqueComponent } from './musique/musique.component';


@NgModule({
  imports: [
    BrowserModule, ModulesRoutingModule, Ng2CompleterModule, FormsModule, DataTableModule, ModalModule
  ],
  declarations: [
    KodiComponent, Telecommande, SerieComponent, EnCoursComponent, ListeComponent, MappingComponent, FilmComponent, ListeFilmsComponent, 
    MusiqueKodiComponent, ListeMusiquesComponent, CourseComponent, SerieFilterPipe, FilmFilterPipe,
    FilmMappingComponent, BebepazComponent, MusiqueComponent
  ]
})
export class ModulesModule {


}
