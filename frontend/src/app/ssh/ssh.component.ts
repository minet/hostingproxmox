import { Component, OnInit } from '@angular/core';
import {TranslateService} from "@ngx-translate/core";
import {CookieService} from "ngx-cookie-service";

@Component({
  selector: 'app-ssh',
  templateUrl: './ssh.component.html',
  styleUrls: ['./ssh.component.css']
})
export class SshComponent implements OnInit {

  constructor(
      private translate: TranslateService,
      private cookie: CookieService
  ) { }

  ngOnInit(): void {
  }

}
