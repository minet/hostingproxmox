import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { UserService } from '../common/services/user.service';
import { User } from '../models/user';

@Component({
  selector: 'app-navbar',
  templateUrl: './navbar.component.html',
  styleUrls: ['./navbar.component.css']
})
export class NavbarComponent implements OnInit {

  constructor(public user: User, private http: HttpClient, private userService: UserService) {

  }

  ngOnInit(): void {
    this.user = this.userService.getUser();

  }




}
