
import {NgModule} from '@angular/core';
import {RouterModule, Routes} from "@angular/router";

import { homeRoutes } from './home/router';

export const appRoutes: Routes = [
  { path: '', redirectTo: 'home', pathMatch: 'full' },
  ...homeRoutes
];

@NgModule({
    imports : [RouterModule.forRoot(appRoutes)],
    exports : [ RouterModule ]
})
export class AppRoutingModule  {
}
