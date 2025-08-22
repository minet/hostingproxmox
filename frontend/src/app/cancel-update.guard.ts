import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot } from '@angular/router';
import { VmsService } from './common/services/vms.service';

@Injectable({
  providedIn: 'root'
})
export class CancelUpdateGuard  {

  constructor(private vmsService: VmsService) {}

  canActivate(route: ActivatedRouteSnapshot): boolean {
    const url = route.url.join('/');
    if (url === 'dns' || url.startsWith('vms/') || url === 'history') {
      this.vmsService.cancelUpdateVms();
    }
    return true;
  }
}