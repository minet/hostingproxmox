import { Component, OnInit } from '@angular/core';
import {User} from '../models/user';
import {Vm} from '../models/vm';
import {UserService} from '../common/services/user.service';
import { Subscription, timer } from 'rxjs';
import { AuthService } from '../common/services/auth.service';
import { HttpClient } from '@angular/common/http';
import { mergeMap } from 'rxjs/operators';
import { Utils } from '../common/utils';

@Component({
  selector: 'app-deletevm',
  templateUrl: './deletevm.component.html',
  styleUrls: ['./deletevm.component.css']
})
export class DeletevmComponent implements OnInit {
  httpPromises = [];
  isLoaded = false;
  pagesAlreadyLoaded = new Array<number>();
  intervals = new Set<Subscription>();
  errorcode = 201;
  expiredUsers = Array<string>();
  vm_has_error = false;
  need_to_be_restored = false;
  errorDescription = "";

  constructor(private http: HttpClient,
    public user: User,
    private userService: UserService,
    private authService: AuthService,
    private utils: Utils,

    ) {
}

ngOnInit(): void {
  setTimeout(() => {  this.userService.getUser().subscribe((user) => this.user = user);
      this.user.vms = Array<Vm>();
      if(this.user.admin) {
            this.get_expired_cotisation_users(); 
      }
  }, 1000);
  this.pagesAlreadyLoaded.push(1);
}

ngOnDestroy(): void {
  for (const id of this.intervals) {
      id.unsubscribe();
  }
}

get_expired_cotisation_users(): void {
  if(this.user.admin) {
      this.expiredUsers = Array<string>();
      this.http.get(this.authService.SERVER_URL + '/expired', {observe: 'response'}).subscribe(rep => {
              console.log("Liste des utilisateurs expirés :" + rep.body);
              this.expiredUsers = rep.body as Array<string>;
              for(let i = 0; i < this.expiredUsers.length; i++) {
                this.httpPromises.push(this.get_expired_vms_from_user(this.expiredUsers[i]));
              }
              Promise.all(this.httpPromises).then(() => {
                this.isLoaded = true;
              });
              


          },
          error => {
              this.errorcode = error.status;
          });
  }
  return null;

}

async get_expired_vms_from_user(user: string) {
  if(this.user.admin) {
    let vmList: Array<string>;
    const url = this.authService.SERVER_URL + '/vm?search=' + user
    this.http.get(url, {observe: 'response'}).subscribe(rep => {
            vmList = rep.body as Array<string>;
            // Initiate the list to construct all the pages if there aren't already
            for(let i=0; i<vmList.length; i++){

                const vm = new Vm();
                vm.id = vmList[i];
                this.user.vms.push(vm);
                this.get_vm(vm);
            }

            if (vmList && vmList.length !== 0) {
              console.log("Liste des VMs de l'utilisateur " + user + " : " + vmList);
            }
            

        },
        error => {
            this.errorcode = error.status;
        });
        
}

}

async get_vm(vm: Vm) {
  const vmid = vm.id;
  const newTimer = timer(0, 30000).pipe(
      mergeMap(() => this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'})))
      .subscribe(rep => {
              vm.name = rep.body['name'].trim();
              vm.user = rep.body['user'];
              vm.status = rep.body['status'];

              vm.createdOn = rep.body['created_on'];

              
          },
          error => {              
              vm.name = this.utils.getTranslation('vm.error.404');
              vm.status = "Error " + error.status;
              vm.createdOn = this.utils.getTranslation("vms.type.unknow")
              vm.type = "unknow";
              this.vm_has_error = true;
              this.errorcode = error.status;
          });
  this.intervals.add(newTimer);
}

delete_vm(vm: Vm): void {
  this.errorDescription = "";
  const vmid = vm.id;
  vm.status = 'deleting';
  console.log(vm.status);
  let url = this.authService.SERVER_URL + '/vm/' + vmid;
  if(this.vm_has_error ){
      url = this.authService.SERVER_URL + '/vmWithError/' + vmid;
  }
  console.log(url)
   this.http.delete(url).subscribe(() => {

      const deletionTimer = timer(0, 3000).pipe(
      mergeMap(() =>  this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, {observe: 'response'}))).subscribe(rep => {
                  const vmstate = rep.body['status'];
                  if(vmstate == "deleted"){
                      deletionTimer.unsubscribe();
                      this.user.vms = this.user.vms.filter(vm => vm.id !== vmid);
                    }
                },
              error => {
                  if (error.status == 403 || error.status == 404){ // the vm is deleted 
                      deletionTimer.unsubscribe();
                  } else {
                      deletionTimer.unsubscribe();
                      this.errorcode = error.status;
                      this.errorDescription = error.error["error"];
                  }
                 
                    
              });
          this.intervals.add(deletionTimer);
      },

      error => {
          this.errorcode = error.status;
          this.errorDescription = error.statusText;
      });
}

}
