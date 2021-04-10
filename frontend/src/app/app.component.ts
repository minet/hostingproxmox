import {Component, OnInit} from '@angular/core';
import { UserService } from './common/services/user.service';
import { timer } from 'rxjs';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'VPS MiNET';


  constructor(private userService: UserService) {
  }

  validToken = this.userService.validToken();
  ngOnInit(): void {
    timer(300).subscribe(x => {this.refreshToken(); });
  }

  refreshToken(): void{
    this.validToken = this.userService.validToken();
  }


}
