import {Component, OnInit} from '@angular/core';
import { UserService } from './common/services/user.service';
import {Observable, timer} from 'rxjs';
import {Router} from '@angular/router';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'VPS MiNET';


  constructor(public userService: UserService, public router: Router) {
  }

  public validToken$: Observable<boolean>;
  ngOnInit(): void {
    this.validToken$ = this.userService.validToken();
    this.validToken$.subscribe((next) => console.log(next));
  }

}
