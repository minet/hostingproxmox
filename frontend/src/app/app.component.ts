import {Component, OnInit} from '@angular/core';
import { UserService } from './common/services/user.service';
import {Observable, timer} from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'VPS MiNET';


  constructor(private userService: UserService) {
  }

  public validToken$: Observable<boolean>;
  ngOnInit(): void {
    this.validToken$ = this.userService.validToken();
    this.validToken$.subscribe((next) => console.log(next));
  }

  refreshToken(): void{
    //this.validToken = this.userService.validToken();
  }


}
