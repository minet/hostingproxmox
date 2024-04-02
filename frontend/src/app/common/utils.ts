import {Injectable} from '@angular/core';
import {TranslateService} from "@ngx-translate/core";
import {CookieService} from "ngx-cookie-service";
import {ActivatedRoute} from '@angular/router';


@Injectable({
    providedIn: 'root'
  })

export class Utils{
    constructor(public translate: TranslateService,
                private cookie: CookieService, 
                private route: ActivatedRoute,
                ) {
        this.cookie.get('lang') == 'en' ? this.translate.use('en') && this.cookie.set('lang','en') : this.translate.use('fr') && this.cookie.set('lang','fr');
    }


    // A function which return the http error message for a given http error code
    getHttpErrorMessage(httpErroCode): string {
        const errorMessages = {"100": "Continue","101": "Switching Protocols","200": "OK","201": "Created","202": "Accepted","203": "Non-Authoritative Information","204": "No Content","205": "Reset Content","206": "Partial Content","300": "Multiple Choices","301": "Moved Permanently","302": "Found","303": "See Other","304": "Not Modified","305": "Use Proxy","307": "Temporary Redirect","400": "Bad Request","401": "Unauthorized","402": "Payment Required","403": "Forbidden","404": "Not Found","405": "Method Not Allowed","406": "Not Acceptable","407": "Proxy Authentication Required","408": "Request Timeout","409": "Conflict","410": "Gone","411": "Length Required","412": "Precondition Failed","413": "Request Entity Too Large","414": "Request-URI Too Long","415": "Unsupported Media Type","416": "Requested Range Not Satisfiable","417": "Expectation Failed","500": "Internal Server Error","501": "Not Implemented","502": "Bad Gateway","503": "Service Unavailable","504": "Gateway Timeout","505": "HTTP Version Not Supported"}
        return errorMessages[httpErroCode];
    }

    getTranslation(str: string) {
        let translation = str;
        this.translate.get(str).subscribe (x=> 
             translation =x);
        console.log(translation);
        return translation;
      }
    


}
