import {Component, OnDestroy, OnInit} from '@angular/core';
import {Vm} from '../models/vm';
import {HttpClient, HttpHeaders, HttpResponse} from '@angular/common/http';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {User} from '../models/user';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Observable, Subscription, timer} from 'rxjs';
import {flatMap} from 'rxjs/internal/operators';
import {ActivatedRoute, Router} from "@angular/router";

@Component({
    selector: 'app-vms',
    templateUrl: './vms.component.html',
    styleUrls: ['./vms.component.css']
})
export class VmsComponent implements OnInit, OnDestroy {
    loading = true;
    intervals = new Set<Subscription>();
    showSsh = false;
    errorcode = 201;
    page = 1;
    pageSize = 10;
    public validToken$: Observable<boolean>;
    constructor(private http: HttpClient,
                private activatedRoute: ActivatedRoute,
                private router: Router,
                public user: User,
                private userService: UserService,
                public authService: AuthService,
                public slugifyPipe: SlugifyPipe, ) {
    }

    ngOnInit(): void {
        setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user);
            this.user.vms = Array<Vm>();
            if((this.user.chartevalidated && this.user.cotisation) || this.user.admin) {
                this.get_vms(); // on laisse une seconde pour charger l'user avant de check si il a validé
            }
        }, 1000);
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

    get_vms(): void {
        if(this.user.chartevalidated || this.user.admin) {
            let vmList: Array<string>;
            this.http.get(this.authService.SERVER_URL + '/vm', {observe: 'response'}).subscribe(rep => {
                    vmList = rep.body as Array<string>;
                    if (vmList.length === 0) {
                        this.loading = false;
                    }
                    for (let i = 0; i < vmList.length; i++) {
                        const vmid = vmList[i];
                        const last = (i === vmList.length - 1);
                        this.get_vm(vmid, last);
                    }
                },
                error => {
                    this.errorcode = error.status;
                });
        }
    }

    get_vm(vmid: string, last: boolean): void {
        const vm = new Vm();
        vm.id = vmid;
        this.user.vms.push(vm);
        const newTimer = timer(0, 15000).pipe(
            flatMap(() => this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'})))
            .subscribe(rep => {
                    vm.name = rep.body['name'];
                    vm.status = rep.body['status'];
                    vm.user = rep.body['user'];
                    vm.ip = rep.body['ip'][0];
                    vm.uptime = rep.body['uptime'];
                    vm.createdOn = rep.body['created_on'];
                    if (rep.body['type'] === 'nginx_vm') {
                        vm.type = 'web server';
                    } else if (rep.body['type'] === 'bare_vm') {
                        vm.type = 'bare vm';
                    } else {
                        vm.type = 'not defined';
                    }

                    if (last) {
                        this.loading = false;
                    }
                },
                error => {
                    this.errorcode = error.status;
                });
        this.intervals.add(newTimer);
    }

}
