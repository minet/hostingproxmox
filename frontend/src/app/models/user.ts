import {Vm} from './vm';
import {Dns} from './dns';

export class User {
    public sn: string;
    public firstname: string;
    public username: string;
    public lastname: string;
    public name: string;
    public admin = false;
    public chartevalidated;
    public freezeState: number;
    public vms?: Array<Vm>;
    public dns?: Array<Dns>;
    public ips?: Array<string>;
<<<<<<< HEAD
    public usedCPU?: number;
    public usedRAM?: number;
    public usedStorage?: number;
=======
    public availableCPU?: number;
    public availableRAM?: number;
    public availableStorage?: number;
>>>>>>> 6ce4559583000eb68296cd70627ddccba4d39258
}
