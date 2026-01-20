
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type IndicatorHorizontal = 'start' | 'center' | 'end';
export type IndicatorVertical = 'top' | 'middle' | 'bottom';

@Component({
  selector: 'daisy-indicator',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="indicator" [class]="customClass">
      <span [class]="indicatorItemClasses">
        <ng-content select="[indicator-item]"></ng-content>
      </span>
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class IndicatorComponent {
  @Input() horizontal: IndicatorHorizontal | null = null;
  @Input() vertical: IndicatorVertical | null = null;
  @Input() customClass = '';
  @Input() indicatorItemCustomClass = '';

  get indicatorItemClasses(): string {
    const baseClasses = 'indicator-item';
    const horizontalClass = this.horizontal ? `indicator-${this.horizontal}` : '';
    const verticalClass = this.vertical ? `indicator-${this.vertical}` : '';

    return [baseClasses, horizontalClass, verticalClass, this.indicatorItemCustomClass]
      .filter(Boolean)
      .join(' ');
  }
}
