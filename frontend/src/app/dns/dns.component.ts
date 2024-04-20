import {Component, OnDestroy, OnInit} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {User} from '../models/user';
import {UserService} from '../common/services/user.service';
import {AuthService} from '../common/services/auth.service';
import {Utils} from '../common/utils';
import {Dns} from '../models/dns';
import {Subscription, Observable, interval, Subject} from 'rxjs';
import { DnsService } from '../common/services/dns.service';
import { takeUntil, tap } from 'rxjs/operators';


@Component({
  selector: 'app-dns',
  templateUrl: './dns.component.html',
  styleUrls: ['./dns.component.css']
})
export class DnsComponent implements OnInit, OnDestroy {
    dns$!: Observable<Dns[]>; // Observable to get the list of DNS
    updateDnsSubscription: Subscription;
    loading = true;
    newDns = new Dns();
    ipList : string[]; // Observable to get the list of IPs
    intervals = new Set<Subscription>();
    showForm = false;
    errorcode = 201;
    httpErrorMessage = "";
    errorMessage = ""
    timer: Subscription;
    success = false;
    page = 1;
    pageSize = 10;
    private destroy$ = new Subject<void>();

    constructor(private http: HttpClient,
                public user: User,
                private userService: UserService,
                private authService: AuthService,
                  public dnsService: DnsService,
                private utils: Utils) {
    }


    ngOnInit(): void {
        //on souscrit aux valeurs de l'utilisateur au cours du temps
        this.userService.getUserObservable().subscribe((user) => {
            //On attend d'avoir un utilisateur valide, en particulier le freezeState qui prend du temps à être récupéré
            if(user && user.freezeState>=0) {
                this.user = user;
                if (this.user.admin || (this.user.chartevalidated && this.user.freezeState < 3)) {

                    //On souscrit à la liste des DNS chargée au cours du temps
                    this.dns$ = this.dnsService.getDnsList();

                    //On update la liste des ids entrées DNS dans la base de données
                    this.dnsService.updateDnsIds();

                    //On souscrit aux infos des entrées DNS
                    this.updateDnsSubscription = interval(30000).pipe(
                            tap(() => this.dnsService.updateAllDns())
                        ).subscribe();
                    this.getIpsList();
                    
                }
            }
        });
        this.newDns.entry =  "";

    }

    ngOnDestroy(): void {
        //On se désabonne pour éviter les fuites de mémoire
        if(this.updateDnsSubscription){
            this.updateDnsSubscription.unsubscribe();
        }
        this.destroy$.next();
        this.destroy$.complete();
    }


    

    getIpsList(): void {
        this.http.get(this.authService.SERVER_URL + '/ips', {observe: 'response'}).pipe(
          takeUntil(this.destroy$)
        ).subscribe(rep => {
            this.ipList = rep.body["ip_list"];
            console.log(this.ipList)
          },
          error => {
            this.errorcode = error.status;
            this.httpErrorMessage = this.utils.getHttpErrorMessage(this.errorcode)
          });
      }

    

    
    create_dns(dns: Dns): void {
        console.log(dns)
        this.errorMessage = ""
        if (dns.ip == null){
            this.errorcode = 400
                this.errorMessage =  this.utils.getTranslation("dns.entry.errorMessage.required")
                this.httpErrorMessage = this.utils.getHttpErrorMessage(this.errorcode)
        } else if(this.user.chartevalidated) {
            if(!this.check_dns_entry(dns.entry)){
                this.errorcode = 401
                this.errorMessage =  this.utils.getTranslation("dns.entry.errorMessage.forbidden")
                this.httpErrorMessage = this.utils.getHttpErrorMessage(this.errorcode)
            } else if (!this.check_dns_ip(dns.ip)){
                this.errorcode = 401
                this.errorMessage = this.errorMessage =  this.utils.getTranslation("dns.ip.errorMessage.forbidden")
                this.httpErrorMessage = this.utils.getHttpErrorMessage(this.errorcode)
            } else {
                let data = {};
                data = {entry: dns.entry, ip: dns.ip};
                console.log(data)
                this.http.post(this.authService.SERVER_URL + '/dns', data, {observe: 'response'}).subscribe(
                    (rep) => {
                        if (rep.status === 201) {
                            this.success = true;
                            window.location.reload();
                        }  else {
                            this.errorcode = rep.status;
                        }

                    },
                    (error_rep) => {
                        this.errorcode = error_rep.status;
                        this.errorMessage = error_rep.error["error"]
                        this.httpErrorMessage = this.utils.getHttpErrorMessage(this.errorcode)
                    });
            }
        }
    }


    // Check if the DNS entry is correct and respect minet rules
    // TO DO : make a manual validation
    check_dns_entry(entry: string):boolean{
        const forbidden_entries = ["armes", "arme", "fuck", "porn", "porno", "weapon", "weapons", "pornographie", "amazon", "sex", "sexe", "attack", "hack", "attaque", "hacker", "hacking", "pornhub", "xxx", "store", "hosting", "adh6"];
        const authorized_entry = /^[a-zA-Z0-9-._]*$/;
        return authorized_entry.test(entry) && !(entry in forbidden_entries);
    }

    // Check if the ip is for hosting
    // TO DO : make a local check if the user owns the ip
    check_dns_ip(ip: string):boolean{
        const authorized_ip = /^157\.159\.195\.([0-9]|[1-9][0-9]|1[0-9][0-9]|2[0-5][0-5])$/; // At least 157.159.40.xxx > 10 < 255. The backend then checks if the user own the ip
        return authorized_ip.test(ip.trim())
    }

    accept_entry(userid: string, dnsentry: string, dnsip: string): void {
        if(this.user.admin) {
            this.http.post(this.authService.SERVER_URL + '/dns/validation', 
                {
                    userid: userid,
                    dnsentry: dnsentry,
                    dnsip: dnsip
                }, 
                {observe: 'response'}
            )
            .subscribe(
                () => {
                    window.location.reload();
                    console.log("ok");
                },
                error => {
                    console.log("error");
                    this.errorcode = error.status;
                    this.httpErrorMessage = this.utils.getHttpErrorMessage(this.errorcode)
                }
            );
        }
    }
    

    delete_entry(id: string): void {
        if(this.user.chartevalidated || this.user.admin) {
            this.http.delete(this.authService.SERVER_URL + '/dns/' + id, {observe: 'response'})
                .subscribe(
                    () => {
                        window.location.reload();
                    },
                    error => {
                        this.errorcode = error.status;
                        this.httpErrorMessage = this.utils.getHttpErrorMessage(this.errorcode)
                    });
        }
    }
}
