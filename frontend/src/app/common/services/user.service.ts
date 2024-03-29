import {Injectable} from '@angular/core';
import {AuthService} from './auth.service';
import {User} from '../../models/user';
import {OAuthService} from 'angular-oauth2-oidc';
import {authCodeFlowConfig} from '../../sso.config';
import {merge, Observable} from 'rxjs';
import {fromPromise} from 'rxjs/internal-compatibility';
import {HttpClient} from '@angular/common/http';

@Injectable({
    providedIn: 'root'
})
export class UserService {
    public errorcode = null;
    private discoveryDocument$: Promise<boolean>;
    public errorMessage = null;
    constructor(private http: HttpClient, private user: User, private authService: AuthService, private oauthService: OAuthService) {
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
            this.discoveryDocument$.then((result) => this.oauthService.hasValidAccessToken()),
            tokenObservable$
        );
    }

    check_freezeState(): void {
        this.http.get(this.authService.SERVER_URL + '/account_state/' + this.user.username, {observe: 'response'}).subscribe(rep => {
                console.log(rep)
                this.user.freezeState = Number(rep.body['freezeState']);
            },
            error => {
                console.log(error)
                if (error.status == 0 ){
                    this.errorcode = 500;
                } else {
                    this.errorcode = error.status;
                }
                this.errorMessage = error.statusText;
                this.user.freezeState = null;
                console.log("error code local ", this.errorcode)
            });
            //this.user.freezeState = 2//Number(rep.body['freezeState']);
    }

    

    

    getUser(): Observable<User> {
        return fromPromise(this.discoveryDocument$.then((result) => {
            const user: any = this.oauthService.getIdentityClaims();
            if (user != null) {
                this.user.username = user.sub;
                this.user.sn = user.sn;
                this.user.name = user.given_name;
                this.user.admin = false;
                this.oauthService.loadUserProfile().then((r: any) => { // Specify the type of 'r' as 'any'
                    if (r.attributes && r.attributes['memberOf']) { // Check if 'attributes' property exists
                        if (r.attributes['memberOf'].indexOf(this.authService.adminDn) > -1) {
                            this.user.admin = true;
                        }
                    }
                    this.check_freezeState();
                    if(r.attributes && r.attributes['signedhosting'] === "false") // Check if 'attributes' property exists
                        this.user.chartevalidated = false;
                    else
                        this.user.chartevalidated = true;
                });
                return this.user;
            } else {
                return null;
            }
        }));

    }
}
