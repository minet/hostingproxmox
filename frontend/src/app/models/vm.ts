export class Vm {
  constructor(
    public user?: string,
    public name?: string,
    public ram?: string,
    public disk?: string,
    public cpu?: string,
    public ssh?: string,
    public type?: string,
    public status?: string,
    public autoreboot?: string,
    public id?: string,
    public password?: string,
    public sshKey?: string,
    public ip?: string,
    public ramUsage?: string,
    public cpuUsage?: string,
    public uptime?: string,
    public createdOn?: string,

  ) { }

}
