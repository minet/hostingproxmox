import { Component, OnInit } from '@angular/core';
import {TranslateService} from "@ngx-translate/core";
import {CookieService} from "ngx-cookie-service";


@Component({
  selector: 'app-manual',
  templateUrl: './manual.component.html',
  styleUrls: ['./manual.component.css']
})
export class ManualComponent implements OnInit {

  constructor(
      private translate: TranslateService,
      private cookie: CookieService
  ) { }

  ngOnInit(): void {
  }

}
