import { Injectable } from '@angular/core';
import { OAuthService} from 'angular-oauth2-oidc';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor() {
  }

  // public SERVER_URL = 'http://localhost:8080/api/1.0.0';
  public SERVER_URL = 'https://backprox.minet.net/api/1.0.0';



}
