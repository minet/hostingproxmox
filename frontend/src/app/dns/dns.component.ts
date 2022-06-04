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


@Component({
  selector: 'app-dns',
  templateUrl: './dns.component.html',
  styleUrls: ['./dns.component.css']
})
export class DnsComponent implements OnInit, OnDestroy {
  loading = true;
  newDns = new Dns();
  intervals = new Set<Subscription>();
  showForm = false;
  errorcode = 201;
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
        if(this.user.admin || (this.user.chartevalidated && this.user.cotisation)) {
            this.get_dns_list();
            this.user.dns = Array<Dns>();
        }
    }, 1000);
    this.newDns.entry = 'YourEntry';
    this.newDns.ip = '157.159.195.x';
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
        });

    this.intervals.add(newTimer);
  }


  create_dns(dns: Dns): void {
    if(this.user.chartevalidated) {
      let data = {};
      data = {entry: dns.entry, ip: dns.ip};
      this.http.post(this.authService.SERVER_URL + '/dns', data, {observe: 'response'}).subscribe(rep => {
            if (rep.status === 201) {
              this.success = true;
            }
            window.location.reload();
          },
          error => {
              this.errorcode = error.status;
          });
    }
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
              });
    }
  }
}
