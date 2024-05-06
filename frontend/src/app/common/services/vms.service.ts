import { HttpClient, HttpErrorResponse, HttpResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, Subject, combineLatest, merge, of, timer } from 'rxjs';
import { Vm } from 'src/app/models/vm';
import { AuthService } from './auth.service';
import { catchError, finalize, map, mergeMap, switchMap, take, takeUntil, tap } from 'rxjs/operators';
import { Utils } from '../utils';

@Injectable({
    providedIn: 'root'
  })

export class VmsService {

    private vmIds$: Observable<number[]> = new Observable<number[]>(); // Observable to get the list of VM IDs
    private vmsSubject: BehaviorSubject<Map<number, Vm>> = new BehaviorSubject<Map<number, Vm>>(new Map()); // Observable to get the list of VMs
    private expiredUsersSubject: BehaviorSubject<string[]> = new BehaviorSubject<string[]>([]); // Observable to get the list of expired users
    
    public isUpdatingVms = 0; // Integer to know how many VMs are being updated
    public isUpdatingExpiredUsers = false; // Boolean to know if the expired users are being updated
    public isUpdatingVmIds = false; // Boolean to know if the VM IDs are being updated

    private cancelRequests = new Subject<void>();


    public CPUCount = 0; // Number of CPUs
    public RAMCount = 0; // Amount of RAM
    public DISKCount = 0; // Amount of disk space
    public VMCount = 0; // Number of VMs
    public ActiveVMCount = 0; // Number of active VMs

    public vmToRestoreCounter = 0;

    
    constructor(private http: HttpClient,
        private authService: AuthService,
        private utils: Utils,
        ) { }


    /**
     * 
     * @returns Observable<number[]> : Observable that emits the list of VM IDs each time it changes
     */
    public getVmIds(): Observable<number[]> {
      return this.vmIds$;
    }

    /**
     * 
     * @returns Observable<Vm[]> : Observable that emits the list of VMs each time it is updated
     */
    public getVms(): Observable<Vm[]> {
        return this.vmsSubject.pipe(
            map(vmsMap => Array.from(vmsMap.values()))
        );
    }

    /**
     * 
     * @param vmid : number : ID of the VM to get
     * @returns Observable<Vm> : Observable that emits the VM with the given ID each time it is updated
     */
    public getVm(vmid: number): Observable<Vm> {
        return this.vmsSubject.pipe(
            map(vmsMap => vmsMap.get(vmid))
        );
    }

    /**
     * 
     * @returns Observable<Vm[]> : Observable that emits the list of VMs that should be deleted each time it is updated
    */
    public getVmsToDelete(): Observable<Vm[]> {
        // Update the list of expired users each time one theses two observables changes
        return combineLatest([this.vmsSubject, this.expiredUsersSubject]).pipe(
            map(([vms, expiredUsers]) => {
                const expiredVms: Vm[] = [];
                if (expiredUsers.length > 0) {
                    vms.forEach((vm) => {
                        if (expiredUsers.includes(vm.user)) {
                            expiredVms.push(vm);
                        }
                    });
                }
                return expiredVms;
            })
        );
    }

    /**
     * 
     * @returns Observable<string[]> : Observable that emits the list of expired users each time it is updated
     */
    public getExpiredUsers(): Observable<string[]> {

        return this.expiredUsersSubject.asObservable();
    }

    /**
     * Update the list of VM IDs
     * Make a call to the API to get the list of VM IDs
     * For each VM ID, create a VM and add it to the list of VMs
     * Emit the list of VM IDs on the Observable
     */
    public updateVmIds(): void {

        //Si une requête est déjà en cours, ne pas en lancer une autre
        if (this.isUpdatingVmIds) {
            return;
        }
        this.isUpdatingVmIds = true;

        this.vmIds$ = this.http.get<number[]>(this.authService.SERVER_URL + '/vm').pipe(
            tap((vmIds: number[]) => {
                vmIds.forEach((vmid: number) => {
                    this.addVm(vmid);
                });
            }),
            catchError(error => {
                console.error("Erreur lors de la récupération des IDs des VMs: ", error);
                return of([]); // Retourne un Observable qui émet un tableau vide en cas d'erreur
            }),
            finalize(() => {
                this.isUpdatingVmIds = false;
            })
        )
    }

