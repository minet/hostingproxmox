import {Component, OnInit} from '@angular/core';
import { UserService } from './common/services/user.service';
import { VmsService } from './common/services/vms.service';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import { Title } from '@angular/platform-browser';
import {CookieService} from "ngx-cookie-service";
import { User } from './models/user';
import { DnsService } from './common/services/dns.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
/**
 * Represents the root component of the application.
 */
export class AppComponent implements OnInit{
  title = 'Hosting';

  constructor(public userService: UserService, 
              public vmsService: VmsService, 
              public dnsService: DnsService,
              public user: User,
              public router: Router, 
              private titleService: Title, 
              public cookie: CookieService) 
              {
    const url = window.location.hostname;
    this.title = "Hosting";
    
    switch(url){
      case "hosting-dev.minet.net" : {
        this.title = "Hosting Dev";
        break;
      }
      case "hosting-local.minet.net" :{
        this.title = "Hosting local";
         break;
      }
      default: {
        this.title = "Hosting";
        break;
      } 
    }
    this.titleService.setTitle(this.title)
  }

  public validToken$: Observable<boolean>;

  /**
  * Est appelé au démarrage de l'app
  */
  ngOnInit(): void {

    this.validToken$ = this.userService.validToken();
    this.validToken$.subscribe(); // Change de valeur à chaque jeton reçu

    this.userService.getUser(); // Met à jour l'utilisateur connecté

    //Puis on souscrit aux valeurs de l'utilisateur au cours du temps
    this.userService.getUserObservable().subscribe((user) => {

      //On attend d'avoir un utilisateur valide, en particulier le freezeState qui prend du temps à être récupéré
      if (user && user.freezeState>=0) {
        this.user = user;
        
        if (this.user.admin) {

          //On précharge les utilisateurs expirés pour plus de rapidité, en mode admin
          this.vmsService.updateExpiredCotisationUsers();
        }
        if ((this.user.chartevalidated && this.user.freezeState < 3) || this.user.admin) {

          //On précharge les VMs et DNS pour plus de rapidité
          this.dnsService.updateDnsIds();
          this.dnsService.updateAllDns();
          this.vmsService.updateVmIds();
          this.vmsService.updateVms(0);

        }
      }
    });
    
  }

}
