import {Component, OnDestroy, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Vm} from '../models/vm';
import {HttpClient} from '@angular/common/http';
import {User} from '../models/user';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {interval, Subscription, timer} from 'rxjs';
import {flatMap} from 'rxjs/internal/operators';

@Component({
  selector: 'app-vm',
  templateUrl: './vm.component.html',
  styleUrls: ['./vm.component.css']
})
export class VmComponent implements OnInit, OnDestroy {

  vmid: number;
  loading = true;
  editing = false;
  deleting = false;
  intervals = new Set<Subscription>();
  newVm = new Vm();

  constructor(
    private activatedRoute: ActivatedRoute,
    private router: Router,
    private http: HttpClient,
    public user: User,
    private userService: UserService,
    public authService: AuthService,
    public slugifyPipe: SlugifyPipe
  ) {
  }

  ngOnInit(): void {
    this.user = this.userService.getUser();
    this.user.vms = Array<Vm>();
    this.vmid = this.activatedRoute.snapshot.params.vmid;
    this.get_vm(this.vmid);

  }

  ngOnDestroy(): void {
    for (const id of this.intervals) {
      id.unsubscribe();
    }
  }


  edit(): void {
    this.newVm.ram = this.user.vms[0].ram;
    this.newVm.cpu = this.user.vms[0].cpu;
    this.newVm.disk = this.user.vms[0].disk;
    this.editing = true;
  }


  commit_edit(status: string): void {

    const data = {
      status,
    };

    this.http.patch(this.authService.SERVER_URL + '/vm/' + this.vmid, data).subscribe(rep => {
      this.loading = true;
    }, error => {

      if (error.status === 404) {
        window.alert('VM not found');
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

  delete_vm(): void {
    this.deleting = true;
    this.http.delete(this.authService.SERVER_URL + '/vm/' + this.vmid).subscribe(rep => {
        this.deleting = false;
        this.router.navigate(['vms']);
      },

      error => {

        if (error.status === 404) {
          window.alert('VM not found');
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

  get_vm(vmid): void {
    const vm = new Vm();
    vm.id = vmid;
    this.user.vms.push(vm);

    const newTimer = timer(0, 3000).pipe(
      flatMap(() => this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'})))
      .subscribe(rep => {
          vm.name = rep.body['name'];
          vm.status = rep.body['status'];
          vm.ram = rep.body['ram'];
          vm.disk = rep.body['disk'];
          vm.cpu = rep.body['cpu'];
          if (vm.status === 'running') {
            vm.ip = rep.body['ip'][0];
          }

          if (rep.body['type'] === 'nginx_vm') {
            vm.type = 'web server';
          } else if (rep.body['type'] === 'bare_vm') {
            vm.type = 'bare vm';
          } else {
            vm.type = 'not defined';
          }

          this.loading = false;
        },
        error => {

          if (error.status === 404) {
            window.alert('VM not found');
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

}
