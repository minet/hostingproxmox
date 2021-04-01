import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DnsComponent } from './dns.component';

describe('DnsComponent', () => {
  let component: DnsComponent;
  let fixture: ComponentFixture<DnsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DnsComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(DnsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
