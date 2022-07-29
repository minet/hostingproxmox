import { Component, OnInit } from '@angular/core';
import { UserService } from '../common/services/user.service';
import { User } from '../models/user';
import {CookieService} from 'ngx-cookie-service';
import {Observable} from 'rxjs';
import {TranslateModule, TranslateLoader, TranslateService} from '@ngx-translate/core';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {
  constructor(public user: User, public userService: UserService, public cookie: CookieService, public translate: TranslateService) {

  }

  public validToken$: Observable<boolean>;
  ngOnInit(): void {
    this.validToken$ = this.userService.validToken();
    this.validToken$.subscribe();
    this.userService.getUser().subscribe((user) => this.user = user);
    this.cookie.get('lang') == 'en' ? this.translate.use('en') : this.translate.use('fr');
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

}
