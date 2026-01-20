
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-fieldset',
  standalone: true,
  imports: [CommonModule],
  template: `
    <fieldset class="fieldset" [class]="customClass">
      @if (legend) {
      <legend class="fieldset-legend">{{ legend }}</legend>
      }
      <ng-content></ng-content>
    </fieldset>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FieldsetComponent {
  @Input() legend: string | null = null;
  @Input() customClass = '';
}
