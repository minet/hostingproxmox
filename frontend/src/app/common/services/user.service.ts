import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { User } from '../../models/user';
import { OAuthService} from 'angular-oauth2-oidc';
import { JwksValidationHandler } from 'angular-oauth2-oidc-jwks';
import { authCodeFlowConfig } from '../../sso.config';
import {merge, Observable} from 'rxjs';
import {fromPromise} from 'rxjs/internal-compatibility';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  private discoveryDocument$: Promise<boolean>;
  constructor(private user: User, private authService: AuthService, private oauthService: OAuthService) {
    this.configureSingleSignOn();
  }

  configureSingleSignOn(): void {

    this.oauthService.configure(authCodeFlowConfig);
    this.oauthService.tokenValidationHandler = new JwksValidationHandler();
    this.discoveryDocument$ = this.oauthService.loadDiscoveryDocumentAndTryLogin();
  }

  login(): void {
    this.oauthService.initImplicitFlow();
    this.oauthService.setupAutomaticSilentRefresh();

  }

  logout(): void {
    this.oauthService.logOut();
  }

  validToken(): Observable<boolean> {
    const tokenObservable$: Observable<boolean> = new Observable<boolean>((sub) => {
      if (this.oauthService.hasValidAccessToken()) {
        sub.next(true);
      }
    });
    return merge(
        this.discoveryDocument$.then((result) => this.oauthService.hasValidAccessToken()),
        tokenObservable$
    );
  }

  getUser(): Observable<User> {
    return fromPromise(this.discoveryDocument$.then((result) => {
    const user: any = this.oauthService.getIdentityClaims();
    if (user != null) {
      this.user.username = user.sub;
      this.user.sn = user.sn;
      this.user.name = user.given_name;
      this.user.admin = false;
      if(['seberus', 'zastava', 'lionofinterest'].includes(user.sub))
        this.user.admin = true;
      return this.user;
    }
    else{
      return null;
      }
    }));

   }
}
