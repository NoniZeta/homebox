import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { KodiComponent }        from './kodi/kodi.component';
import { Telecommande }         from './kodi/telecommande/telecommande.component';
import { SerieComponent }       from './kodi/serie/serie.component';
import { FilmComponent }        from './kodi/film/film.component';
import { MusiqueKodiComponent } from './kodi/musique/musique.component';
import { ListeFilmsComponent }  from './kodi/film/liste/liste.component';
import { ListeComponent }       from './kodi/serie/liste/liste.component';
import { ListeMusiquesComponent }  from './kodi/musique/liste/liste.component';
import { EnCoursComponent }     from './kodi/serie/encours/encours.component';
import { MappingComponent }     from './kodi/serie/mapping/mapping.component';

import { CourseComponent }     from './courses/courses.component';
import { FilmMappingComponent } from './kodi/film/mapping/mapping.component';
import { BebepazComponent } from './bebepaz/bebepaz.component';
import { MusiqueComponent } from './musique/musique.component';


export const modulesRoutes: Routes = [
    { path: 'kodi',  component: KodiComponent, 
        children: [
            { path: '', component: Telecommande, outlet: 'kodiRouter'  },
            { path: 'telecommande',  component: Telecommande, outlet: 'kodiRouter'  },
            { path: 'film',  component: FilmComponent, outlet: 'kodiRouter',
              children: [
                { path: '', component: ListeFilmsComponent, outlet: 'filmRouter'  },
                { path: 'liste', component: ListeFilmsComponent, outlet: 'filmRouter'  },
                { path: 'mapping', component: FilmMappingComponent, outlet: 'filmRouter'  }  
            ]},
            { path: 'musique',  component: MusiqueKodiComponent, outlet: 'kodiRouter',
              children: [
                { path: '', component: ListeMusiquesComponent, outlet: 'musiqueRouter'  },
                { path: 'liste', component: ListeMusiquesComponent, outlet: 'musiqueRouter'  },
                { path: 'mapping', component: MappingComponent, outlet: 'musiqueRouter'  }  
            ]},
            { path: 'serie',  component: SerieComponent, outlet: 'kodiRouter',
                children: [
                { path: '', component: ListeComponent, outlet: 'serieRouter'  },
                { path: 'liste', component: ListeComponent, outlet: 'serieRouter'  },
                { path: 'encours', component: EnCoursComponent, outlet: 'serieRouter'  },
                { path: 'mapping', component: MappingComponent, outlet: 'serieRouter'  }  
            ]}
          ],  
    },
    { path: 'courses',  component: CourseComponent },
    { path: 'bebepaz',  component: BebepazComponent }, 
    { path: 'musicModule',  component: MusiqueComponent }   
];

@NgModule({
  imports: [
    RouterModule.forChild(modulesRoutes)
  ],
  exports: [
    RouterModule
  ],

})
export class ModulesRoutingModule { }
