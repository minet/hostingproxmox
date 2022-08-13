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
    private errorcode;
    private discoveryDocument$: Promise<boolean>;

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

    check_cotisation(): void {
        this.http.get(this.authService.SERVER_URL + '/cotisation', {observe: 'response'}).subscribe(rep => {
                this.user.cotisation = rep.body['uptodate'];
            },
            error => {
                this.errorcode = error.status;
            });
    }

    // A function which return the http error message for a given http error code
    getHttpErrorMessage(httpErroCode): string {
        let errorMessages = {"100": "Continue","101": "Switching Protocols","200": "OK","201": "Created","202": "Accepted","203": "Non-Authoritative Information","204": "No Content","205": "Reset Content","206": "Partial Content","300": "Multiple Choices","301": "Moved Permanently","302": "Found","303": "See Other","304": "Not Modified","305": "Use Proxy","307": "Temporary Redirect","400": "Bad Request","401": "Unauthorized","402": "Payment Required","403": "Forbidden","404": "Not Found","405": "Method Not Allowed","406": "Not Acceptable","407": "Proxy Authentication Required","408": "Request Timeout","409": "Conflict","410": "Gone","411": "Length Required","412": "Precondition Failed","413": "Request Entity Too Large","414": "Request-URI Too Long","415": "Unsupported Media Type","416": "Requested Range Not Satisfiable","417": "Expectation Failed","500": "Internal Server Error","501": "Not Implemented","502": "Bad Gateway","503": "Service Unavailable","504": "Gateway Timeout","505": "HTTP Version Not Supported"}
        return errorMessages[httpErroCode];
    }

    getUser(): Observable<User> {
        return fromPromise(this.discoveryDocument$.then((result) => {
            const user: any = this.oauthService.getIdentityClaims();
            if (user != null) {
                this.user.username = user.sub;
                this.user.sn = user.sn;
                this.user.name = user.given_name;
                this.user.admin = false;
                this.oauthService.loadUserProfile().then(r => {
                    if (!!r.attributes['memberOf']) {
                        if (r.attributes['memberOf'].indexOf(this.authService.adminDn) > -1) {
                            this.user.admin = true;
                        }
                    }
                    if(this.user.admin == false)
                        this.check_cotisation();
                    if(r.attributes['signedhosting'] === "false")
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
