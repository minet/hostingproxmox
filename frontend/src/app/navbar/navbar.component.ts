import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/services/user.service';
import { User } from '../models/user';
import {CookieService} from 'ngx-cookie-service';
import {Observable} from 'rxjs';
import {TranslateService} from '@ngx-translate/core';
import {HttpClient} from '@angular/common/http';
import {AuthService} from '../common/services/auth.service';
@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  constructor(
    public user: User, 
    public userService: UserService, 
    public cookie: CookieService, 
    public translate: TranslateService,
    private http: HttpClient,
    private authService: AuthService,
    ) {

  }

  public validToken$: Observable<boolean>;
  public notificationTitle: string; // if NULL, no notification;
  public notificationMessage: string; // if NULL, no notification;
  public notificationCriticity: string; 



  ngOnInit(): void {
    this.validToken$ = this.userService.validToken();
    this.validToken$.subscribe();
    this.userService.getUser().subscribe((user) => this.user = user);
    this.cookie.get('lang') == 'en' ? this.translate.use('en') : this.translate.use('fr');
    this.fetchNotification();
  }

  /**
   * Use to change page language
   * @param lang fr ou en selon langue voulue
   */
  changeLanguage(lang): void {
    if(lang == 'en') {
      this.cookie.set('lang', 'en');
      this.translate.use('en');
      this.ngOnInit();
    } else {
      this.cookie.set('lang', 'fr');
      this.translate.use('fr');
      this.ngOnInit();
    }
  }

  /**
   * Used to display a notification as a banner if one is available
   */
  fetchNotification(): void {
    this.http.get(this.authService.SERVER_URL + '/notification', {observe: 'response'}).subscribe(rep => {
      if(rep.status == 200) {
        this.notificationTitle = rep.body['title'];
        this.notificationMessage = rep.body['message'];
        this.notificationCriticity = rep.body['criticity'];
      } else {
        this.notificationTitle = null;
        this.notificationMessage = null;
      }
    },
    error => {
      this.notificationTitle = null;
      this.notificationMessage = null;
    });
  }
}
