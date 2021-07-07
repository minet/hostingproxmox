import { Injectable } from '@angular/core';


@Injectable({
  providedIn: 'root'
})
export class AuthService {

  constructor() {
  }

   //public SERVER_URL = 'http://localhost:8080/api/1.0.0';
   public adminDn = 'cn=cluster-hosting,ou=groups,dc=minet,dc=net';
   public SERVER_URL = 'https://backprox.minet.net/api/1.0.0';



}
