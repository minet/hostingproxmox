import { Component, OnDestroy, OnInit } from '@angular/core';
import {HttpClient} from "@angular/common/http";
import {User} from "../models/user";
import {UserService} from "../common/services/user.service";
import {AuthService} from "../common/services/auth.service";
import {SlugifyPipe} from "../pipes/slugify.pipe";
import {Subscription, timer} from "rxjs";
import {mergeMap} from "rxjs/operators";

@Component({
  selector: 'app-history',
  templateUrl: './history.component.html',
  styleUrls: ['./history.component.css']
})
export class HistoryComponent implements OnInit, OnDestroy {
  history: unknown;
  page = 1;
  errorcode = 201;
  pageSize = 200;
  searchText: unknown;
  private subscription: Subscription;

  constructor(
      private http: HttpClient,
      public user: User,
      private userService: UserService,
      public authService: AuthService,
      public slugifyPipe: SlugifyPipe,
  ) { }

  ngOnInit(): void {
    this.userService.getUserObservable().subscribe((user) => {
      if(user) {
        this.user = user;
      }
    });
      this.subscription = this.get_ip_history();
  }

  ngOnDestroy(): void {
    if (this.subscription) {
      this.subscription.unsubscribe();
    }
  }

  get_ip_history(): Subscription {
    return timer(0, 3000).pipe(
      mergeMap(() => this.http.get(this.authService.SERVER_URL + '/historyall', {observe: 'response'})))
      .subscribe(rep => {
          this.history = rep.body;
        },
        error => {
          this.errorcode = error.status;
        });
  }

}
