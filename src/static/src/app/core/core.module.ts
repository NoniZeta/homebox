import {NgModule}      from '@angular/core';
import {BrowserModule} from "@angular/platform-browser";
import {FormsModule}   from "@angular/forms";
import {HttpModule}    from "@angular/http";
import {RouterModule}  from "@angular/router";

import { CoreRoutingModule } from './core-routing.module';

import { ObjectsConnectedListComponent }  from './objects-connected/objects-connected.component';
import { ObjectCOnnectedComponent }  from './objects-connected/object-connected.component';
import { EmplacementComponent }    from './emplacement/emplacement.component';
import { EmplacementSatelitesListComponent }    from './emplacement/emplacement-satelites-list';
import { VocalComponent }    from './vocal/vocal.component';
import { DictionnaireComponent }    from './vocal/dictionnaire/dictionnaire.component';
import { OrdreComponent }    from './vocal/ordre/ordre.component';
import { ActionComponent }    from './vocal/action/action.component';


import { DataTableModule } from '../common/datatable/datatable.module';
import { ModalModule } from '../common/modal/modal.module';
import { OrdreFilterPipe } from './vocal/action/ordre-filter.pipe';
import { WordFilterPipe } from './vocal/dictionnaire/word-filter.pipe';
import { NoMappingFilterPipe } from './vocal/dictionnaire/noMapping-filter.pipe';

import { TabsModule, AlertModule } from 'ng2-bootstrap';
import { JournalComponent } from './journal/journal';
import { KeysPipe } from '../common/objectFor.pipe';
import { NumericComponent } from './vocal/numero/muneric.component';
import { NumericFilterPipe } from './vocal/numero/numeric-filter';


@NgModule({
  imports: [
    BrowserModule, FormsModule, HttpModule, RouterModule, CoreRoutingModule, DataTableModule,
    ModalModule, TabsModule.forRoot(), AlertModule.forRoot()
  ],
  declarations: [
    ObjectsConnectedListComponent, ObjectCOnnectedComponent, EmplacementComponent, NumericComponent, NumericFilterPipe,
     EmplacementSatelitesListComponent, VocalComponent, DictionnaireComponent, KeysPipe,
    OrdreComponent,  ActionComponent, OrdreFilterPipe, WordFilterPipe, NoMappingFilterPipe, JournalComponent
  ]
})
export class CoreModule { }