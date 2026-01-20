
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <ul class="list" [class]="customClass">
      <ng-content></ng-content>
    </ul>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListComponent {
  @Input() customClass = '';
}

@Component({
  selector: 'li[daisy-list-row]',
  standalone: true,
  imports: [CommonModule],
  template: ` <ng-content></ng-content> `,
  host: {
    class: 'list-row',
  },
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ListRowComponent {}
