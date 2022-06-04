import {Component, OnInit, Input, SimpleChange, OnChanges, SimpleChanges} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {User} from '../models/user';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Vm} from '../models/vm';
import {Router} from '@angular/router';
import {timer} from 'rxjs';
import {mergeMap} from 'rxjs/operators';
import {Dns} from "../models/dns";

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css'],
})


  

export class HomeComponent implements OnInit {

  

  vm = new Vm('', '', '1', '10', 'stopped', 'No', '', '', '', '');
  maxVmPerUser = 3;
  rulesCheck = false;
  passwordErrorMessage = "";
  prefix: string;
  loading = false;
  valide = false;
  errorcode = 0;
  errorMessage = ""
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
    setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user);
      if ((this.user.chartevalidated && this.user.cotisation) || this.user.admin) {
        this.count_vm();
      }
      if(this.user.admin) {
        this.count_dns();
      }}, 1000);

  }


  progress_bar(): void{
    this.interval = setInterval(() => {
      if (this.progress < 100){
        console.log(this.progress)
        this.progress = this.progress + 10 / 18;
      }
    }, 1000);
  }



  rules_checked(): void {
    if (this.rulesCheck === false) {
      this.rulesCheck = true;
    } else {
      this.rulesCheck = false;
    }
    this.check_password(this.vm)
    this.checkSSHkey(this.vm)
  }

  
  // check if the password respect the CNIL specs It is check after the box check and after that, after each new char modification
  check_password(vm):boolean{
    var special = /[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/;
    var upper = /[A-Z]/;
    var number = /[0-9]/;
    this.passwordErrorMessage = "";
    var isOk = true;

    if (vm.password.length<=11){
      this.passwordErrorMessage += "● 12 characters.<br/>";
      isOk = false;
    }
    
    if (!upper.test(vm.password)){
      this.passwordErrorMessage += "● 1 uppercase letter.<br/>";
      isOk = false;
    }
    if (!special.test(vm.password)){
      this.passwordErrorMessage += "● 1 special character.<br/>";
      isOk = false;
    }

    

    if(!number.test(vm.password)){
      this.passwordErrorMessage += "●  1 number.<br/>";
      isOk = false;
    }

    if (!isOk){
      this.passwordErrorMessage = "Your password must contains at least <br/>" + this.passwordErrorMessage
    }
    
    return isOk;
    
  }

  // check with a regex if the ssh key has a correct format. It is check after the box check and after that, after each new char modification
  checkSSHkey(vm: Vm):boolean{
    var rule = /ssh.[a-zA-Z0-9]* [a-zA-Z0-9[()[\]{}+*\/%$&#@=:?]*/
    return rule.test(vm.sshKey)
  }

  // a username different of 'root' is mandatory
  checkUser(vm:Vm):boolean{
    console.log("check user")
    return vm.user == "root"
  }

  create_vm(vm: Vm): void {
    // first of all check parameter : 
    const isPasswordOk = this.check_password(this.vm)
    if (isPasswordOk) {
       
      this.loading = true;
      this.progress_bar();
      let data = {};
        data = {
          name: this.slugifyPipe.transform(vm.name),
          type: vm.type,
          password: vm.password,
          sshKey: vm.sshKey,
          user: this.slugifyPipe.transform(vm.user),
          ssh: true,

        };
      this.http.post(this.authService.SERVER_URL + '/vm', data, {observe: 'response'}).   subscribe(rep => {
          this.progress = 100;
          this.loading = false;
        },
        error => {
          this.loading = false
          clearInterval(this.interval);
          this.errorcode = error.status;
          this.errorMessage = error.error["error"];
          console.log(error)
        });
      }
      //this.loading = false
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

