import { TestBed } from '@angular/core/testing';

import { DnsService } from './dns.service';

describe('DnsService', () => {
  let service: DnsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DnsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
