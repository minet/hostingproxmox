import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VmBoxComponent } from './vm-box.component';

describe('VmBoxComponent', () => {
  let component: VmBoxComponent;
  let fixture: ComponentFixture<VmBoxComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ VmBoxComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VmBoxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
