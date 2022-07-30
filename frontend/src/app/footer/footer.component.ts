import { Component, OnInit } from '@angular/core';
import {TranslateService} from "@ngx-translate/core";
import {CookieService} from "ngx-cookie-service";


@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent implements OnInit {
  date: Date = new Date();

  constructor(
      private translate: TranslateService,
      public cookie: CookieService
  ) {

  }

  ngOnInit(): void {
  }


}
