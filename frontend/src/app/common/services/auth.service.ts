import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor() {
  }
    // local : true
   public SERVER_URL = environment.backendURL + '/api/1.0.0';
   public adminDn = 'cn=cluster-hosting,ou=groups,dc=minet,dc=net';
   //public SERVER_URL = 'https://backprox.minet.net/api/1.0.0';



}
