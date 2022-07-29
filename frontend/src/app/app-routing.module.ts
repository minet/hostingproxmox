import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {HomeComponent} from './home/home.component';
import {VmsComponent} from './vms/vms.component';
import {VmComponent} from './vm/vm.component';
import {DnsComponent} from './dns/dns.component';
import {RulesComponent} from './rules/rules.component';
import {LegalComponent} from './legal/legal.component';
import {ManualComponent} from './manual/manual.component';
import {HistoryComponent} from './history/history.component';


const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: ':lang/vms', component: VmsComponent},
  {path: ':lang/vms/:vmid', component: VmComponent},
  {path: ':lang/dns', component: DnsComponent},
  {path: ':lang/rules', component: RulesComponent},
  {path: ':lang/legal', component: LegalComponent},
  {path: ':lang/manual', component: ManualComponent},
  {path: ':lang/history', component: HistoryComponent},
  {path: '**', redirectTo: ''},
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {relativeLinkResolution: 'legacy'})],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