    /**
     * Update the information of the VMs in the list
     * Make a call to the API to get the information of each VM
     * For each VM, update the information in the list
     * We use merge to execute all the requests in parallel and process the responses as soon as they arrive
     */
    public updateVms(startIndex: number): void {
        
        //Si une requête est déjà en cours, ne pas en lancer une autre
        if (this.isUpdatingVms > 0) {
            return;
        }
        
        this.vmIds$.pipe(
            switchMap((vmIds: number[]) => {

                const slicedVmIds = vmIds.slice(startIndex);

                // Créer un tableau d'Observables pour chaque requête HTTP
                const httpRequests = slicedVmIds.map((vmid: number) => {

                    this.isUpdatingVms++; // Incrémenter le compteur de requêtes en cours

                    return this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, { observe: 'response' }).pipe(
                        takeUntil(this.cancelRequests),
                        tap(response => {
                            this.addVm(vmid); // Ajouter la VM au Subject
                            const vm = this.vmsSubject.getValue().get(vmid); 
                            this.updateVmFromResponse(response, vm); // Créer la VM à partir de la réponse HTTP
                            this.isUpdatingVms--; // Décrémenter le compteur de requêtes en cours
                        }),
                        catchError(error => {
                            console.error(`Erreur lors de la récupération de la VM avec l'ID ${vmid}: `, error);
                            this.addVm(vmid); // Ajouter la VM au Subject
                            const vm = this.vmsSubject.getValue().get(vmid); 
                            this.createErrorVm(vm, error); // Créez une VM erreur
                            this.isUpdatingVms--; // Décrémenter le compteur de requêtes en cours
                            
                            return of(null); // Retourne un Observable qui émet 'null' en cas d'erreur
                        })
                    );
                });
                // Exécuter toutes les requêtes en parallèle et traiter les réponses dès qu'elles arrivent
                return merge(...httpRequests);
            })
        ).subscribe();
    }

    /**
     * Update the information of the VM with the given ID in the list
     * Make a call to the API to get the information of the VM
     * Add the VM to the list if it does not exist
     * Update the information of this VM in the list
     * return an Observable that emits information about the update
     */
    public updateVm(vmid: number): Observable<{ errorcode: number, errorDescription: string, vm_has_error: boolean, vm_has_proxmox_error: boolean }> {
        return new Observable<{ errorcode: number, errorDescription: string, vm_has_error: boolean, vm_has_proxmox_error: boolean }>(observer => {
            this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, { observe: 'response' }).pipe(
                tap(response => {
                    this.addVm(vmid); // Ajouter la VM au Subject
                    const vm = this.vmsSubject.getValue().get(vmid); // Récupérer la VM à partir du Subject
                    this.updateVmFromResponse(response, vm); // Créer la VM à partir de la réponse HTTP
                }),
                catchError(error => {
                    console.error(`Erreur lors de la récupération de la VM avec l'ID ${vmid}: `, error);
                    this.addVm(vmid); // Ajouter la VM au Subject
                    const vm = this.vmsSubject.getValue().get(vmid); // Récupérer la VM à partir du Subject
                    this.createErrorVm(vm, error); // Créez une VM par défaut
                    return of({ errorcode: error.status, errorDescription: error.error["error"], vm_has_error: true, vm_has_proxmox_error: false });
                })
            ).subscribe(() => {
                observer.next({ errorcode: 201, errorDescription: "", vm_has_error: false, vm_has_proxmox_error: false });
                observer.complete();
            });
        });
    }

    /**
     * Delete the VM with the given ID
     * Make a call to the API to delete the VM
     * Then, check if the VM is deleted by making a call to the API every 3 seconds
     * return an Observable that emits information about the deletion during the process
     */
    public deleteVm(vmid: number, vmHasError: boolean): Observable<{ deletionStatus: string, errorcode: number, errorDescription: string }> {
        let url = this.authService.SERVER_URL + '/vm/' + vmid;
        if (vmHasError) {
            url = this.authService.SERVER_URL + '/vmWithError/' + vmid;
        }

        const unsubscribeTimer = new Subject();
        const maxAttempt = 20;

        return new Observable<{ deletionStatus: string, errorcode: number, errorDescription: string }>(observer => {
            this.http.delete(url).subscribe(() => {
                timer(0, 3000).pipe(
                    take(maxAttempt), //Si on a atteint le nombre maximum de tentatives, arrêter le timer
                    takeUntil(unsubscribeTimer),  //Arrêter le timer si la requête est terminée
                    mergeMap(() => this.http.get(this.authService.SERVER_URL + '/vm/' + vmid, { observe: 'response' }))
                ).subscribe(rep => {
                    const vmstate = rep.body['status'];
                    if (vmstate == "deleted") {
                        //wipe out les vms pour recalculer les ressources
                        this.vmIds$ = of([]);
                        this.vmsSubject.next(new Map());
                        this.VMCount = 0;
                        this.CPUCount = 0;
                        this.RAMCount = 0;
                        this.DISKCount = 0;
                        this.ActiveVMCount = 0;
                        this.vmToRestoreCounter = 0;

                        this.updateVmIds();
                        this.updateVms(0);

                        
                        unsubscribeTimer.next();
                        observer.next({ deletionStatus: "deleted", errorcode: null, errorDescription: null });
                        observer.complete();
                    }
                },
                    error => {
                        if (error.status == 403 || error.status == 404) { // the vm is deleted 
                            //wipe out les vms pour recalculer les ressources
                            this.vmIds$ = of([]);
                            this.vmsSubject.next(new Map());
                            this.VMCount = 0;
                            this.CPUCount = 0;
                            this.RAMCount = 0;
                            this.DISKCount = 0;
                            this.ActiveVMCount = 0;
                            this.vmToRestoreCounter = 0;
                            
                            this.updateVmIds();
                            this.updateVms(0);
                            
                            
                            unsubscribeTimer.next();
                            observer.next({ deletionStatus: "deleted", errorcode: null, errorDescription: null });
                            observer.complete();
                        } else {
                            unsubscribeTimer.next();
                            console.error(`Erreur lors de la suppression de la VM avec l'ID ${vmid}: `, error);
                            observer.next({ deletionStatus: "None", errorcode: error.status, errorDescription: error.error["error"] });
                            observer.complete();
                        }
                    });
            },
                error => {
                    console.error(`Erreur lors de la suppression de la VM avec l'ID ${vmid}: `, error);
                    observer.next({ deletionStatus: "None", errorcode: error.status, errorDescription: error.statusText });
                    observer.complete();
                });
        });
    }


    public renewVm(vmid: number):Observable<{ renew_vm_status: string, errorcode: number, errorDescription: string }> {
        let data = {};
        data = {
            vmid: vmid,
        };
        return new Observable<{ renew_vm_status: string, errorcode: number, errorDescription: string }>(observer => {
            this.http.post(this.authService.SERVER_URL + '/renew-ip', data, { observe: 'response' }).subscribe(rep => {
                this.vmsSubject.getValue().get(vmid).ip = rep.body['ip'][0];
                observer.next({ renew_vm_status: "reboot", errorcode: null, errorDescription: null });
                observer.complete();
            },
                error => {
                    observer.next({ renew_vm_status: null, errorcode: error.status, errorDescription: error.error["error"] });
                    observer.complete();
                });
        });
    }

    /**
     * Update the list of expired users
     * Make a call to the API to get the list of expired users
     * Emit the list of expired users on the Observable
     */
    public updateExpiredCotisationUsers(): void {
        this.http.get<string[]>(this.authService.SERVER_URL + '/expired', {observe: 'response'}).pipe(
          map(response => response.body),
          catchError(error => {
            console.error("Erreur lors de la récupération des utilisateurs expirés: ", error);
            return of([]);
          })
        ).subscribe(expiredUsers => {
          // Mettez à jour expiredUsers$ avec les nouveaux utilisateurs expirés
          this.expiredUsersSubject.next(expiredUsers);
        });
      }
      

    /**
     * fill the fields of the VM with the error message
     * @param vm : Vm : VM with an error
     * @param error : HttpErrorResponse : Error response from the API
     */
    private createErrorVm(vm: Vm, error: HttpErrorResponse): void {
        vm.name = this.utils.getTranslation('vm.error.404');
        vm.status = "Error " + error.status;
        vm.createdOn = this.utils.getTranslation("vms.type.unknow")
        vm.type = "unknow";
        vm.hasError = true;
        this.get_need_to_be_restored(vm, true)
        this.vmsSubject.next(this.vmsSubject.getValue());
    }
    
    /**
     * update the fields of the VM with the response and update the counters
     * @param response : HttpResponse<unknown> : Response from the API to update the VM
     * @param vm : Vm : VM to update
     */
    private updateVmFromResponse(response: HttpResponse<unknown>, vm: Vm): void {
        
        if(vm.name == undefined){ //On compte que les Vms qui n'ont jamais été définies
            this.CPUCount += +response.body['cpu'];
            this.RAMCount += Math.floor(response.body['ram']/1000);
            this.DISKCount += +response.body['disk'];
            if (response.body['status'] == "running"){
                this.ActiveVMCount += 1;
            }
        }
        
        vm.name = response.body['name'].trim();
        vm.status = response.body['status'];
        vm.ram = String(Math.floor(response.body['ram']/1000));
        vm.disk = response.body['disk'];
        vm.cpu = response.body['cpu'];
        vm.user = response.body['user'];
        vm.autoreboot = response.body['autoreboot'];
        vm.ramUsage = response.body['ram_usage'];
        vm.cpuUsage = response.body['cpu_usage'];
        vm.uptime = response.body['uptime'];
        vm.lastBackupDate = response.body['last_backup_date'];
        if (response.body['ip'] == ""){
            vm.ip = ""
        } else {
            vm.ip = response.body['ip'][0];
        }
        vm.createdOn = response.body['created_on'];
        vm.isUnsecure = Boolean(response.body["unsecure"]);
        if (response.body['type'] === 'nginx_vm') {
        vm.type = "web_server";
        } else if (response.body['type'] === 'bare_vm') {
        vm.type = "bare_vm";
        } else {
        vm.type = "unknown";
        }
        vm.hasError = false;
        this.get_need_to_be_restored(vm, false)
        this.vmsSubject.next(this.vmsSubject.getValue());
    }
    
    /**
     * Add a Vm to the list of VMs if it does not already exist and emit the new list
     * Count the number of VMs
     * @param vmid : number : ID of the VM to add
     */
    private addVm(vmid: number): void {
        const vms = this.vmsSubject.getValue();
        if(!vms.has(vmid)){
            this.VMCount += 1;
            const vm = new Vm();
            vm.id = vmid;
            vms.set(vmid, vm);
            this.vmsSubject.next(vms);
        }
    }
    
    // Check if a VM need to be restored
    get_need_to_be_restored(vm: Vm, didAnErrorOccur: boolean):void{
        this.http.get(this.authService.SERVER_URL + '/needToBeRestored/' + vm.id, {observe: 'response'}).pipe(takeUntil(this.cancelRequests))
        .subscribe(rep => {
            const needToBeRestored = Boolean(rep.body['need_to_be_restored']);
                if(needToBeRestored){
                    console.log("needToBeRestored", needToBeRestored)
                    if (needToBeRestored && didAnErrorOccur){// If the VM is not found, and need to be restored, then it data are lost
                        vm.name = ""
                        vm.status = "Error: Your VM data is lost. Click to see more details."
                        vm.createdOn = ""
                        vm.type = "unknow";
                    } else if (needToBeRestored && !didAnErrorOccur){ // juste incremente the number of vm to be restored
                        this.vmToRestoreCounter += 1
                    }
                }
                 
            });
            return null;
    }

    public cancelUpdateVms(): void {
        this.cancelRequests.next(); // Annule les requêtes en cours

        let length:number
        const temp = this.isUpdatingVms;
        this.vmIds$.subscribe((vms: number[]) => {
            length = vms.length;
            this.isUpdatingVms = 0; // Réinitialise le compteur
            this.updateVms(Math.max(length-temp-3, 0)); // Relance la mise à jour des VMs
          });
        
    }

}