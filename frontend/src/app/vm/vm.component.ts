import {Component, OnDestroy, OnInit, ViewChild, ElementRef} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Vm} from '../models/vm';
import {HttpClient} from '@angular/common/http';
import {User} from '../models/user';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {SlugifyPipe} from '../pipes/slugify.pipe';
import {Subscription, timer} from 'rxjs';
import {mergeMap} from 'rxjs/operators';
import {Utils} from "../common/utils";


@Component({
    selector: 'app-vm',
    templateUrl: './vm.component.html',
    styleUrls: ['./vm.component.css']
})
export class VmComponent implements OnInit, OnDestroy {
    vmid: number;
    loading = true;
    editing = false;
    errorcode = 201;
    errorDescription = "";
    deletionStatus = "None";
    intervals = new Set<Subscription>();
    newVm = new Vm();
    history: any;
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


    constructor(
        private activatedRoute: ActivatedRoute,
        private router: Router,
        private http: HttpClient,
        public user: User,
        private userService: UserService,
        public authService: AuthService,
        public slugifyPipe: SlugifyPipe,
        private utils : Utils,
        

    ) {
    }
    @ViewChild('updateCloseButton') closeUpdatePopUp: ElementRef;
    @ViewChild('openModalButton') openModalButton: ElementRef;
    @ViewChild('openUpdateButton') openUpdateButton: ElementRef;

