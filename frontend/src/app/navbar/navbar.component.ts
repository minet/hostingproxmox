import { Component, OnInit,  Inject} from '@angular/core';
import { UserService } from '../common/services/user.service';
import { User } from '../models/user';
import {CookieService} from 'ngx-cookie-service';
import {Observable} from 'rxjs';
import {TranslateService} from '@ngx-translate/core';
import {HttpClient} from '@angular/common/http';
import {AuthService} from '../common/services/auth.service';
import { DOCUMENT } from '@angular/common';

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
    @Inject(DOCUMENT) private document: Document
    ) {

  }

  public validToken$: Observable<boolean>;
  public notificationTitle: string; // if NULL, no notification;
  public notificationMessage: string; // if NULL, no notification;
  public notificationCriticity: string; 
  public isNotificationEnable: string;
  public isNotificationEnableTest: string; 
  public popUpLoading= false; 
  public saveButtonLabel = "Enregistrer";
  public popUpError = "";



  ngOnInit(): void {
    this.validToken$ = this.userService.validToken();
    this.validToken$.subscribe();
    this.userService.getUserObservable().subscribe((user) => {
        if (user) {
            this.user = user;
        }
    });
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
        this.isNotificationEnable = rep.body['active'];
          this.notificationTitle = rep.body['title'];
        this.notificationMessage = rep.body['message'];
        this.notificationCriticity = rep.body['criticity'];
      } else {
        this.notificationTitle = null;
        this.notificationMessage = null;
      }
    },
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    _error => {
      this.notificationTitle = null;
      this.notificationMessage = null;
    });
  }

  addNotification(): void {
    this.popUpError = "";
    this.popUpLoading = true;
    this.http.patch(this.authService.SERVER_URL + '/notification', {
      title: this.notificationTitle,
      message: this.notificationMessage,
      criticity: this.notificationCriticity,
      active: document.getElementById("notificationEnable")['checked']
    }, {observe: 'response'}).subscribe(rep => {
      if(rep.status == 201) {
        this.saveButtonLabel = "Enregistré !";
        setTimeout(() => {this.popUpLoading = false;
          this.saveButtonLabel = "Enregistrer";}, 1000);
      }
    }, error => {
      this.popUpLoading = false;
      this.popUpError = "Erreur" + String(error.status) + " : " + error.error["error"];
    }
    );
  }

  local_test():void{
    this.isNotificationEnableTest = "true";
  }

}
