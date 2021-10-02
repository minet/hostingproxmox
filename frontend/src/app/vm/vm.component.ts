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
    history: any;

    constructor(
        private activatedRoute: ActivatedRoute,
        private router: Router,
        private http: HttpClient,
        public user: User,
        private userService: UserService,
        public authService: AuthService,
        public slugifyPipe: SlugifyPipe,
    ) {
    }

    ngOnInit(): void {
        setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user); }, 1000);
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

    secondsToDhms(seconds): string {
        seconds = Number(seconds);
        const d = Math.floor(seconds / (3600 * 24));
        const h = Math.floor(seconds % (3600 * 24) / 3600);
        const m = Math.floor(seconds % 3600 / 60);
        const s = Math.floor(seconds % 60);

        const dDisplay = d > 0 ? d + 'd ' : '';
        const hDisplay = h > 0 ? h + 'h ' : '';
        const mDisplay = m > 0 ? m + 'min ' : '';
        const sDisplay = s > 0 ? s + 's ' : '';
        return dDisplay + hDisplay + mDisplay + sDisplay;
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
                    if(this.user.admin)
                        this.get_ip_history(vmid);
                    vm.name = rep.body['name'];
                    vm.status = rep.body['status'];
                    vm.ram = rep.body['ram'];
                    vm.disk = rep.body['disk'];
                    vm.cpu = rep.body['cpu'];
                    vm.user = rep.body['user'];
                    vm.autoreboot = rep.body['autoreboot'];
                    vm.ramUsage = rep.body['ram_usage'];
                    vm.cpuUsage = rep.body['cpu_usage'];
                    vm.uptime = rep.body['uptime'];
                    vm.ip = rep.body['ip'][0];
                    vm.createdOn = rep.body['created_on'];
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

    get_ip_history(vmid): void {
        this.http.get(this.authService.SERVER_URL + '/history/' + vmid, {observe: 'response'})
        .subscribe(rep => {
                this.history = rep.body;
            },
            error => {

                if (error.status === 404) {
                    window.alert('VM not found');
                    this.router.navigate(['']);
                } else if (error.status === 403) {
                    window.alert('Session expired or not enough permissions');
                    this.router.navigate(['']);
                } else {
                    window.alert('Unknown error');
                    this.router.navigate(['']);
                }

            });
    }

}
