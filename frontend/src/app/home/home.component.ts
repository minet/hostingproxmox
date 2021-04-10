import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {User} from '../models/user';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Vm} from '../models/vm';
import {Router} from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})

export class HomeComponent implements OnInit {

  vm = new Vm('bob', 'phobos', '1', '10', 'stopped', 'No', '', '', '', 'Secret');

  rulesCheck = false;
  prefix: string;
  loading = false;
  valide = false;
  url: string;
  sshAddress: string;
  interval;
  progress = 0;

  images = [
    {name: 'Bare VM', id: 'bare_vm'},
    {name: 'Simple static web server', id: 'nginx_vm'},
  ];


  constructor(private http: HttpClient,
              private router: Router,
              private user: User,
              private userService: UserService,
              private authService: AuthService,
              private slugifyPipe: SlugifyPipe) {

  }


  ngOnInit(): void {
    this.user = this.userService.getUser();

  }

  progress_bar(): void{
    this.interval = setInterval(() => {
      if (this.progress < 100){
        this.progress = this.progress + 100000 / 180000;
      }
    }, 1000);

  }

  rules_checked(): void {
    if (this.rulesCheck === false) {
      this.rulesCheck = true;
    } else {
      this.rulesCheck = false;
    }
  }

  create_vm(vm: Vm): void {
    this.loading = true;
    this.progress_bar();
    let data = {};
    if (vm.ssh === 'No') {
      data = {
        name: this.slugifyPipe.transform(vm.name),
        ssh: false,
        type: vm.type,
        password: vm.password,
        user: this.slugifyPipe.transform(vm.user)
      };
    } else {
      data = {
        name: this.slugifyPipe.transform(vm.name),
        type: vm.type,
        password: vm.password,
        sshKey: vm.sshKey,
        user: this.slugifyPipe.transform(vm.user),
        ssh: true,

      };
    }
    this.http.post(this.authService.SERVER_URL + '/vm', data, {observe: 'response'}).subscribe(rep => {
        this.progress = 100;
      },
      error => {
        this.progress = 0;
        clearInterval(this.interval);
        if (error.status === 409) {
          window.alert('VM already exists');
          this.router.navigate(['']);
        } else if (error.status === 403) {
          window.alert('Session expired');
          this.router.navigate(['']);
        } else {
          window.alert('Unknown error');
          this.router.navigate(['']);
        }
      });
  }

}
