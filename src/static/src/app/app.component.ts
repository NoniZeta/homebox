import { Component, ViewEncapsulation, OnInit, ViewContainerRef } from '@angular/core';
import { RouterModule, Router } from '@angular/router';

import { WebSocketService } from './common/service/websocket.service';
import { ToastsManager, Toast } from 'ng2-toastr/ng2-toastr';

@Component({
  selector: 'app',
  templateUrl: "./app.html",
  styleUrls: [
    'app.styles.scss'
  ], 
  providers: [WebSocketService],
  encapsulation: ViewEncapsulation.None,
})
export class AppComponent implements OnInit { 

  private toast:Toast;

  constructor(private router: Router, private wvService: WebSocketService, public toastr: ToastsManager, vcr: ViewContainerRef) {
      this.toastr.setRootViewContainerRef(vcr);
  }

  ngOnInit() { 
    this.wvService.connect("monitoringVocalService").subscribe(text => {
      console.log("Ordre vocal : " + text);
      
      if (text === 'start_utterance') {
        this.showCustom();
      } else if (text === 'end_utterance') {
        this.toastr.dismissToast(this.toast);
      } else {
        this.showInfo(text);
      }
      if (text === 'liste_serie') {
        this.router.navigate(['kodi', { outlets: { kodiRouter: ['serie', { outlets: { serieRouter: ['liste'] } }] } }]);
      }
      if (text === 'liste_film') {
        this.router.navigate(['kodi',{ outlets: { kodiRouter: ['film'] } }]);
      }
      if (text === 'liste_music') {
        this.router.navigate(['kodi',{ outlets: { kodiRouter: ['musique'] } }]);
      }
      if (text === 'liste_course') {
        this.router.navigate(['courses']);
      }
      if (text === 'display_emplacement') {
        this.router.navigate(['emplacements']);
      }
      if (text === 'display_dic') {
         this.router.navigate(['vocal',{ outlets: { vocalRouter: ['dictionnaire'] } }]);
      }
      if (text === 'display_ordre') {
        this.router.navigate(['vocal',{ outlets: { vocalRouter: ['ordres'] } }]);
      }
      if (text === 'display_objectConnected') {
        this.router.navigate(['objectsConnected']);
      }
      if (text === 'display_action') {
        this.router.navigate(['vocal',{ outlets: { vocalRouter: ['actions'] } }]);
      }
      if (text === 'display_mapping_serie') {
        this.router.navigate(['kodi', { outlets: { kodiRouter: ['serie', { outlets: { serieRouter: ['mapping'] } }] } }]);      
      }
      if (text === 'display_serie_encours') {
        this.router.navigate(['kodi', { outlets: { kodiRouter: ['serie', { outlets: { serieRouter: ['encours'] } }] } }]);      
      }
      if (text === 'display_mapping_film') {
        this.router.navigate(['kodi', { outlets: { kodiRouter: ['film', { outlets: { filmRouter: ['mapping'] } }] } }]);      
      }
      if (text === 'display_mapping_music') {
        this.router.navigate(['kodi', { outlets: { kodiRouter: ['musique', { outlets: { musiqueRouter: ['mapping'] } }] } }]);      
      }
      if (text === 'display_telecommande') {
        this.router.navigate(['kodi', { outlets: { kodiRouter: ['telecommande'] } }]);      
      }
      if (text === 'display_bebepaz') {
        this.router.navigate(['bebepaz']);      
      }
    });

  }

    showSuccess() {
        this.toastr.success('Enregistrement ok!!!', 'Success');
      }
    
      closeCustom(){
        this.toastr.dismissToast(this.toast);
      }

      showError() {
        this.toastr.error('This is not good!', 'Oops!');
      }
    
      showWarning() {
        this.toastr.warning('You are being warned.', 'Alert!');
      }
    
      showInfo(text:string) {
        this.toastr.info(text);
      }
      
      showCustom() { 
        this.toastr.custom('<span style="color: green">Ecoute en cours</span>', null, {enableHTML: true, dismiss: 'controlled'}).then((toast: Toast) => {
         this.toast = toast;
        });
      }

}