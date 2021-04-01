import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {HomeComponent} from './home/home.component';
import {VmsComponent} from './vms/vms.component';
import {VmComponent} from './vm/vm.component';
import {DnsComponent} from './dns/dns.component';
import {RulesComponent} from './rules/rules.component';
import {LegalComponent} from './legal/legal.component';
import {ManualComponent} from './manual/manual.component';


const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: 'vms', component: VmsComponent},
  {path: 'vms/:vmid', component: VmComponent},
  {path: 'dns', component: DnsComponent},
  {path: 'rules', component: RulesComponent},
  {path: 'legal', component: LegalComponent},
  {path: 'manual', component: ManualComponent},
  {path: '**', component: HomeComponent},


];

@NgModule({
  imports: [RouterModule.forRoot(routes, {relativeLinkResolution: 'legacy'})],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
