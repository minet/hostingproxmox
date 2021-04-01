import {Vm} from './vm';
import {Dns} from './dns';

export class User {
    public firstname: string;
    public username: string;
    public lastname: string;
    public name: string;
    public vms?: Array<Vm>;
    public dns?: Array<Dns>;
}
