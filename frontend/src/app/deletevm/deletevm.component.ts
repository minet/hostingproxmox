import { Component, OnInit } from '@angular/core';
import {User} from '../models/user';
import {UserService} from '../common/services/user.service';
import { VmsService } from '../common/services/vms.service';
import { Vm } from '../models/vm';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-deletevm',
  templateUrl: './deletevm.component.html',
  styleUrls: ['./deletevm.component.css']
})
export class DeletevmComponent implements OnInit {
  
  errorcode = 201;
  errorDescription = "";
  vmsToDelete$: Observable<Vm[]>;
  expiredUsers$: Observable<string[]>;

  constructor(public user: User,
              private userService: UserService,
              private vmsService: VmsService,
              ) { }

  ngOnInit(): void {
      //on souscrit aux valeurs de l'utilisateur au cours du temps
      this.userService.getUserObservable().subscribe((user) => {
          //On attend d'avoir un utilisateur valide, en particulier le freezeState qui prend du temps à être récupéré
          if (user && user.freezeState >= 0) {
              this.user = user;
              if (this.user.admin) {

                  //On souscrit à la liste des VMs à supprimer et des utilisateurs expirés
                  //Ces derniers ont été chargés au démarrage de l'app
                  this.expiredUsers$ = this.vmsService.getExpiredUsers();
                  this.vmsToDelete$ = this.vmsService.getVmsToDelete();
              }
          }
      });
  }

  deleteVm(vm: Vm): void {
      this.errorDescription = "";
      const vmid = +vm.id;
      vm.status = 'deleting';
      this.vmsService.deleteVm(vmid, vm.hasError).subscribe(
          () => {
            // Handle success response
          },
          (error) => {
            this.errorcode = error.status;
            this.errorDescription = error.statusText;
          }
      );
  }

}
