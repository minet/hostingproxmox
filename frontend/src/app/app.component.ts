import {Component, OnDestroy, OnInit} from '@angular/core';
import { UserService } from './common/services/user.service';
import { User } from './models/user';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit, OnDestroy {
  title = 'VPS MiNET';


  constructor(public user: User, private userService: UserService) {
  }

  ngOnInit(): void {
    this.user = this.userService.getUser();
    console.log(this.userService.validToken());
  }
  ngOnDestroy(): void {
    this.user = this.userService.getUser();
  }


}
