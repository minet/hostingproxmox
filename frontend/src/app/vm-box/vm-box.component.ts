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


  

}
