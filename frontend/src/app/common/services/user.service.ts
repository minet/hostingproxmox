import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { User } from '../../models/user';
import { OAuthService} from 'angular-oauth2-oidc';
import { JwksValidationHandler } from 'angular-oauth2-oidc-jwks';
import { authCodeFlowConfig } from '../../sso.config';

@Injectable({
  providedIn: 'root'
})
export class UserService {

  constructor(private user: User, private authService: AuthService, private oauthService: OAuthService) {
    this.configureSingleSignOn();
  }

  configureSingleSignOn(): void {

    this.oauthService.configure(authCodeFlowConfig);
    this.oauthService.tokenValidationHandler = new JwksValidationHandler();
    this.oauthService.loadDiscoveryDocumentAndTryLogin();

  }

  login(): void {
    this.oauthService.initImplicitFlow();
    this.oauthService.setupAutomaticSilentRefresh();

  }

  logout(): void {
    this.oauthService.logOut();
  }

  validToken(): boolean{
    return this.oauthService.hasValidAccessToken();
  }

  getUser(): User {
    const user: any = this.oauthService.getIdentityClaims();
    if (user != null) {
      this.user.username = user.sub;
      this.user.name = user.given_name;
      return this.user;
    }
    else{
      return null;
    }

  }

}