    ngOnInit(): void {
        setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user); }, 1000);
        this.user.vms = Array<Vm>();
        this.vmid = this.activatedRoute.snapshot.params.vmid;
        this.start_get_vm(this.vmid);
    }


    startPopUp(){
        try {
            this.openModalButton.nativeElement.click();
            this.popUpShowed = true;
        } catch (error) {
            console.log(error)
        }
       
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

    secondsToDhms(seconds: number): string {
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

        this.http.patch(this.authService.SERVER_URL + '/vm/' + this.vmid, data).subscribe(rep => {
            this.loading = true;
        }, error => {
            this.loading = false;
            this.errorcode = error.status;
        });
    }

    delete_vm(): void {
        this.deletionStatus = "deleting";
        this.errorDescription = "";
        let url = this.authService.SERVER_URL + '/vm/' + this.vmid;
        if(this.vm_has_error ){
            url = this.authService.SERVER_URL + '/vmWithError/' + this.vmid;
        }
        console.log(this.errorDescription)
        console.log(url)
         this.http.delete(url).subscribe(rep => {

            const deletionTimer = timer(0, 3000).pipe(
            mergeMap(() =>  this.http.get(this.authService.SERVER_URL + '/vm/' +this.vmid, {observe: 'response'}))).subscribe(rep => {
                        const vmstate = rep.body['status'];
                        if(vmstate == "deleted"){
                            deletionTimer.unsubscribe();
                            if(this.need_to_be_restored){
                                this.openModalButton.nativeElement.click();
                            }
                            this.deletionStatus = "deleted";
                            setTimeout(() =>this.router.navigate(['vms']), 2000);
                        }
                      },
                    error => {
                        if (error.status == 403 || error.status == 404){ // the vm is deleted 
                            deletionTimer.unsubscribe();
                            this.deletionStatus = "deleted";
                            setTimeout(() =>this.router.navigate(['vms']), 2000);
                        } else {
                            deletionTimer.unsubscribe();
                            this.loading = false;
                              this.errorcode = error.status;
                              this.errorDescription = error.error["error"];
                        }
                       
                          
                    });
                this.intervals.add(deletionTimer);
            },

            error => {
                this.loading = false;
                this.deletionStatus  = "None";
                this.errorcode = error.status;
                this.errorDescription = error.statusText;
            });
    }

    transfer_vm_ownership():void{
        const data = {
            "status" : "transfering_ownership",
            "user": this.new_user_to_transfer
        };
        this.transfering_ownership = true;
        this.http.patch(this.authService.SERVER_URL + '/vm/' + this.vmid, data).subscribe(rep => {
            this.transfering_request_message = "success";
            setTimeout(() => {this.transfering_ownership = false;
            this.transfering_request_message = ""}, 1000);
        }, error => {
            this.transfering_ownership = false;
            this.transfering_request_message = error.error["error"];
        });
    }

    start_get_vm(vmid){
        const vm = new Vm();
        vm.id = vmid;
        this.user.vms.push(vm);
        setInterval(()=> { this.get_vm(vmid, vm) }, 3000); // each 3 s
        if (this.need_to_be_restored == null || !this.popUpShowed){
            this.get_need_to_be_restored(vmid);
        }
    }


    get_vm(vmid, vm): void {
       this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'})
            .subscribe(rep => {

                console.log(rep)
                    if(this.user.admin)
                        this.get_ip_history(vmid);
                    vm.name = rep.body['name'];
                    vm.status = rep.body['status'];
                    vm.ram = String(Math.floor(rep.body['ram']/1000));
                    vm.disk = rep.body['disk'];
                    vm.cpu = rep.body['cpu'];
                    vm.user = rep.body['user'];
                    vm.autoreboot = rep.body['autoreboot'];
                    vm.ramUsage = rep.body['ram_usage'];
                    vm.cpuUsage = rep.body['cpu_usage'];
                    vm.uptime = rep.body['uptime'];
                    vm.lastBackupDate = rep.body['last_backup_date'];
                    vm.isUnsecure = Boolean(rep.body["unsecure"]);
                    if (rep.body['ip'] == ""){
                        vm.ip = ""
                    } else {
                        vm.ip = rep.body['ip'][0];
                    }
                    //console.log("rep = ", rep.body['ip']);
                    vm.createdOn = rep.body['created_on'];
                    if (rep.body['type'] === 'nginx_vm') {
                        vm.type = 'web server';
                    } else if (rep.body['type'] === 'bare_vm') {
                        vm.type = 'bare vm';
                    } else {
                        vm.type = 'not defined';
                    }
                    this.loading = false;
                    console.log("vm.status", vm.status)
                },
                error => {
                    if(error.status == 500 && error.error["error"] == "VM not found in proxmox"){
                       this.vm_has_proxmox_error = true;
                    }
                    this.errorcode = error.status;
                    this.errorDescription = error.error["error"];
                    this.vm_has_error = true;
                    console.log(this.vm_has_error)
                    this.loading = false;
                });
    }

    get_ip_history(vmid): void {
        this.http.get(this.authService.SERVER_URL + '/history/' + vmid, {observe: 'response'})
        .subscribe(rep => {
                this.history = rep.body;
            },
            error => {
                this.errorcode = error.status;
            });
    }

    get_need_to_be_restored(vmid):void{
        this.http.get(this.authService.SERVER_URL + '/needToBeRestored/' + vmid, {observe: 'response'})
        .subscribe(rep => {
            console.log(rep)

                this.need_to_be_restored = rep.body['need_to_be_restored'];
                if(this.need_to_be_restored){
                    this.startPopUp();
                }
            },
            error => {
                this.errorcode = error.status;
                this.errorDescription = error.error["error"];
            });
    }

    renew_vm():void{
        this.renew_vm_status = "loading";
        let data = {};
        data = {
            vmid: this.vmid,
        };
        this.http.post(this.authService.SERVER_URL + '/renew-ip', data, {observe: 'response'}).subscribe(rep => {
            this.renew_vm_status = "reboot" // need reboot to apply
            this.user.vms[0].ip = rep.body['ip'];
        }, 
        error => {
            this.errorcode = error.status;
            this.errorDescription = error.error["error"];
        })
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
        
      this.http.post(this.authService.SERVER_URL + '/updateCredentials', data, {observe: 'response'}).subscribe(rep => {
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

    displayError(errorcode): string {
        this.loading = false; // de toute manière on va pas charger pendant 106 ans
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
