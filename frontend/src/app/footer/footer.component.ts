import { Component} from '@angular/core';
import {CookieService} from "ngx-cookie-service";


@Component({
  selector: 'app-footer',
  templateUrl: './footer.component.html',
  styleUrls: ['./footer.component.css']
})
export class FooterComponent  {
  date: Date = new Date();

  constructor(
      public cookie: CookieService
  ) {

  }


}
