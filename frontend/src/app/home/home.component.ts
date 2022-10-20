import {Component, OnInit, Input, SimpleChange, OnChanges, SimpleChanges} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {UserService} from '../common/services/user.service';
import {Utils} from '../common/utils';
import {AuthService} from '../common/services/auth.service';
import {User} from '../models/user';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Vm} from '../models/vm';
import {ActivatedRoute, Router} from '@angular/router';
import {timer} from 'rxjs';
import {mergeMap} from 'rxjs/operators';
import {Dns} from "../models/dns";
import {TranslateService} from "@ngx-translate/core";
import {CookieService} from "ngx-cookie-service";

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
  nb_error_resquest = 0; // Count the number of SUCCESSIVE error returned by a same request
  isVmCreated = false; // true doesn't mean the VM is started 

 


  constructor(private http: HttpClient,
              private router: Router,
              public user: User,
              private utils: Utils,
              private userService: UserService,
              private authService: AuthService,
              private slugifyPipe: SlugifyPipe,
              private route: ActivatedRoute,
              public translate: TranslateService,
              private cookie: CookieService, 
              ) {
    this.cookie.get('lang') == 'en' ? this.translate.use('en') && this.cookie.set('lang','en') : this.translate.use('fr') && this.cookie.set('lang','fr');
    console.log("cookie =" + this.route.snapshot.paramMap.get('lang'))
  }

  


  ngOnInit(): void {
    setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user);
      if ((this.user.chartevalidated && this.user.cotisation) || this.user.admin) {
        this.count_vm();
      }
      if(this.user.admin) {
        this.count_dns();
      }}, 1000);
      console.log("translation  = " +this.utils.getTranslation("home.errorMessage.errorCreating"))

  }

  images = [
    {name: "home.vm_type.bare", id: 'bare_vm'},
    {name: "home.vm_type.web", id: 'nginx_vm'},
  ];


  progress_bar(): void{
    this.interval = setInterval(() => {
      if (this.progress < 95) {
        console.log(this.progress)
        const max = 5
        const min = 1
        this.progress = this.progress +  (Math.random() * (max - min) + min) / 18;
      }
    }, 300);
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
      this.passwordErrorMessage += this.utils.getTranslation("home.password.length") + "<br>";
      isOk = false;
    }
    
    if (!upper.test(vm.password)){
      this.passwordErrorMessage += this.utils.getTranslation("home.password.uppercase") + "<br>";
      isOk = false;
    }
    if (!special.test(vm.password)){
      this.passwordErrorMessage += this.utils.getTranslation("home.password.special_char") + "<br>";
      isOk = false;
    }

    

    if(!number.test(vm.password)){
      this.passwordErrorMessage += this.utils.getTranslation("home.password.digit") + "<br>";;
      isOk = false;
    }

    if (!isOk){
      this.passwordErrorMessage =  this.utils.getTranslation("home.password.requirementIntro") + "<br/>" + this.passwordErrorMessage
    }
    
    return isOk;
    
  }

  // check with a regex if the ssh key has a correct format. It is check after the box check and after that, after each new char modification
  checkSSHkey(vm: Vm):boolean{
    var rule = /^[a-zA-Z0-9[()[\].{\-}_+*""\/%$&#@=:?]* [a-zA-Z0-9[()[\].{\-}_+*""\/%$&#@=:?]* [a-zA-Z0-9[()[\].{\-}_+*""\/%$&#@=:?]*/
    return rule.test(vm.sshKey)
  }

  // a username different of 'root' is mandatory
  checkUser(vm:Vm):boolean{
    console.log("check user")
    return vm.user == "root"
  }

  /*
  Create a vm.
  The first step is to check if the password is strong enough. The other arg are check while typing and by the backend 

  Then the request is send to the backend. It answers when the vm is cloning. 
  After, we check every second if the vm is up and started. It means it is well configurated. Else we wait. If there is no vm anymore then a error occured
  */
  create_vm(vm: Vm): void {
    this.errorMessage = ""
    this.errorcode = 0
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
        this.errorMessage = ""
          var id = rep.body["vmId"]
          var isStarted = false;


          // The vm is creating we check if it is up and started
          (async () => { 
            while (!isStarted && this.loading){ 
              this.http.get(this.authService.SERVER_URL + '/vm/' + id, {observe: 'response'}).subscribe(rep => {
                  this.vmstate = rep.body['status'];
                  isStarted = this.vmstate == "created" || this.vmstate == "booting" || this.vmstate == "running" || this.vmstate == "stoped";
                },
                  error => {
                          this.loading = false;
                        this.errorcode = error.status;
                        this.errorMessage = error.error["error"];
                        clearInterval(this.interval);
                    
              });
              await delay(2000);
          }
          if (isStarted){ // There were no errors, we show the vm
            this.progress = 100;
            this.router.navigate(['/vms/' + id]);
          } else { // There was an error, we show the form for a new submit
            clearInterval(this.interval);
          }
            
        }
        )();
        },
        error => {
          // If it's system error, it most come from the user. Then we send him to the vms page.
            this.errorcode = error.status;
            this.loading = false
            clearInterval(this.interval);
            
            this.errorMessage = error.error["error"];
            console.log(error)
        });
      }
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
          this.loading = false
          this.errorcode = error.status;
          this.errorMessage = error.error["error"];
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
          this.new_vmstatus(vmid);
        }
      },

      error => {
        this.loading = false
        this.errorcode = error.status;
        this.errorMessage = error.error["error"];
      });
  }

  /*
    Check the vm status (vmid). If it's started, the number of active vm is added to 1
  */
  new_vmstatus(vmid: string): void {
    const vm = new Vm();
    vm.id = vmid;
    this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'}).subscribe(rep => {
        this.vmstate = rep.body['status'];
        if(rep.body['status'] === "running")
          this.countactivevm++;
        },
        error => {
          this.loading = false
          this.errorcode = error.status;
          this.errorMessage = error.error["error"];
    });
  }

/*Return true if the vm is booting and false if not
vmid is the id of the vm researched 

While the number of consecutive error throws by the backend is under 5, we consider it is just some request who failed and not a global file. It should sustain the up to 10s/15s of errors
*/
is_vm_booting(vmid: string) : boolean {
  this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'}).subscribe(rep => {
    this.nb_error_resquest =0;
      this.vmstate = rep.body['status'];
      return rep.body['status'] == "booting" || rep.body['status'] == "running"
    },
      error => {
        this.nb_error_resquest ++;
        if (this.nb_error_resquest >= 5){
          if (error.status == 404){
            this.loading = false;
            this.errorcode = error.status;
            this.errorMessage = this.utils.getTranslation("home.errorMessage.errorCreating");

          } else {
            this.loading = false;
          this.errorcode = error.status;
          this.errorMessage = error.error["error"];
          }
        }
        
  });
  return false
}
}

function delay(ms: number) {
  return new Promise( resolve => setTimeout(resolve, ms) );
}
