import { Injectable } from '@angular/core';
import { AuthService } from './auth.service';
import { HttpClient, HttpErrorResponse, HttpResponse } from '@angular/common/http';
import { Dns } from 'src/app/models/dns';
import { BehaviorSubject, Observable, merge, of } from 'rxjs';
import { Utils } from '../utils';
import { catchError, finalize, map, switchMap, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class DnsService {

    private dnsIds$: Observable<string[]> = new Observable<string[]>(); // Observable to get the list of DNS IDs
    private dnsSubject: BehaviorSubject<Map<string,Dns>> = new BehaviorSubject<Map<string,Dns>>(new Map()); // Observable to get the list of DNS
    public isUpdatingDnsIds = false; // Boolean to know if the DNS IDs are being updated
    public isUpdatingDns = 0; // Integer to know how many DNS are being updated

    public DNSCount = 0; // Number of DNSs
    public PendingDNSCount = 0; // Number of DNSs in pending state
    public ActiveDNSCount = 0; // Number of DNSs in active state

    constructor(private authService: AuthService,
                private http: HttpClient,
                private utils: Utils,
      ) { }

    /**
     * 
     * @returns Observable<string[]> : Observable that emits the list of DNS IDs each time it changes
     */
    getDnsIds(): Observable<string[]> {
        return this.dnsIds$;
    }

    /**
     * 
     * @returns Observable<Dns[]> : Observable that emits the list of DNS information each time it changes
     */
    getDnsList(): Observable<Dns[]> {
        return this.dnsSubject.pipe(
          map(dnsMap => Array.from(dnsMap.values()))
      );
    }

    /**
     * Update the list of DNS IDs
     * Make a call to the API to get the list of DNS IDs
     * For each DNS ID, add it to the list of DNS
     * Emit the list of DNS IDs on the Observable
     */
    public updateDnsIds(): void {
        if (this.isUpdatingDnsIds) {
            return; // Si la mise à jour est déjà en cours, on ne fait rien
        }

        this.isUpdatingDnsIds = true;

        this.http.get<string[]>(this.authService.SERVER_URL + '/dns').pipe(
            tap((dnsIds: string[]) => {
                dnsIds.forEach((id: string) => {
                    this.addDns(id);
                });
            }),
            catchError(error => {
                console.error("Erreur lors de la récupération des IDs des DNSs: ", error);
                this.isUpdatingDnsIds = false;
                return of([]); // Retourne un Observable qui émet un tableau vide en cas d'erreur
            }),
            finalize(() => {
                this.isUpdatingDnsIds = false;
            })
        ).subscribe(dnsIds => {
            this.dnsIds$ = of(dnsIds);
        });
    }

    /**
     * Update all the information on DNS entries
     * Use the list of DNS IDs to make a call to the API to get the information of each DNS
     * For each DNS, update the information
     * We use merge to execute all the requests in parallel and process the responses as soon as they arrive
     * @returns Observable<number | null> : Observable that emits the error code in case of error
     */
    public updateAllDns(): Observable<number | null> {
        return this.dnsIds$.pipe(
            switchMap((dnsIds: string[]) => {
                const httpRequests = dnsIds.map((id: string) => {
                    this.isUpdatingDns++;
                    return this.http.get(this.authService.SERVER_URL + '/dns/' + id, {observe: 'response'}).pipe(
                        tap(response => {
                            const dns = this.dnsSubject.getValue().get(id); 
                            this.updateDns(response, dns); 
                            this.isUpdatingDns--;
                        }),
                        catchError(error => {
                            console.error(`Erreur lors de la récupération de la VM avec l'ID ${id}: `, error);
                            const dns = this.dnsSubject.getValue().get(id); 
                            this.createErrorDns(dns, error); // Créez un DNS erreur
                            this.isUpdatingDns--;
                            return of(error.code); // Retourne un Observable qui émet l'error code en cas d'erreur
                        })
                    )
                });
                // Exécuter toutes les requêtes en parallèle et traiter les réponses dès qu'elles arrivent
                return merge(...httpRequests);
            })
        );
    }


    /**
     * Update the information of a DNS entry
     * @param response : HttpResponse<unknown> : Response from the API
     * @param dns : Dns : DNS entry to update
     */
    updateDns(response: HttpResponse<unknown>, dns: Dns): void {
        dns.entry = response.body['entry'];
        dns.ip = response.body['ip'];
        dns.user = response.body['user'];
        dns.validated = response.body['validated'];

        if (dns.validated) {
            this.ActiveDNSCount++;
        }
        else {
            this.PendingDNSCount++;
        }

        this.dnsSubject.next(this.dnsSubject.getValue());
    }

    /**
     * Create a DNS entry with an error
     * @param dns : Dns : DNS entry to create
     * @param error : HttpErrorResponse : Error response from the API
     */
    createErrorDns(dns: Dns, error: HttpErrorResponse): void {
        dns.entry = this.utils.getTranslation('dns.error.404');
        dns.ip = "Error " + error.status;
        dns.user = this.utils.getTranslation("dns.type.unknow");
        this.dnsSubject.next(this.dnsSubject.getValue());
    }

    /**
     * Add a DNS entry to the list of DNS entries if it does not already exist and emit the new list
     * @param id : string : ID of the DNS entry
     */
    private addDns(id: string): void {
      const dnsList = this.dnsSubject.getValue();
      if (!dnsList.has(id)) {
        this.DNSCount++;
        const dns = new Dns();
        dns.id = id;
        dnsList.set(id, dns);
        this.dnsSubject.next(dnsList);
      }
    }
  
}
