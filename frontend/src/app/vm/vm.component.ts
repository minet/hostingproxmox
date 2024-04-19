import {Component, OnDestroy, OnInit, ViewChild, ElementRef} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Vm} from '../models/vm';
import {HttpClient} from '@angular/common/http';
import {User} from '../models/user';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Observable, Subscription, interval, of} from 'rxjs';
import {switchMap} from 'rxjs/operators';
import {Utils} from "../common/utils";
import { VmsService } from '../common/services/vms.service';


@Component({
    selector: 'app-vm',
    templateUrl: './vm.component.html',
    styleUrls: ['./vm.component.css']
})
export class VmComponent implements OnInit, OnDestroy {
    vmid: number;
    vm$!: Observable<Vm>;
    updateVmSubscription: Subscription;
    
    errorcode = 0;
    errorDescription = "";
    deletionStatus = "None";
    history: [string, string, string, string];
    input_vm_id = ""; // for the deletion pop up
    vm_has_error = false;
    vm_has_proxmox_error = false;
    need_to_be_restored = null; 
    popUpShowed = false; 
    popUpErrorCode = 0;
    popUpErrorMessage = "";
    popUpUsername ="";
    popUpPassword = "";
    popUpSSHkey = "";
    popUpLoading = false;
    renew_vm_status = "";
    new_user_to_transfer="";
    transfering_ownership=false;
    transfering_request_message="";
    editing = false;

    constructor(
        private activatedRoute: ActivatedRoute,
        private router: Router,
        private http: HttpClient,
        public user: User,
        private userService: UserService,
        public authService: AuthService,
        private vmsService: VmsService,
        public slugifyPipe: SlugifyPipe,
        private utils : Utils,
        

    ) {
    }
    @ViewChild('updateCloseButton') closeUpdatePopUp: ElementRef;
    @ViewChild('openModalButton') openModalButton: ElementRef;
    @ViewChild('openUpdateButton') openUpdateButton: ElementRef;

    ngOnInit(): void {
        //on souscrit aux valeurs de l'utilisateur au cours du temps
        this.userService.getUserObservable().subscribe((user) => {
            //On attend d'avoir un utilisateur valide, en particulier le freezeState qui prend du temps à être récupéré
            if(user && user.freezeState >= 0) {
                this.user = user;
                this.vmid = +this.activatedRoute.snapshot.params.vmid; //On récupère l'id de la vm dans l'url
                this.vm$ = this.vmsService.getVm(this.vmid); //On souscrit aux infos de la vm
                if (this.user.admin) {
                    this.getIpHistory(this.vmid);
                }
                //On update les infos sur la vm toutes les 3s
                this.updateVmSubscription = interval(3000).pipe(
                    switchMap(() => {
                        if (this.deletionStatus !== "deleting" && this.errorcode !== 500 && this.errorcode !== 403) {
                            return this.vmsService.updateVm(this.vmid);
                        } else {
                            return of(null); // Return an empty observable if deletionStatus is 'deleting'
                        }
                    })
                ).subscribe((response) => {
                    if (this.deletionStatus !== "deleting") {
                        this.errorcode = response.errorcode;
                        this.errorDescription = response.errorDescription;
                        this.vm_has_error = response.vm_has_error;
                        this.vm_has_proxmox_error = response.vm_has_proxmox_error;
                    }
                });

        
            }
        });
        
    }


    startPopUp(){
        try {
            this.openModalButton.nativeElement.click();
            this.popUpShowed = true;
        } catch (error) {
            console.log(error)
        }
       
    }
    

    ngOnDestroy() {
        // Important de se désabonner pour éviter les fuites de mémoire
        if (this.updateVmSubscription) {
          this.updateVmSubscription.unsubscribe();
        }
      }


    // edit(): void {
    //     this.newVm.ram = this.user.vms[0].ram;
    //     this.newVm.cpu = this.user.vms[0].cpu;
    //     this.newVm.disk = this.user.vms[0].disk;
    //     this.editing = true;
    // }


    
    formatTimestamp(timestamp: number): string {
        const date = new Date(timestamp*1000);
        const year = date.getFullYear();
        const month = (date.getMonth() + 1).toString().padStart(2, '0');
        const day = date.getDate().toString().padStart(2, '0');
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        
        return `${year}-${month}-${day} ${hours}:${minutes}`;
      }


