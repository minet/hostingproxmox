import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {OAuthModule, OAuthStorage} from 'angular-oauth2-oidc';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HomeComponent } from './home/home.component';
import { NavbarComponent } from './navbar/navbar.component';
import { FooterComponent } from './footer/footer.component';
import { AuthService } from './common/services/auth.service';
import { UserService } from './common/services/user.service';
import { FormsModule } from '@angular/forms';
import { User } from './models/user';
import { SlugifyPipe } from './pipes/slugify.pipe';
import { VmsComponent } from './vms/vms.component';
import { VmComponent } from './vm/vm.component';
import { DnsComponent } from './dns/dns.component';
import { SshComponent } from './ssh/ssh.component';
import { LegalComponent } from './legal/legal.component';
import { ManualComponent } from './manual/manual.component';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { HistoryComponent } from './history/history.component';
import {Ng2SearchPipeModule} from "ng2-search-filter";
import { environment } from './../environments/environment';
import {HttpClient, HttpClientModule} from '@angular/common/http';
import {TranslateModule, TranslateLoader} from '@ngx-translate/core';
import {TranslateHttpLoader} from '@ngx-translate/http-loader';
import { UserComponent } from './user/user.component';

export function storageFactory() : OAuthStorage {
  return localStorage;
}

export function HttpLoaderFactory(http: HttpClient): TranslateHttpLoader {
  return new TranslateHttpLoader(http);
}

@NgModule({
  declarations: [
    AppComponent,
    HomeComponent,
    NavbarComponent,
    FooterComponent,
    SlugifyPipe,
    VmsComponent,
    VmComponent,
    DnsComponent,
    SshComponent,
    LegalComponent,
    ManualComponent,
    HistoryComponent,
    UserComponent,
  ],
  imports: [
    BrowserModule,
    NgbModule,
    AppRoutingModule,
    HttpClientModule,
    Ng2SearchPipeModule,
    OAuthModule.forRoot({
      resourceServer: {
        allowedUrls: [environment.backendURL],
        sendAccessToken: true
      }
    }),
    FormsModule,
    NgbModule,
    TranslateModule.forRoot({
      defaultLanguage: 'en',
      loader: {
        provide: TranslateLoader,
        useFactory: HttpLoaderFactory,
        deps: [HttpClient]
      }
    }),
  ],
  providers: [AuthService, UserService, User, SlugifyPipe, { provide: OAuthStorage, useFactory: storageFactory }],
  bootstrap: [AppComponent]
})
export class AppModule {

}
