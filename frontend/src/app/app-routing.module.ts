import {NgModule} from '@angular/core';
import {Routes, RouterModule} from '@angular/router';
import {HomeComponent} from './home/home.component';
import {VmsComponent} from './vms/vms.component';
import {VmComponent} from './vm/vm.component';
import {DnsComponent} from './dns/dns.component';
import {LegalComponent} from './legal/legal.component';
import {ManualComponent} from './manual/manual.component';
import {HistoryComponent} from './history/history.component';
import {DeletevmComponent} from './deletevm/deletevm.component';
import { CancelUpdateGuard } from './cancel-update.guard';


const routes: Routes = [
  {path: '', component: HomeComponent},
  {path: 'vms', component: VmsComponent},
  {path: 'vms/:vmid', component: VmComponent, canActivate: [CancelUpdateGuard]},
  {path: 'dns', component: DnsComponent, canActivate: [CancelUpdateGuard]},
  {path: 'legal', component: LegalComponent},
  {path: 'manual', component: ManualComponent},
  {path: 'history', component: HistoryComponent, canActivate: [CancelUpdateGuard]},
  {path: 'deletevm', component: DeletevmComponent},
  {path: '**', redirectTo: ''},
];


@NgModule({
  imports: [RouterModule.forRoot(routes, {relativeLinkResolution: 'legacy'})],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
