
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type BadgeColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'ghost'
  | 'info'
  | 'success'
  | 'warning'
  | 'error';
export type BadgeSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';
export type BadgeStyle = 'outline' | 'dash' | 'soft';

@Component({
  selector: 'daisy-badge',
  standalone: true,
  imports: [CommonModule],
  template: ` <span [class]="classes"><ng-content></ng-content></span> `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class BadgeComponent {
  @Input() color: BadgeColor | null = null;
  @Input() size: BadgeSize | null = null;
  @Input() style: BadgeStyle | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'badge';
    const colorClass = this.color ? `badge-${this.color}` : '';
    const sizeClass = this.size ? `badge-${this.size}` : '';
    const styleClass = this.style ? `badge-${this.style}` : '';

    return [baseClasses, colorClass, sizeClass, styleClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
