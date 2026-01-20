
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type ProgressColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'info'
  | 'success'
  | 'warning'
  | 'error';

@Component({
  selector: 'daisy-progress',
  standalone: true,
  imports: [CommonModule],
  template: `
    <progress
      class="progress"
      [class]="classes"
      [value]="value"
      [max]="max"
    ></progress>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ProgressComponent {
  @Input() value: number | null = null;
  @Input() max = 100;
  @Input() color: ProgressColor | null = null;
  @Input() customClass = '';

  get classes(): string {
    const colorClass = this.color ? `progress-${this.color}` : '';
    return [colorClass, this.customClass].filter(Boolean).join(' ');
  }
}
