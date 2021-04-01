import { Vm } from './vm';

describe('Vm', () => {
  it('should create an instance', () => {
    expect(new Vm('', '', false, '', '', '')).toBeTruthy();
  });
});
