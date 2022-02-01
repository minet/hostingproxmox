import {Component, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {User} from '../models/user';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Vm} from '../models/vm';
import {Router} from '@angular/router';
import {timer} from 'rxjs';
import {flatMap} from 'rxjs/internal/operators';
import {Dns} from "../models/dns";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})

export class HomeComponent implements OnInit {

  vm = new Vm('bob', 'phobos', '1', '10', 'stopped', 'No', '', '', '', 'Secret');
  maxVmPerUser = 3;
  rulesCheck = false;
  prefix: string;
  loading = false;
  valide = false;
  errorcode = 201;
  url: string;
  sshAddress: string;
  countvm: number;
  countactivevm: number;
  countdns: number;
  vmstate: string;
  interval;
  progress = 0;

  images = [
    {name: 'Bare VM', id: 'bare_vm'},
    {name: 'Simple static web server', id: 'nginx_vm'},
  ];


  constructor(private http: HttpClient,
              private router: Router,
              public user: User,
              private userService: UserService,
              private authService: AuthService,
              private slugifyPipe: SlugifyPipe) {

  }


  ngOnInit(): void {
    setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user); }, 1000);
    this.count_vm();
    if(this.user.admin) {
      this.count_dns();
    }

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
        this.errorcode = error.status;
      });
  }
  count_dns(): void {
    let dns: Array<string>;
    this.countdns = 0;
    this.http.get(this.authService.SERVER_URL + '/dns', {observe: 'response'}).subscribe(rep => {
          dns = rep.body as Array<string>;
          for (let i = 0; i < dns.length; i++) {
            const dnsid = dns[i];
            this.countdns++;
          }
        },
        error => {
          this.errorcode = error.status;
        });
  }
  count_vm(): void {
    let vmList: Array<string>;
    this.countvm = 0;
    this.countactivevm = 0;
    this.http.get(this.authService.SERVER_URL + '/vm', {observe: 'response'}).subscribe(rep => {
      vmList = rep.body as Array<string>;
      for (let i = 0; i < vmList.length; i++) {
        const vmid = vmList[i];
        this.countvm++;
        this.get_vmstatus(vmid);
      }
    },

    error => {
      this.errorcode = error.status;
    });
  }
  get_vmstatus(vmid: string): void {
    const vm = new Vm();
    vm.id = vmid;
    this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'}).subscribe(rep => {
        this.vmstate = rep.body['status'];
        if(rep.body['status'] === "running")
          this.countactivevm++;
        },
        error => {
          this.errorcode = error.status;
    });
  }
}
