import {Component, OnDestroy, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {HttpClient} from '@angular/common/http';
import {User} from '../models/user';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Dns} from '../models/dns';
import {timer, Subscription} from 'rxjs';
import {mergeMap} from 'rxjs/operators';
import { stringify } from 'querystring';


@Component({
  selector: 'app-dns',
  templateUrl: './dns.component.html',
  styleUrls: ['./dns.component.css']
})
export class DnsComponent implements OnInit, OnDestroy {
  loading = true;
  newDns = new Dns();
  ipList = Array<string>();
  intervals = new Set<Subscription>();
  showForm = false;
  errorcode = 201;
  httpErrorMessage = "";
  errorMessage = ""
  timer: Subscription;
  success = false;
  page = 1;
  pageSize = 10;
  constructor(private activatedRoute: ActivatedRoute,
              private http: HttpClient,
              private router: Router,
              public user: User,
              private userService: UserService,
              private authService: AuthService,
              private slugifyPipe: SlugifyPipe) {
  }


  ngOnInit(): void {
    setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user);
        if(this.user.admin || (this.user.chartevalidated && this.user.freezeState < 3)) {
            this.get_dns_list();
            this.user.dns = Array<Dns>();
            this.get_ips_list();
            console.log("ips :", this.user.ips);
        }
    }, 1000);
    this.newDns.entry = 'YourEntry';

  }

  ngOnDestroy(): void {
    for (const id of this.intervals) {
      id.unsubscribe();
    }
  }


  get_dns_list(): void {
    let dnsList: Array<string>;

    this.http.get(this.authService.SERVER_URL + '/dns', {observe: 'response'})
      .subscribe(rep => {
          dnsList = rep.body as Array<string>;
          console.log(dnsList.length);
          if (dnsList.length === 0) {
            this.loading = false;
          }
          for (let i = 0; i < dnsList.length; i++) {
            const id = dnsList[i];
            const last = (i === dnsList.length - 1);
            this.get_dns(id, last);
          }
        },
        error => {
            this.errorcode = error.status;
            this.httpErrorMessage = this.userService.getHttpErrorMessage(this.errorcode)
        });

  }

  get_ips_list(): void {
    this.http.get(this.authService.SERVER_URL + '/ips', {observe: 'response'})
      .subscribe(rep => {
          this.ipList =rep.body["ip_list"];
          console.log(this.ipList)
        },
        error => {
            this.errorcode = error.status;
            this.httpErrorMessage = this.userService.getHttpErrorMessage(this.errorcode)
        });

  }

  get_dns(id: string, last: boolean): void {
    const dns = new Dns();
    dns.id = id;
    this.user.dns.push(dns);
    const newTimer = timer(0, 5000).pipe(
      mergeMap(() => this.http.get(this.authService.SERVER_URL + '/dns/' + id, {observe: 'response'})))
      .subscribe(rep => {
          dns.entry = rep.body['entry'];
          dns.ip = rep.body['ip'];
          dns.user = rep.body['user'];
          if (last) {
            this.loading = false;
          }
        },
        error => {
            this.errorcode = error.status;
            this.httpErrorMessage = this.userService.getHttpErrorMessage(this.errorcode)
        });

    this.intervals.add(newTimer);
  }


  create_dns(dns: Dns): void {
    this.errorMessage = ""
    if(this.user.chartevalidated) {
      if(!this.check_dns_entry(dns.entry)){
        this.errorcode = 401
        this.errorMessage = "This dns entry isn't valid or is forbidden. The submission of this entry will be reported."
        this.httpErrorMessage = this.userService.getHttpErrorMessage(this.errorcode)
      } else if (!this.check_dns_ip(dns.ip)){
        this.errorcode = 401
        this.errorMessage = "This ip isn't valid or is forbidden. Only try with the ip of one of your vm."
        this.httpErrorMessage = this.userService.getHttpErrorMessage(this.errorcode)
      } else {
        let data = {};
        data = {entry: dns.entry, ip: dns.ip};
        this.http.post(this.authService.SERVER_URL + '/dns', data, {observe: 'response'}).subscribe(
          (rep) => {
              if (rep.status === 201) {
                this.success = true;
                window.location.reload();
              }  else {
                this.errorcode = rep.status;
              }
              
            },
            (error_rep) => {
                this.errorcode = error_rep.status;
                this.errorMessage = error_rep.error["error"]
                this.httpErrorMessage = this.userService.getHttpErrorMessage(this.errorcode)
            });
        }
      }
    }


  // Check if the DNS entry is correct and respect minet rules 
  // TO DO : make a manual validation
  check_dns_entry(entry):Boolean{
    let forbidden_entries = ["armes", "arme", "fuck", "porn", "porno", "weapon", "weapons", "pornographie", "amazon", "sex", "sexe", "attack", "hack", "attaque", "hacker", "hacking", "pornhub", "xxx", "store", "hosting", "adh6"];
    let authorized_entry = /^[a-zA-Z0-9]*$/; 
    return authorized_entry.test(entry) && !(entry in forbidden_entries);
  }

 // Check if the ip is for hosting 
  // TO DO : make a local check if the user owns the ip
  check_dns_ip(ip):Boolean{
    let authorized_ip = /^157\.159\.195\.([1-9][0-9]|1[0-9][0-9]|2[0-5][0-5])$/; // At least 157.159.40.xxx > 10 < 255. The backend then checks if the user own the ip
    return authorized_ip.test(ip.trim())
  }

  delete_entry(id): void {
    if(this.user.chartevalidated || this.user.admin) {
      this.http.delete(this.authService.SERVER_URL + '/dns/' + id, {observe: 'response'})
          .subscribe(
              rep => {
                window.location.reload();
              },
              error => {
                  this.errorcode = error.status;
                  this.httpErrorMessage = this.userService.getHttpErrorMessage(this.errorcode)
              });
    }
  }
}
