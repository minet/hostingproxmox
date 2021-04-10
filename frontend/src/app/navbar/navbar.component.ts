import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserService } from '../common/services/user.service';
import { User } from '../models/user';
import {timer} from 'rxjs';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {

  constructor(public user: User, private http: HttpClient, public userService: UserService) {

  }

  ngOnInit(): void {
    timer(300).subscribe(x => {this.refreshUser(); });
    this.user = this.userService.getUser();
  }

  refreshUser(): void{
    this.user = this.userService.getUser();
  }




}
