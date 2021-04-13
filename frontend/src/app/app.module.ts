import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
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
import { RulesComponent } from './rules/rules.component';
import { LegalComponent } from './legal/legal.component';
import { ManualComponent } from './manual/manual.component';

export function storageFactory() : OAuthStorage {
  return localStorage;
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
    RulesComponent,
    LegalComponent,
    ManualComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    OAuthModule.forRoot({
      resourceServer: {
        // allowedUrls: [ 'http://localhost:8080' ],
        allowedUrls: [ 'https://backprox.minet.net' ],
        sendAccessToken: true
      }
    }),
    FormsModule,

  ],
  providers: [AuthService, UserService, User, SlugifyPipe, { provide: OAuthStorage, useFactory: storageFactory }],
  bootstrap: [AppComponent]
})
export class AppModule {

  constructor() {
  }
}
