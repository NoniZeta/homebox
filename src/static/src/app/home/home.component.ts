import { ViewEncapsulation, OnInit, Component } from '@angular/core';
import { HomeService } from './home.service';

@Component({
  templateUrl: "./home.html",
  providers: [HomeService],
  styleUrls: [
    'home.scss'
  ],
  encapsulation: ViewEncapsulation.Emulated
})
export class HomeComponent implements OnInit {

  isActive: boolean = false;
  errorMessage: string;

  constructor(private homeService: HomeService) { }

  ngOnInit() { this.isActived(); }

  isActived() {
    this.homeService.isVocalActive().subscribe(
      isActive => {
        this.isActive = isActive
      },
      error => this.errorMessage = <any>error);
  }

  onChange() {
    if (this.isActive) {
      this.homeService.startVocal().subscribe(
        isActive => console.log(),
        error => this.errorMessage = <any>error);
    } else {
      this.homeService.stopVocal().subscribe(
        isActive => console.log(),
        error => this.errorMessage = <any>error);
    }
  }
}