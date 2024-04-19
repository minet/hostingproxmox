import {Component, OnDestroy, OnInit} from '@angular/core';
import {Vm} from '../models/vm';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {User} from '../models/user';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {BehaviorSubject, Observable, Subscription, combineLatest, interval} from 'rxjs';
import { VmsService } from '../common/services/vms.service';
import { map, tap } from 'rxjs/operators';

@Component({
    selector: 'app-vms',
    templateUrl: './vms.component.html',
    styleUrls: ['./vms.component.css']
})

export class VmsComponent implements OnInit, OnDestroy {
    showSsh = false;
    errorcode = 201;
    searchFilter = "";
    searchFilter$ = new BehaviorSubject(this.searchFilter);
    vmToRestoreCounter = 0; // Number VMs that need to be restored
    
    vms$!: Observable<Vm[]>;
    updateVmSubscription: Subscription;


    constructor(private userService: UserService,
                public vmsService: VmsService,
                public user: User,
                public authService: AuthService,
                public slugifyPipe: SlugifyPipe) {
    }

    ngOnInit(): void {
        //on souscrit aux valeurs de l'utilisateur au cours du temps
        this.userService.getUserObservable().subscribe((user) => {
            //On attend d'avoir un utilisateur valide, en particulier le freezeState qui prend du temps à être récupéré
            if(user && user.freezeState >= 0) {
                this.user = user;
                if(this.user.chartevalidated || this.user.admin) {

                    //On update les infos sur les vms toutes les 40s
                    this.updateVmSubscription = interval(40000).pipe(
                        tap(() => {
                            this.vmsService.updateVmIds();
                            this.vmsService.updateVms();
                        })
                    ).subscribe();

                    //Cette observable est actualisé à chaque vm chargée ou à chaque recherche
                    //Elle permet de filtrer les vms en fonction de la recherche
                    this.vms$ = combineLatest([
                        this.vmsService.getVms(),
                        this.searchFilter$
                      ]).pipe(
                        map(([vms]) => 
                          vms.filter(vm => 
                          this.searchFilter == "" || 
                          (vm.name && vm.name.includes(this.searchFilter)) || 
                          (vm.id && String(vm.id).includes(this.searchFilter)) || 
                          (vm.user && vm.user.includes(this.searchFilter))
                        ))
                      );
                    console.log(this.user)
                }
            }
        });
    }


    ngOnDestroy(): void {
        // Important de se désabonner pour éviter les fuites de mémoire
        this.updateVmSubscription.unsubscribe();
    }

    scrollSsh($element): void {
        this.showSsh = !this.showSsh;
        if (this.showSsh) {
            $element.scrollIntoView({behavior: 'auto', block: 'start', inline: 'start'});
        }
    }

    /**
     * Lorsqu'on clique sur le bouton de recherche
     */
    search(): void {
        this.searchFilter$.next(this.searchFilter);
    }

    /**
    * 
    * Get the vm id list and call get_vm with the related id
    *
    */

    // get_vms(): void {
    //     // this.user.vms = Array<Vm>();
    //     if(this.user.chartevalidated || this.user.admin) {
    //         this.loading = true;
    //         let vmList: Array<string>;
    //         let url = this.authService.SERVER_URL + '/vm'
    //         if(this.searchFilter != ""){
    //             url += '?search=' + this.searchFilter
    //         }
    //         this.http.get(url, {observe: 'response'}).subscribe(rep => {
    //                 vmList = rep.body as Array<string>;

    //                 // Initiate the list to construct all the pages if there aren't already
    //                 for(let i=0; i<vmList.length; i++){
    //                     const vm = new Vm();
    //                     vm.id = vmList[i];
    //                     // this.user.vms.push(vm);
    //                 }

    //                 if (vmList.length === 0) {
    //                     this.loading = false;
    //                 }

    //                 this.totalVm = vmList.length;
    //                 let lastVmDisplayedOnPage = vmList.length

    //                 if (this.pageSize*this.page < vmList.length){
    //                     lastVmDisplayedOnPage = this.page*this.pageSize
    //                 } 
    //                 for (let i = (this.page-1)*this.pageSize; i < lastVmDisplayedOnPage; i++) {
    //                     const last = (i === lastVmDisplayedOnPage - 1);
    //                     this.get_vm(i, last);
    //                 }
    //             },
    //             error => {
    //                 this.loading = false;
    //                 this.errorcode = error.status;
    //             });
                
    //     }
    // }


    /**
     *  Click on a new page in ngb-pagination
     *  VM's infos are loaded if it's not already done 
     */

    // loadPage(){
    //     if (!this.pagesAlreadyLoaded.includes(this.page)){
    //         this.loading = true;
    //         this.totalVm = this.user.vms.length;
    //         let lastVmDisplayedOnPage = this.user.vms.length
    //         if (this.pageSize*this.page < this.user.vms.length){
    //             lastVmDisplayedOnPage = this.page*this.pageSize
    //         } 
    //         for (let i = (this.page-1)*this.pageSize; i < lastVmDisplayedOnPage; i++) {
    //             const last = (i === lastVmDisplayedOnPage - 1);
    //             this.get_vm(i, last);
    //         }
    //         this.pagesAlreadyLoaded.push(this.page);
    //     }
    // }   

}
