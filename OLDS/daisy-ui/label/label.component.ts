
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-label',
  standalone: true,
  imports: [CommonModule],
  template: `
    <label [class]="classes">
      <ng-content></ng-content>
    </label>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class LabelComponent {
  @Input() floating = false;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = this.floating ? 'floating-label' : 'label';
    return [baseClasses, this.customClass].filter(Boolean).join(' ');
  }
}
