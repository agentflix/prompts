
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type AlertColor = 'info' | 'success' | 'warning' | 'error';
export type AlertStyle = 'outline' | 'dash' | 'soft';
export type AlertDirection = 'vertical' | 'horizontal';

@Component({
  selector: 'daisy-alert',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div role="alert" [class]="classes">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlertComponent {
  @Input() color: AlertColor | null = null;
  @Input() style: AlertStyle | null = null;
  @Input() direction: AlertDirection | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'alert w-full';
    const colorClass = this.color ? `alert-${this.color}` : '';
    const styleClass = this.style ? `alert-${this.style}` : '';
    const directionClass = this.direction ? `alert-${this.direction}` : '';

    return [baseClasses, colorClass, styleClass, directionClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
