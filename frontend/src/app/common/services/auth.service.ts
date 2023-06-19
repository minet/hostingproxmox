import { Injectable } from '@angular/core';
import { environment } from '../../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

    // local : true
   public SERVER_URL = environment.backendURL + '/2.0';
   public adminDn = 'cn=cluster-hosting,ou=groups,dc=minet,dc=net';
   //public SERVER_URL = 'https://api.hosting.minet.net/2.0';



}
