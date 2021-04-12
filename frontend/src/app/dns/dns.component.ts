import {Component, OnDestroy, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {HttpClient} from '@angular/common/http';
import {User} from '../models/user';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Dns} from '../models/dns';
import {timer, Subscription} from 'rxjs';
import {flatMap} from 'rxjs/internal/operators';


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
  timer: Subscription;
  success = false;

  constructor(private activatedRoute: ActivatedRoute,
              private http: HttpClient,
              private router: Router,
              public user: User,
              private userService: UserService,
              private authService: AuthService,
              private slugifyPipe: SlugifyPipe) {
  }


  ngOnInit(): void {
    this.userService.getUser().subscribe((user) => this.user = user);
    this.get_dns_list();
    this.user.dns = Array<Dns>();
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
          if (error.status === 404) {
            window.alert('Not found');
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

  get_dns(id: string, last: boolean): void {
    const dns = new Dns();
    dns.id = id;
    this.user.dns.push(dns);
    const newTimer = timer(0, 3000).pipe(
      flatMap(() => this.http.get(this.authService.SERVER_URL + '/dns/' + id, {observe: 'response'})))
      .subscribe(rep => {
          dns.entry = rep.body['entry'];
          dns.ip = rep.body['ip'];
          if (last) {
            this.loading = false;
          }
        },
        error => {
          if (error.status === 404) {
            window.alert('DNS not found');
            this.router.navigate(['']);
          } else if (error.status === 403) {
            window.alert('Session expired');
            this.router.navigate(['']);
          } else {
            window.alert('Unknown error');
            this.router.navigate(['']);
          }

        });

    this.intervals.add(newTimer);
  }


  create_dns(dns: Dns): void {

    let data = {};
    data = {entry: this.slugifyPipe.transform(dns.entry), ip: dns.ip};
    this.http.post(this.authService.SERVER_URL + '/dns', data, {observe: 'response'}).subscribe(rep => {
        if (rep.status === 201) {
          this.success = true;
        }
        window.location.reload();
      },
      error => {
        if (error.status === 405) {
          window.alert('DNS already exists');
        } else if (error.status === 403) {
          window.alert('Session expired');
        } else {
          window.alert('Unknown error');
        }
      });

  }

  delete_entry(id): void {
    this.http.delete(this.authService.SERVER_URL + '/dns/' + id, {observe: 'response'})
      .subscribe(
        rep => {
          window.location.reload();
        },
        error => {
          if (error.status === 409) {
            window.alert('Dns entry already exists');
            window.location.reload();
          } else if (error.status === 403) {
            window.alert('Session expired');
            window.location.reload();
          } else {
            window.alert('Unknown error');
            window.location.reload();
          }
        });
  }
}
