
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-countdown',
  standalone: true,
  imports: [CommonModule],
  template: `
    <span class="countdown" [class]="customClass">
      <span
        [style.--value]="value"
        [style.--digits]="digits"
        aria-live="polite"
        [attr.aria-label]="value"
      ></span>
    </span>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CountdownComponent {
  @Input() value!: number;
  @Input() digits: 1 | 2 | 3 | null = null;
  @Input() customClass = '';
}
