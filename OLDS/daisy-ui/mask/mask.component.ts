
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type MaskShape =
  | 'squircle'
  | 'heart'
  | 'hexagon'
  | 'hexagon-2'
  | 'decagon'
  | 'pentagon'
  | 'diamond'
  | 'square'
  | 'circle'
  | 'star'
  | 'star-2'
  | 'triangle'
  | 'triangle-2'
  | 'triangle-3'
  | 'triangle-4';

@Component({
  selector: 'daisy-mask',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="classes">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MaskComponent {
  @Input() shape: MaskShape | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'mask';
    const shapeClass = this.shape ? `mask-${this.shape}` : '';

    return [baseClasses, shapeClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
