import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SshComponent } from './ssh.component';

describe('SshComponent', () => {
  let component: SshComponent;
  let fixture: ComponentFixture<SshComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SshComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SshComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
