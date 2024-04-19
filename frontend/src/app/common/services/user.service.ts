import {Injectable} from '@angular/core';
import {AuthService} from './auth.service';
import {User} from '../../models/user';
import {OAuthService} from 'angular-oauth2-oidc';
import {authCodeFlowConfig} from '../../sso.config';
import { BehaviorSubject, merge, Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
@Injectable({
    providedIn: 'root'
})
export class UserService {
    public errorcode = null;
    private discoveryDocument$: Promise<boolean>;
    public errorMessage = null;
    user$: BehaviorSubject<User> = new BehaviorSubject<User>(null);

    

    constructor(private http: HttpClient, 
                private user: User, 
                private authService: AuthService, 
                private oauthService: OAuthService
                ) {
        this.configureSingleSignOn();
    }

    configureSingleSignOn(): void {

        this.oauthService.configure(authCodeFlowConfig);
        this.discoveryDocument$ = this.oauthService.loadDiscoveryDocumentAndTryLogin();
    }

    login(): void {
        this.oauthService.initCodeFlow();

    }

    logout(): void {
        this.oauthService.logOut();
        window.location.href = this.oauthService.logoutUrl;
    }

    

    validToken(): Observable<boolean> {
        const tokenObservable$: Observable<boolean> = new Observable<boolean>((sub) => {
            if (this.oauthService.hasValidAccessToken()) {
                sub.next(true);
            }
        });
        return merge(
            this.discoveryDocument$.then(() => this.oauthService.hasValidAccessToken()),
            tokenObservable$
        );
    }

    check_freezeState(): number {
        this.http.get(this.authService.SERVER_URL + '/account_state/' + this.user.username, {observe: 'response'}).subscribe(rep => {
                console.log(rep)
                return Number(rep.body['freezeState']);
            },
            error => {
                console.log(error)
                if (error.status == 0 ){
                    this.errorcode = 500;
                } else {
                    this.errorcode = error.status;
                }
                this.errorMessage = error.statusText;
                console.log("error code local ", this.errorcode)
                return null;
            });
            return null;
    }

    
    /**
     * Crée un User qui contient toutes les données de la personne connectée sur cette session
     */
    public getUser(): void {
        this.discoveryDocument$.then(() => {
          const user : any = this.oauthService.getIdentityClaims(); 
          if (user != null) {
            this.user.username = user.sub;
            this.user.sn = user.sn;
            this.user.name = user.given_name;
            this.user.admin = false;
            this.oauthService.loadUserProfile().then(r => {
              if (r.attributes['memberOf']) {
                if (r.attributes['memberOf'].indexOf(this.authService.adminDn) > -1) {
                  this.user.admin = true;
                }
              }
              if(r.attributes['signedhosting'] === "false")
                this.user.chartevalidated = false;
              else
                this.user.chartevalidated = true;

              this.http.get(this.authService.SERVER_URL + '/account_state/' + this.user.username, {observe: 'response'}).subscribe(rep => {
                  console.log(rep)
                  this.user.freezeState = Number(rep.body['freezeState']);

                  // On actualise la dernière valeur de l'utilisateur
                  this.user$.next(this.user);
              },
              error => {
                  console.log(error)
                  if (error.status == 0 ){
                      this.errorcode = 500;
                  } else {
                      this.errorcode = error.status;
                  }
                  this.errorMessage = error.statusText;
                  console.log("error getting freeze state ", this.errorcode)
                  // On actualise la dernière valeur de l'utilisateur mais sans le freezeState
                  this.user$.next(this.user);
              });
            });
          } else {
            this.user$.next(null);
          }
        });
      }

      /**
       * Permet de s'abonner à la dernière valeur des données de l'utilisateur
       * @returns Observable<User>
       */
      public getUserObservable(): Observable<User> {
        // Renvoie l'Observable du BehaviorSubject
        return this.user$.asObservable();
      }

    
}
