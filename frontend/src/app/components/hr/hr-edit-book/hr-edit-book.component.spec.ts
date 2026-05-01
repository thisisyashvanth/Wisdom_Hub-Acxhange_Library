import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HrEditBookComponent } from './hr-edit-book.component';

describe('HrEditBookComponent', () => {
  let component: HrEditBookComponent;
  let fixture: ComponentFixture<HrEditBookComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [HrEditBookComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(HrEditBookComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