    commit_edit(status: string): void {
        const data = {
            status,
        };

        this.http.patch(this.authService.SERVER_URL + '/vm/' + this.vmid, data).subscribe(() => {
            return;
        }, error => {
            this.errorcode = error.status;
        });
    }

    

    transfer_vm_ownership():void{
        const data = {
            "status" : "transfering_ownership",
            "user": this.new_user_to_transfer
        };
        this.transfering_ownership = true;
        this.http.patch(this.authService.SERVER_URL + '/vm/' + this.vmid, data).subscribe(() => {
            this.transfering_request_message = "success";
            setTimeout(() => {this.transfering_ownership = false;
            this.transfering_request_message = ""}, 1000);
        }, error => {
            this.transfering_ownership = false;
            this.transfering_request_message = error.error["error"];
        });
    }

    deleteVm(): void {
        this.deletionStatus = "deleting";
        this.errorDescription = "";
        this.vmsService.deleteVm(this.vmid, this.vm_has_error).subscribe((response) => {
            this.deletionStatus = response.deletionStatus;
            this.errorcode = response.errorcode;
            this.errorDescription = response.errorDescription;
            if (response.deletionStatus == "deleted") {
                if (this.need_to_be_restored) {
                    this.openModalButton.nativeElement.click();
                }
                //On attend 2s avant de rediriger vers la page des VMs
                //On en profite pour mettre à jour les VMs
                this.vmsService.updateVmIds();
                this.vmsService.updateVms();
                setTimeout(() => this.router.navigate(['vms']), 2000);
            }
        });
    }

    // start_get_vm(vmid){
    //     const vm = new Vm();
    //     vm.id = vmid;
    //     this.user.vms.push(vm);
    //     setInterval(()=> { this.get_vm(vmid, vm) }, 3000); // each 3 s
    //     if (this.need_to_be_restored == null || !this.popUpShowed){
    //         this.get_need_to_be_restored(vmid);
    //     }
    // }

    renewVm():void{
        this.renew_vm_status = "loading";
        this.vmsService.renewVm(this.vmid).subscribe((response) => {
            this.renew_vm_status = response.renew_vm_status;
            this.errorcode = response.errorcode;
            this.errorDescription = response.errorDescription;
        });
    }

    
    public getIpHistory(vmid: number): void {
        this.http.get(this.authService.SERVER_URL + '/history/' + vmid, { observe: 'response' })
            .subscribe(
                rep => {
                    
                    this.history = rep.body as [string, string, string, string];
                },
                error => {
                    console.error(`Erreur lors de la récupération de l'historique des IPs de la VM avec l'ID ${vmid}: `, error);
                    this.errorcode = error.status;
                    this.history = ["", "", "", ""];
                }
            );
        this.history = ["", "", "", ""];
    }


    update_vm_credentials(): void {
        console.log("test")
        let data = {};
        data = {
            vmid: Number(this.vmid),
          username: this.popUpUsername,
            password: this.popUpPassword,
            sshKey: this.popUpSSHkey,
        };
        this.popUpLoading = true;
        
      this.http.post(this.authService.SERVER_URL + '/updateCredentials', data, {observe: 'response'}).subscribe(() => {
        console.log("success")
        this.popUpLoading = false;
        if(this.need_to_be_restored){
            this.openModalButton.nativeElement.click();
            this.openUpdateButton.nativeElement.click();
        } else {
            
            this.closeUpdatePopUp.nativeElement.click();
        }
        this.popUpShowed = false;
        this.popUpErrorCode = 0;
        this.popUpErrorMessage = "";
        this.commit_edit("reboot")
        console.log("success2")
        }, error => {
            this.popUpErrorCode = error.status;
            const httpError = this.utils.getHttpErrorMessage(error.status);
            this.popUpErrorMessage = "<b>Error " + this.popUpErrorCode + " : "+ httpError + "</b><br><br>" + error.error["status"];
            this.popUpLoading = false;
        });
    }

    displayError(errorcode: number): string {
        switch(errorcode) {
            case 500:
                return this.utils.getTranslation('vm.error.500');
                break;
            case 404:
                return this.utils.getTranslation('vm.error.404');
                break;
            case 403:
                return this.utils.getTranslation('vm.error.403');
                break;
        }
    }

}
