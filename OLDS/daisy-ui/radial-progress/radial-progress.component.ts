
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-radial-progress',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div
      class="radial-progress"
      [class]="customClass"
      [style.--value]="value"
      [style.--size]="size"
      [style.--thickness]="thickness"
      [attr.aria-valuenow]="value"
      role="progressbar"
    >
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class RadialProgressComponent {
  @Input() value!: number;
  @Input() size: string | null = null; // e.g., '12rem'
  @Input() thickness: string | null = null; // e.g., '2px', '2rem'
  @Input() customClass = '';
}
