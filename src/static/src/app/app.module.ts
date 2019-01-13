import { NgModule }       from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import { FormsModule }    from '@angular/forms';

import { AppRoutingModule } from './app.routing.module';
import { CoreModule } from './core/core.module';
import { ModulesModule } from './modules/modules.module';

import { AppComponent }     from './app.component';
import { HomeComponent }  from './home/home.component';
import { ToastModule } from 'ng2-toastr/ng2-toastr';

@NgModule({
  imports: [
    BrowserModule,
    FormsModule,
    AppRoutingModule,
    CoreModule,
    ModulesModule,
    BrowserAnimationsModule,
    ToastModule.forRoot()
  ],
  declarations: [
    AppComponent,
    HomeComponent
      ],
  bootstrap: [ AppComponent ]
})
export class AppModule {
}
