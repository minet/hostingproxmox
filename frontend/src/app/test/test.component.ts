import { Component, OnInit } from '@angular/core';

@Component({
    selector: 'app-test',
    templateUrl: './test.component.html',
    styleUrls: ['./test.component.css'],
    standalone: false
})
export class TestComponent implements OnInit {

  maVariable: number;

  ngOnInit(): void {
    this.maVariable = 3;
  }

  increment() {
    this.maVariable++;
  }

}
