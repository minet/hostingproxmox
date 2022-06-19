import {Component, OnInit} from '@angular/core';
import { UserService } from './common/services/user.service';
import {Observable} from 'rxjs';
import {Router} from '@angular/router';
import { Title } from '@angular/platform-browser';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'VPS MiNET';


  constructor(public userService: UserService, public router: Router, private titleService: Title) {
    var url = window.location.hostname;
    var title = "Hosting";
    
    switch(url){
      case "hotsing-dev.minet.net" : {
        title = "Hosting Dev";
        break;
      }
      case "hosting-local.minet.net" :{
         title = "Hosting local";
         break;
      }
      default: {
        title = "Hosting";
        break;
      } 
    }
    this.titleService.setTitle(title)
  }

  public validToken$: Observable<boolean>;
  ngOnInit(): void {
    this.validToken$ = this.userService.validToken();
    this.validToken$.subscribe();
  }

}
