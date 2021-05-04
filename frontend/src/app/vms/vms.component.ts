import {Component, OnDestroy, OnInit} from '@angular/core';
import {Vm} from '../models/vm';
import {HttpClient, HttpHeaders, HttpResponse} from '@angular/common/http';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {User} from '../models/user';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {interval, Observable, Subscription, timer} from 'rxjs';
import {flatMap} from 'rxjs/internal/operators';
import {ViewportScroller} from '@angular/common';

@Component({
    selector: 'app-vms',
    templateUrl: './vms.component.html',
    styleUrls: ['./vms.component.css']
})
export class VmsComponent implements OnInit, OnDestroy {
    loading = true;
    intervals = new Set<Subscription>();
    showSsh = false;
    page = 1;
    pageSize = 5;

    constructor(private http: HttpClient,
                public user: User,
                private userService: UserService,
                public authService: AuthService,
                public slugifyPipe: SlugifyPipe,
                private vps: ViewportScroller) {
    }

    ngOnInit(): void {
        this.userService.getUser().subscribe((user) => this.user = user);
        this.user.vms = Array<Vm>();
        this.get_vms();
    }

    ngOnDestroy(): void {
        for (const id of this.intervals) {
            id.unsubscribe();
        }
    }

    scrollSsh($element): void {
        this.showSsh = !this.showSsh;
        if (this.showSsh) {
            $element.scrollIntoView({behavior: 'auto', block: 'start', inline: 'start'});
        }
    }

    get_vms(): void {
        let vmList: Array<string>;
        this.http.get(this.authService.SERVER_URL + '/vm', {observe: 'response'}).subscribe(rep => {
                vmList = rep.body as Array<string>;
                console.log(vmList);
                if (vmList.length === 0) {
                    this.loading = false;
                }
                for (let i = 0; i < vmList.length; i++) {
                    const vmid = vmList[i];
                    const last = (i === vmList.length - 1);
                    this.get_vm(vmid, last);
                    console.log(vmid);
                }
            },
            error => {

            });

    }

    get_vm(vmid: string, last: boolean): void {
        const vm = new Vm();
        vm.id = vmid;
        this.user.vms.push(vm);
        const newTimer = timer(0, 3000).pipe(
            flatMap(() => this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'})))
            .subscribe(rep => {
                    vm.name = rep.body['name'];
                    vm.status = rep.body['status'];
                    vm.user = rep.body['user'];
                    if (rep.body['type'] === 'nginx_vm') {
                        vm.type = 'web server';
                    } else if (rep.body['type'] === 'bare_vm') {
                        vm.type = 'bare vm';
                    } else {
                        vm.type = 'not defined';
                    }

                    if (vm.status === 'running') {
                        vm.ip = rep.body['ip'][0];
                    }

                    if (last) {
                        this.loading = false;
                    }
                },
                error => {

                });
        this.intervals.add(newTimer);
    }

}
