import { Component, Input } from '@angular/core';
import { Vm } from '../models/vm';
import { User } from '../models/user';

@Component({
  selector: 'app-vm-box',
  templateUrl: './vm-box.component.html',
  styleUrls: ['./vm-box.component.css']
})
export class VmBoxComponent {
  @Input() vm!: Vm;
  @Input() user!: User;


  /**
   * Convert seconds to days, hours, minutes and seconds
   * @param seconds
   * @returns string
   * @example 90061 => 1d 1h 1min 1s
  */
  secondsToDhms(seconds: number): string {
    seconds = Number(seconds);
    const d = Math.floor(seconds / (3600 * 24));
    const h = Math.floor(seconds % (3600 * 24) / 3600);
    const m = Math.floor(seconds % 3600 / 60);
    const s = Math.floor(seconds % 60);

    const dDisplay = d > 0 ? d + 'd ' : '';
    const hDisplay = h > 0 ? h + 'h ' : '';
    const mDisplay = m > 0 ? m + 'min ' : '';
    const sDisplay = s > 0 ? s + 's ' : '';
    return dDisplay + hDisplay + mDisplay + sDisplay;
}

}
