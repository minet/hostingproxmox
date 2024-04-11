import { ComponentFixture, TestBed } from '@angular/core/testing';

import { DeletevmComponent } from './deletevm.component';

describe('DeletevmComponent', () => {
  let component: DeletevmComponent;
  let fixture: ComponentFixture<DeletevmComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ DeletevmComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(DeletevmComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
