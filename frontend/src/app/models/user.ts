import {Vm} from './vm';
import {Dns} from './dns';

export class User {
    public sn: string;
    public firstname: string;
    public username: string;
    public lastname: string;
    public name: string;
    public admin: boolean;
    public vms?: Array<Vm>;
    public dns?: Array<Dns>;
}
