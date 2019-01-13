import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ObjectsConnectedListComponent }    from './objects-connected/objects-connected.component';
import { EmplacementComponent }    from './emplacement/emplacement.component';
import { VocalComponent }    from './vocal/vocal.component';
import { DictionnaireComponent }    from './vocal/dictionnaire/dictionnaire.component';
import { OrdreComponent }    from './vocal/ordre/ordre.component';
import { ActionComponent }    from './vocal/action/action.component';
import { JournalComponent } from './journal/journal';
import { NumericComponent } from './vocal/numero/muneric.component';


const coreRoutes: Routes = [
  { path: 'objectsConnected',  component: ObjectsConnectedListComponent },
  { path: 'emplacements',  component: EmplacementComponent },
  { path: 'vocal',  component: VocalComponent,
       children: [
                { path: '', component: DictionnaireComponent, outlet: 'vocalRouter'  },
                { path: 'dictionnaire', component: DictionnaireComponent, outlet: 'vocalRouter'  },
                { path: 'ordres', component: OrdreComponent, outlet: 'vocalRouter'  },
                { path: 'actions', component: ActionComponent, outlet: 'vocalRouter'  },
                { path: 'numeric', component: NumericComponent, outlet: 'vocalRouter'  }
            ]},
  { path: 'journal',  component: JournalComponent },
];

@NgModule({
  imports: [
    RouterModule.forChild(coreRoutes)
  ],
  exports: [
    RouterModule
  ],

})
export class CoreRoutingModule { }
