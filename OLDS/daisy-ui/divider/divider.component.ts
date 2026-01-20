
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type DividerDirection = 'horizontal' | 'vertical';
export type DividerColor =
  | 'neutral'
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'success'
  | 'warning'
  | 'info'
  | 'error';
export type DividerPlacement = 'start' | 'end';

@Component({
  selector: 'daisy-divider',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="classes">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DividerComponent {
  @Input() direction: DividerDirection | null = null;
  @Input() color: DividerColor | null = null;
  @Input() placement: DividerPlacement | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'divider';
    const directionClass = this.direction ? `divider-${this.direction}` : '';
    const colorClass = this.color ? `divider-${this.color}` : '';
    const placementClass = this.placement ? `divider-${this.placement}` : '';

    return [
      baseClasses,
      directionClass,
      colorClass,
      placementClass,
      this.customClass,
    ]
      .filter(Boolean)
      .join(' ');
  }
}
