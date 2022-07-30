import { Component, OnInit } from '@angular/core';
import {TranslateService} from "@ngx-translate/core";
import {CookieService} from "ngx-cookie-service";

@Component({
  selector: 'app-rules',
  templateUrl: './rules.component.html',
  styleUrls: ['./rules.component.css']
})
export class RulesComponent implements OnInit {

  constructor(
      private translate: TranslateService,
      private cookie: CookieService
  ) { }

  ngOnInit(): void {
  }

}
