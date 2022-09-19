import {Component, OnDestroy, OnInit} from '@angular/core';
import {Vm} from '../models/vm';
import {HttpClient, HttpHeaders, HttpResponse} from '@angular/common/http';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {User} from '../models/user';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Observable, Subscription, timer} from 'rxjs';
import {mergeMap} from 'rxjs/operators';
import {ActivatedRoute, Router} from "@angular/router";
import {Utils} from "../common/utils";

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
    totalVm = 0;
    pagesAlreadyLoaded = new Array<number>();
    public validToken$: Observable<boolean>;

    constructor(private http: HttpClient,
                private activatedRoute: ActivatedRoute,
                private router: Router,
                public user: User,
                private userService: UserService,
                private utils: Utils,
                public authService: AuthService,
                public slugifyPipe: SlugifyPipe) {
    }

    ngOnInit(): void {
        setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user);
            console.log(this.user)
            this.user.vms = Array<Vm>();
            if((this.user.chartevalidated && this.user.cotisation) || this.user.admin) {
                this.get_vms(); // on laisse une seconde pour charger l'user avant de check si il a validé
            }
        }, 1000);
        this.pagesAlreadyLoaded.push(1);
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

    /**
    * 
    * Get the vm id list and call get_vm with the related id
    *
    */

    get_vms(): void {
        if(this.user.chartevalidated || this.user.admin) {
            let vmList: Array<string>;
            this.http.get(this.authService.SERVER_URL + '/vm', {observe: 'response'}).subscribe(rep => {
                    vmList = rep.body as Array<string>;

                    // Initiate the list to construct all the pages if there aren't already
                    for(let i=0; i<vmList.length; i++){
                        const vm = new Vm();
                        vm.id = vmList[i];
                        this.user.vms.push(vm);
                    }

                    if (vmList.length === 0) {
                        this.loading = false;
                    }

                    this.totalVm = vmList.length;
                    var lastVmDisplayedOnPage = vmList.length

                    if (this.pageSize*this.page < vmList.length){
                        lastVmDisplayedOnPage = this.page*this.pageSize
                    } 
                    for (let i = (this.page-1)*this.pageSize; i < lastVmDisplayedOnPage; i++) {
                        const last = (i === lastVmDisplayedOnPage - 1);
                        this.get_vm(i, last);
                    }
                },
                error => {
                    this.errorcode = error.status;
                });
                
        }
    }

    /**
     *  Call the API in order to retrieve the vm infos related to the id in the list, initiated with vmid in user.vms list
     * 
     * It waits for response before updating vm info 
     * 
     * Every 30s, a new call is made to update vm info
     */



    get_vm(id: number, last: boolean): void {
        let vm = this.user.vms[id]
        const vmid = vm.id;
        const newTimer = timer(0, 30000).pipe(
            mergeMap(() => this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'})))
            .subscribe(rep => {
                    vm.name = rep.body['name'].trim();
                    vm.status = rep.body['status'].trim();
                    vm.user = rep.body['user'];
                    vm.ip = rep.body['ip'][0];
                    vm.uptime = rep.body['uptime'];
                    vm.createdOn = rep.body['created_on'];
                    if (rep.body['type'] === 'nginx_vm') {
                        vm.type = "web_server";
                    } else if (rep.body['type'] === 'bare_vm') {
                        vm.type = "bare_vm";
                    } else {
                        vm.type = "unknow";
                    }

                    if (last) {
                        this.loading = false;
                    }
                },
                error => {
                    vm.name = this.utils.getTranslation('vm.error.404');
                    vm.status = "Error " + error.status;
                    vm.createdOn = this.utils.getTranslation("vms.type.unknow")
                    vm.type = "unknow";
                    if (last) {
                        this.loading = false;
                    }
                    this.errorcode = error.status;
                });
        this.intervals.add(newTimer);
    }


    /**
     *  Click on a new page in ngb-pagination
     *  VM's infos are loaded if it's not already done 
     */

    loadPage(){
        if (!this.pagesAlreadyLoaded.includes(this.page)){
            this.loading = true;
            this.totalVm = this.user.vms.length;
            var lastVmDisplayedOnPage = this.user.vms.length
            if (this.pageSize*this.page < this.user.vms.length){
                lastVmDisplayedOnPage = this.page*this.pageSize
            } 
            for (let i = (this.page-1)*this.pageSize; i < lastVmDisplayedOnPage; i++) {
                const last = (i === lastVmDisplayedOnPage - 1);
                this.get_vm(i, last);
            }
            this.pagesAlreadyLoaded.push(this.page);
        }
    }

}
