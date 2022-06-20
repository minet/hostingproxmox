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
  title = 'Hosting';


  constructor(public userService: UserService, public router: Router, private titleService: Title) {
    var url = window.location.hostname;
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
  ngOnInit(): void {
    this.validToken$ = this.userService.validToken();
    this.validToken$.subscribe();
  }

}
