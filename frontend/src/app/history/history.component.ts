import { Component, OnInit } from '@angular/core';
import {ActivatedRoute, Router} from "@angular/router";
import {HttpClient} from "@angular/common/http";
import {User} from "../models/user";
import {UserService} from "../common/services/user.service";
import {AuthService} from "../common/services/auth.service";
import {SlugifyPipe} from "../pipes/slugify.pipe";
import {timer} from "rxjs";
import {mergeMap} from "rxjs/operators";
import {TranslateService} from "@ngx-translate/core";
import {CookieService} from "ngx-cookie-service";

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css']
})
export class HistoryComponent implements OnInit {
  history: unknown;
  page = 1;
  errorcode = 201;
  pageSize = 200;
  searchText;
  constructor(
      private activatedRoute: ActivatedRoute,
      private router: Router,
      private http: HttpClient,
      public user: User,
      private userService: UserService,
      public authService: AuthService,
      public slugifyPipe: SlugifyPipe,
      private translate: TranslateService,
      private cookie: CookieService
  ) { }

  ngOnInit(): void {
    this.userService.getUser().subscribe((user) => {
      this.user = user;
    });
      this.get_ip_history();
  }


  get_ip_history(): void {
    const newTimer = timer(0, 3000).pipe(
      mergeMap(() => this.http.get(this.authService.SERVER_URL + '/historyall', {observe: 'response'})))
        .subscribe(rep => {
              this.history = rep.body;
            },
            error => {
              this.errorcode = error.status;
            });
  }

}
